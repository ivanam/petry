""" Este modulo contiene la clase Simulacion."""
import pyglet
import os, signal
from viamultiple import *
from generadortrafico import *
from utilidades.decodificadorJson import *
import logging
from semaforos import *
from utilidades.graficador import *
from easygui import *

class Simulacion(pyglet.event.EventDispatcher):
	""" Esta clase se emplea para iniciar el resto de los componentes de la simulacion.
		Mantiene referencias a la red de semaforos, las viasMultiples y la Vista, como asi tambien
		tiene un atributo para determinar si esta continua en ejecucion o si finalizado.
		La clase Simulacion tambien se encarga de unir a las redes de Petri de las vias multiples entre si 
		y con la red de Petri de los Semaforos. """
	def __init__(self,diccRP,diccRedSemaforos,ordenTransicionesSemaforos,cantCiclos,nombreEscenario,LUGARES_A_INICIALIZAR):
		""" Metodo constructor de la clase Simulacion.
			@param diccRP: Conjunto de valores que describen la estructura de la red de Petri de las
			vias multiples
			@type diccRP: Diccionario
			@param diccRedSemaforos: Estructura de la red de Petri de la red de semaforos
			@type diccRedSemaforos: Diccionario
			@param ordenTransicionesSemaforos: Diccionario que tiene como clave el orden de la transicion a disparar, y como valor
			el nombre de la transicion. 
			ordenTransicionesSemaforos={
					1:"t22",
				...
			}
			@type ordenTransicionesSemaforos: Diccionario
			@param cantCiclos: Cantidad maxima de ciclos a simular (ingresado por el usuario)
			@type cantCiclos: Integer
			@param nombreEscenario: Nombre del escenario que se simulara
			@type nombreEscenario: String
			@param LUGARES_A_INICIALIZAR: Diccionario con los nombres de los lugares que se deben incializar
			@type LUGARES_A_INICIALIZAR: Diccionario """
		super(Simulacion,self).__init__()
		self.cantidadCiclos=cantCiclos
		#Atributos para la sincronizacion entre Threads-->
		
		#Se utiliza esta variable desde los objetos viaMultiple, para saber cuando
		# detener el ingreso de vehiculos a las viasMulitples y la temporizacion en la RP
		#  de cada ViaMuliple. Este atributo se utiliza desde el metodo "terminoSimulacion()".
		self.finalizoSimulacion=False
		#La simulacion mantiene una lista con los theads GeneradoresTrafico,
		# que permitiran iniciar cada thread cuando la via se inicie.
		self.generadoresTrafico=[]
		# La simulacion mantiene un diccionario con el nombre y los objetos viasMultiples.
		# Cada ViaMultiple, mantiene a su vez una referencia a la simulacion, para saber cuando
		# terminar y dejar de ingresar trafico.
		self.viasMultiples={}
		#Se recorren el diccionario con la definicion de las RP de la simulacion.
		for nombreVia,tupla in diccRP.iteritems():
			logging.debug("La via %s tiene el siguiente esquema leido desde el disco: %s" % (nombreVia,tupla["esquema"]))
			logging.debug("")

			vm=ViaMultiple(nombreVia,tupla["delayVehiculos"],tupla["esquema"],tupla["viasCircHabilitadas"],
				tupla["nodosInicio"],tupla["nodosFin"],
				tupla["traficoPredefinido"],tupla["cantCarriles"],tupla["cantTransicionesLink"],
				tupla["fasesARegistrar"],
				tupla["nombreSemaforoControlador"],self)
			if tupla["datosLinkAContabilizar"].has_key("transicionesSalidaLink"):
				vm.setTransicionesSalidaLink(tupla["datosLinkAContabilizar"]["transicionesSalidaLink"])
			self.viasMultiples[nombreVia]=vm
			vm.setSimulacion(self)
			# Se establece un GeneradorTrafico para cada viaMultiple. Cada GeneradorTrafico tiene la referencia
			#  a la ViaMultiple y la Simulacion, de manera que el generador sepa cuando la simulacion finalizo.
			genTraf=GeneradorTrafico(self,vm)
			# Se mantiene desde la simulacion una referencia a los obj. GeneradorTrafico.
			self.generadoresTrafico.append(genTraf)
			vm.setGeneradorTrafico(genTraf)
		#Luego de construir las ViasMultiples se completan los lugares que necesita una viaMultiple
		# que estan en otra via (agregando tambien transiciones).
		self._completarVias()
		# Se establecen las Alternativas Ordenadas (arreglo con los nombres de las transiciones de cada ViaMultiple)
		# a cada ViaMultiple.
		for nombVia,viaMult in self.viasMultiples.iteritems():
			alternativas=diccRP[nombVia]["alternativasDisparo"]
			viaMult.generarAltOrdenadas(alternativas)

		#Se mantiene la referencia desde la Simulacion al objeto RedDeSemarofos, con la RP que de los semaforos.
		self.redSemaforos=RedDeSemaforos(self,diccRedSemaforos,ordenTransicionesSemaforos,cantCiclos)

		# Se agregan los generadoresTrafico para que la reddeSemaforos sepa como notificar acerca del cambio de ciclo.
		# NOTA: Cuando se agrega un generador a la RedDeSemaforos, se conecta (con self.dispatcher) con manejador 
		# del evento de generadorTrafico.
		for generador in self.generadoresTrafico:
			self.redSemaforos.agregarGenerador(generador)
		for gen in self.generadoresTrafico:
			if gen.getViaMultiple().getNombre()=="viaX":
				sem1=self.redSemaforos.getSemaforo("semaforoLink1")
				sem1.setGenerador(gen)
				sem1.registrarGenerador()
			elif gen.getViaMultiple().getNombre()=="viaYDesc":
				sem1=self.redSemaforos.getSemaforo("semaforoLink6")
				sem1.setGenerador(gen)
				sem1.registrarGenerador()
			elif gen.getViaMultiple().getNombre()=="viaYAsc":
				sem1=self.redSemaforos.getSemaforo("semaforoLink3")
				sem1.setGenerador(gen)
				sem1.registrarGenerador()

		# Una vez armadas la RP de las viasMultipes y la RP de los semaforos,
		# se crea un diccionario que mantiene la informacion respecto de la union de la RP de la ViaMultiple
		# con la RP del semaforo. La union se debe hacer agregando a la ViaMultiple las transiciones y los lugares
		# que correspondan del Semaforo.
		# Esta union debe hacerse porque los tokens que circulan por la ViaMultiple deben retenerse
		# segun los tokens que haya en el semaforo y el estado en el que este se encuentre.
		# La estructura del diccionario es la siguiente:
		#
		######################################################################################################################################
		#################### Se especifican los nombres de los lugares compartidos, que se deben agregar en la RP ###########################
		#################### de las vias de circulacion y que regularan el disparo de 							   ###########################
		####################  ciertas transiciones (por ej. t1 y t1' en el modelo teorico).						   ###########################
		#####################################################################################################################################
		# Los "lugaresCompartidos" tienen los sig. atributos:
		#								 - El "nombre" del lugar en la RP de los semaforos.
		#								 - La "viaDestino" que es el nombre de la via de circulacion en la que se buscara la "transicionDestino".
		#								 - Un arreglo de "transicionesAfectadas", que son los nombres de las  transiciones 
		# a las que se deben agregar un arco de entrada y salida hacia el "lugarCompartido". Estos nombres de transicion son unicos y se agregan solamente
		# en la RP de la red de semaforos.
		diccUnionesRPConSemaforos=cargarJson("LugaresCompartidosViasMultiples.json","modelo/json/simulacion")
		#Se realiza la union de las 2 RP (Semaforos + ViasMultiples) en los lugares compartidos que corresponda.
		redesPetriUnidas=self.unirRedesPetri(diccUnionesRPConSemaforos,self.redSemaforos.getRedPetri())
		#Se actualizan todas las ViasMultiples con la nueva estructura.
		for nombre,red in redesPetriUnidas.iteritems():
			self.viasMultiples[nombre].setRedPetri(red)

		#La coleccion de threads de las viasMultiples.
		#NOTA: Esta coleccion se usa para que el thread de la simulacion espere a que los threads
		# de las viasMultiples finalicen para comenzar a leer la informacion en las RP.
		self.threads=[]

		# Este metodo se utiliza para inicializar las vias; Recibe el nombre del escenario del paper
		# que va a representar y un diccionario con los lugares a inicializar para ese escenario.
		# self._inicializarViasMultiples("escenario1",LUGARES_A_INICIALIZAR)
		self._inicializarViasMultiples(nombreEscenario,LUGARES_A_INICIALIZAR)
		#Se asocia el semaforo con su viaMutiple de pertenencia.
		for nombreVia,via in self.viasMultiples.iteritems():
			if nombreVia=="viaX":
				via.setSemaforo(self.redSemaforos.getSemaforo("semaforoLink1"))
			elif nombreVia=="viaYDesc":
				via.setSemaforo(self.redSemaforos.getSemaforo("semaforoLink6"))
			elif nombreVia=="viaYAsc":
				via.setSemaforo(self.redSemaforos.getSemaforo("semaforoLink3"))

		logging.debug("Semaforos inicializados correctamente!")
		logging.debug("")
		self.todoListo=False
		self.reloj=None

	def getCantidadCiclos(self):
		""" Metodo getter para el atributo 'cantidadCiclos'
			@return: Cantidad de ciclos maxima a temporizar
			@rtype: Integer """
		return self.cantidadCiclos

	# Simulacion.setReloj()	
	def setReloj(self,r):
		""" Metodo setter para el atributo 'reloj'
			@param r: Reloj que opera paralelamente a la simulacion
			@rtype: Reloj """
		self.reloj=r

	def estaTodoListo(self):
		""" Este metodo indica si todas las configuraciones ya fueron realizadas por la 
			simulacion.
			@return: Flag indicando la finalizacion de las configuraciones previas
			@rtype: Boolean"""
		return self.todoListo

	def setTodoListo(self,valor):
		""" Metodo setter para el atributo 'todoListo'
			@param valor: Valor indicando el estado de la simulacion
			@type valor: Reloj """
		self.todoListo=valor

	def _inicializarViasMultiples(self,nombreEscenario,diccValores):
		""" Este metodo agrega tokens en el inicio de determinados lugares (que se suponen incializados para un escenario 
			de la simulacion dado) antes que la simulacion comience.
			@param nombreEscenario:Nombre del escenario que se simulara
			@type nombreEscenario: String
			@param diccValores: Coleccion de lugares que se deben inicializar
			@type diccValores: Diccionario """

		logging.debug("Diccionario de valores: %s" % diccValores)
		logging.debug("")
		logging.debug("nombreEscenario : %s" % nombreEscenario)
		logging.debug("")
		elementos=diccValores[nombreEscenario]
		for nombreVia,tupla in elementos.iteritems():
			# Se cuentan los vehiculos iniciales de cada via para inicializar el primer ciclo.
			cantVehiculosEnVia=0
			if len(tupla["colLugares"])>0:
				for nombreLug in tupla["colLugares"]:
					self.viasMultiples[nombreVia].agregarToken(nombreLug,tupla["imagenVehiculos"])
					cantVehiculosEnVia+=1
			# Se inicializa el primer ciclo de la viaMultiple.
			self.viasMultiples[nombreVia].actualizarDicEstadisticas(1,cantVehiculosEnVia)

	#Simulacion.obtenerRP(nombreViaMultiple)
	def obtenerRP(self,nombreVia):
		""" Este metodo retorna la RP de una viaMultiple segun su nombre. 
			@param nombreVia: Nombre de la via multiple a retornar
			@type nombreVia: String
			@return: Red de Petri para el nombre de via dado
			@rtype: PetriNet """
		return self.viasMultiples[nombreVia].getRedPetri()

	#Simulacion._completarVias()
	def _completarVias(self):
		"""	Este metodo completa todas las vias de circulacion con los lugares que son parte de 
			otra via y crea las transiciones que hagan falta hacia dichos lugares. """
		#Se completa primero la ViaMultiple: viaX
		#NOTA: Se considera que las vias que tienen "Lugares compartidos" con OTRAS VIAS, 
		# deben tener el atributo "enViaCirculacion" establecido en False, ya  que
		# dicho lugar no esta en la ruta de circulacion de la ViaMultiple. Esto evita que el metodo
		# "marcarRP()" marque dos veces el mismo lugar en la RP.

		# Lugares que se completan de la via X con respecto a las demas vias multiples:
		#	-Se agrega la transicion de cambio de rumbo desde p14 hacia p30 (GIRO A LA DERECHA)
		#	-Se agrega la transicion de cambio de rumbo desde p15 hacia p30 (GIRO A LA DERECHA)
		dicViaX=cargarJson("LugaresDependientesViaX.json","modelo/json/simulacion")
		self._agregarElemRP(self.viasMultiples["viaX"],self.viasMultiples["viaYDesc"],dicViaX)
		
		#Se completa primero la ViaMultiple: viaYDesc. Los lugares que se agregan de esta via
		# son los siguientes:
		#  ###################### Lugares y transiciones necesarios para el avance RECTO hacia LINK 2. ######################
		# 	-Se agrega la transicion de cambio de rumbo desde p13  hacia p14 (CRUCE DE LA INTERSECCION)
		#	-Se agrega la transicion de cambio de rumbo desde p23  hacia p24 (CRUCE DE LA INTERSECCION)
		# NOTA: Las transiciones que cruzan el carril tienen llegan al mismo lugar
		# por lo que se les agrega una letra para distinguirlas.
		#	-Se agrega la transicion de cambio de rumbo desde  p14 hasta p15
		#	-Se agrega la transicion de cambio de rumbo desde  p24 hasta p25
		# 	-Se agrega la transicion de cambio de rumbo desde  p25 hasta p30 desde carril 1
		# 	-Se agrega la transicion de cambio de rumbo desde  p25 hasta p30 desde carril 2
		#
		######################## Lugares y transiciones necesarios para el giro hacia la derecha en ambos carriles ##########
		# NOTA IMPORTANTE: Las transiciones relacionadas con los GIROS A LA DERECHA siguen la misma nomenclatura que las transiciones
		# comunes. Y para diferenciarlas se les agrega una letra comenzando por la "A".
		# 	-Lugares p16,p26,p17.L4,p27.L4
		# 	-Se agrega la transicion de cambio de rumbo desde p16 a p17.L4
		# 	-Se agrega la transicion de cambio de rumbo desde p26 a p27.L4
		dicViaYDesc=cargarJson("LugaresDependientesViaYDesc.json","modelo/json/simulacion")
		self._agregarElemRP(self.viasMultiples["viaYDesc"],self.viasMultiples["viaX"],dicViaYDesc)
		# Se completa la ViaMultiple: viaYAsc
		# Los lugares y transiciones que se agregan que pertenecen a la via multiple son los siguientes:
		# 	-Lugares p16,p26
		# 	-Se agrega la transicion que ingresa a la interseccion: p13 a p26
		# 	-Se agrega la transicion de cambio de rumbo desde p26 a p16
		# 	-Se agrega la transicion que sale  de la interseccion: p16 a p32
		#NOTA: Se considera que las vias que tienen "Lugares compartidos" con OTRAS VIAS, 
		# deben tener el atributo "enViaCirculacion" establecido en False, ya  que
		# dicho lugar no esta en la ruta de circulacion de la ViaMultiple. Esto evita que el metodo
		# "marcarRP()" marque dos veces el mismo lugar en la RP.
		dicViaYAsc=cargarJson("LugaresDependientesViaYAsc.json","modelo/json/simulacion")
		self._agregarElemRP(self.viasMultiples["viaYAsc"],self.viasMultiples["viaX"],dicViaYAsc)

	# Simulacion._agregarElemRP()
	def _agregarElemRP(self,viaModificable,viaLectura,diccModificaciones):
		""" Este metodo completa la RP de una via en base a un diccionario con elementos (lugares y transicions) de otra
			RP. Al finalizar actualiza la RP de la "viaModificable".
			El diccModificaciones tiene la sig. estructura:
			diccMod=[ 
		 		{ "tipo": "lugar","nombre":"p31"}, --> En este caso se pasa el nombre del recurso que se tiene que agregar en la
				"rpModificable".
		
		 		{ "tipo":"transicionNueva", "nombre":"t31",  "esTransicionCruzada": False, "input_places": [{"nombrelugar" : 'p25', "nombreVariable":"vehiculo"}] ,
					 "output_places": [{ "nombrelugar": 'p31', "nombreVariable": "vehiculo"}] }						 			
			--> En el caso de las transiciones se pasan las transiciones que involucran a los lugares agregados y que se tienen
			que agregar en la RP actual.
	 		...
				{ "tipo": "transicionExistente","nombre":"t31"} --> Si existe la transicion se la agrega en la RPModificable
			]

			@param viaModificable:
			@type viaModificable:
			@param viaLectura:
			@type viaLectura:
			@param diccModificaciones:
			@type diccModificaciones:  """
		rpModificable=viaModificable.getRedPetri()
		rpLectura=viaLectura.getRedPetri()
		for tupla in diccModificaciones:
			if tupla["tipo"]=="lugar":
				lug=rpLectura.place(tupla["nombre"])
				rpModificable.add_place(lug)
			elif tupla["tipo"]=="transicionNueva":
				rpModificable.add_transition(Transition(tupla["nombre"]))
				#Se agregan los arcos de entrada/salida desde/hacia el lugar nuevo agregado
				for elem in tupla["input_places"]:
					rpModificable.add_input(elem["nombrelugar"], tupla["nombre"] , Variable(elem["nombreVariable"]))
				for elem in tupla["output_places"]:
					rpModificable.add_output(elem["nombrelugar"], tupla["nombre"] , Variable(elem["nombreVariable"]))
			elif tupla["tipo"]=="transicionExistente":
				rpModificable.add_transition(Transition(tupla["nombre"]) )
		#Se solicita a la ViaMultiple que se actulice con el nuevo valor
		viaModificable.setRedPetri(rpModificable)

	def unirRedesPetri(self,diccUnionesRP,redPetriSemaforos):
		"""	Este metodo agrega los lugares de la RP de los semaforos a la RP de la ViaMultiple. Luego, crea los arcos de 
			entrada/salida desde el lugar compartido agregado hacia la "transicionAfectada". Esto se hace para produccion
			y devolucion de los tokens especiales usados por el semaforo. 
			Este metodo retorna un diccionario de redesDePetri de ViaMultiple indexadas por su nombre. 
			@param diccUnionesRP: Coleccion de valores que se uniran
			@type diccUnionesRP: Diccionario
			@param redPetriSemaforos: Red de Petri de los semaforos
			@type diccUnionesRP: PetriNet """
		redesPetriUnidas={}
		for elem in diccUnionesRP:
			lugComp=redPetriSemaforos.place(elem["nombre"])
			redPetriVia=self.viasMultiples[elem["viaDeDestino"]].getRedPetri()
			#Se agrega el  lugarCompartido de la RP de las vias de circulacion a la RP de la red de semaforos
			redPetriVia.add_place(lugComp)
			#Se crea un arco de entrada y de salida desde y hacia el lugarCompartido
			for nombt in elem["transicionesAfectadas"]:
				redPetriVia.add_input(elem["nombre"], nombt , Value(91))
				redPetriVia.add_output(elem["nombre"], nombt , Value(91))

			#Se agrega la RP de la via que corresponda al diccionario de RP actualizadas,
			#indexandolas por medio del atributo "viaDestino"
			redesPetriUnidas[ elem["viaDeDestino"] ]=redPetriVia
		return redesPetriUnidas

	#simulacion.getRedDeSemaforos()
	def getRedSemaforos(self):
		""" Metodo getter para el atributo 'redSemaforos'
			@return: Red de semaforos de la simulacion
			@rtype: PetriNet """
		return self.redSemaforos

	
	def iniciarSemarofos(self):
		""" Este metodo inicia desde la simulacion el thread que corresponde a la temporizacion de la red
			de semaforos."""
		self.redSemaforos.daemon=True
		self.redSemaforos.start()
		logging.debug ("Temporizacion de RedSemarofos iniciada!")
		logging.debug ("")

	# Simulacion.comenzar()
	def comenzar(self):
		""" Se inicializan los threads de todas las vias multiples y el thread de red de semaforos. """
		#Se ejecuta un bucle de movimiento de los vehiculos mientras la simulacion este
		#en ejecucion. Cuando finalice se detiene el movimiento de los vehiculos.
		#NOTA: -La frecuencia con la que se dispara la RP de movimiento de trafico
		# es cada 1 seg. ya que los intervalos van desde los 3 seg. hasta los 10 o 15 seg. 
		# en las pruebas.
		i=0
		logging.debug ("Threads de GeneradorTrafico y RedDeSemaforos iniciados correctamente!! ")
		logging.debug ("")
		logging.debug ("Despues del for de viasMultiples!! ")		
		logging.debug ("")
		for clave,via in self.viasMultiples.iteritems():
			via.setDaemon(True)
			via.start()
			#Esto se usa para unir el thread de finalizacion de semaforos hasta
			# que termine la temporizacion de las viasMultiples.
			self.threads.append(via)
			logging.debug("viaMultiple "+str(clave)+" iniciada correctamente!")
			logging.debug("")
		self.iniciarSemarofos()
		logging.debug("RedDeSemaforos iniciada correctamente!")
		logging.debug("")
		# Se establece que esta todo listo para iniciar la simulacion.
		self.setTodoListo(True)
		logging.debug("TODO LISTO! Simulacion comenzando...")
		logging.debug("")

	def terminoSimulacion(self):
		""" Este metodo indica si la simulacion ya termino.
			@return: Valor que indica el estado de la simulacion
			@rtype: Boolean"""
		return self.finalizoSimulacion

	def detener(self):
		""" Este metodo detiene la simluacion, los hilos demonio asociados a la misma y se inicia el dibujado de las estadisticas. """
		#Se bloquea el thread  de la simulacion hasta que las viasMultiples terminen la temporizacion
		# y detecten que self.finalizoSimulacion es True.
		#Se finaliza el dibujado unicamente, cuando se hayan terminado de temporizar
		#todas las viasMultiples
		self.finalizoSimulacion=True
		logging.debug(" Terminando el calculo de estadisticas de las vias")
		logging.debug("")
		for t in self.threads:
			# Si existe alguna fase que no este temporizada, se llama al metodo de calculo
			# de estadisticas para que termine de temporizarlas.
			logging.debug("Via= %s ; fasesTemporizadas= %s" % (t.getNombre(),t.getFasesTemporizadas()) )
			logging.debug(t.getFasesTemporizadas())
			logging.debug("")
			todosCiclosEstanTemporizados=True
			ciclosTemporizados=t.getFasesTemporizadas()
			for nroCiclo,cicloTemporizado in ciclosTemporizados.iteritems():
				if not cicloTemporizado or t.getDicEstadisticas()[nroCiclo+1]==CANT_NO_CONTABILIZADA:
					todosCiclosEstanTemporizados=False
					break
			# Si alguno de los ciclos de alguna viaMultiple no esta temporizado, se calculan
			# las estadisticas para el final de la simulacion.
			if not todosCiclosEstanTemporizados:
				logging.debug("La via %s no termino de temporizar..." % t.getNombre())
				logging.debug("Terminando de calcular estadisticas...")
				logging.debug("")
				t.terminarCalculoDeEstadisticas()				
				logging.debug("Se termino calculo estadistico!! y la via %s termino de temporizar..." % t.getNombre())
				logging.debug("")
			else:
				logging.debug("La via %s termino de temporizar..." % t.getNombre())
				logging.debug("")

		estadisticasFinales={}
		logging.debug("Las estadisticas sin formatear son: ")
		for nombreVia,viaMultiple in self.viasMultiples.iteritems():
			dicVia=viaMultiple.getDicEstadisticas()
			logging.debug("viaMultiple= "+str(nombreVia)+
				"; dicVia= "+str(dicVia))
			logging.debug("---------------------------------------------- ")
			logging.debug("")
			estadisticasFinales[viaMultiple.getNombre()]=dicVia
		self.reloj.detener()
		# Se formatean las estadisticas y se crea el graficador para los resultados.
		estadisticasDeVias={}
		estadisticasDeVias=self.completarEstadisticas(estadisticasFinales)
		self.graficarResultados(estadisticasDeVias)

	def cancelar(self):
		""" Este metodo cancela la ejecucion de la simulacion."""
		logging.debug("Terminando la simulacion...")
		logging.debug("")
		os.kill(os.getpid(),signal.SIGKILL)
		return True

	def completarEstadisticas(self,estadisticasFinales):
		""" Se adaptan las estadisticas al formato esperado por el graficador.
			Un ejemplo del formato que mantienen las estadisticas es el siguiente:
			{
				0: {'nombreVia': 'viaX', 'nombreLink': 'link1', 'tipoVariable': 'n', 'rangoValores': {1: 4, 2: 0}, 'nombreVariable': 'n(i): Cant. vehiculos en via'}, 
				1: {'nombreVia': 'viaX', 'nombreLink': 'interseccionL1', 'tipoVariable': 'w', 'rangoValores': {1: 0, 2: 0}, 'nombreVariable': 'w(i): Cant.vehiculos esperando'}
			}
			@param estadisticasFinales: Estadisticas finales al terminar la ejecucion de la simulacion
			@type estadisticasFinales: Diccionario
			@return: Se retornan las estadisticas formateadas para ser recibidas por el graficador.
			@rtype: Diccionario """
		estadisticasFormateadas={}
		posActual=1
		# Se obtienen los diccionarios de estasdisticas para c/u de las vias.
		for nombreVia,dicRangoValores in estadisticasFinales.iteritems():
			estadisticasFormateadas[posActual]={}
			estadisticasFormateadas[posActual]['nombreVia']=nombreVia
			nombreLink=None
			if nombreVia=='viaX':
				nombreLink='link1'
			elif nombreVia=='viaYDesc':
				nombreLink='link6'
			elif nombreVia=='viaYAsc':
				nombreLink='link3'
			estadisticasFormateadas[posActual]['nombreLink']=nombreLink
			# El nombreVariable es el nombre de la variable que se mide y es lo que se muestra en el grafico
			# en el eje X.
			estadisticasFormateadas[posActual]['nombreVariable']='n(i): Cant. vehiculos en via'
			estadisticasFormateadas[posActual]['rangoValores']={}
			for nroCiclo,cantVehiculos in dicRangoValores.iteritems():
				estadisticasFormateadas[posActual]['rangoValores'][nroCiclo]=cantVehiculos
			posActual+=1
		logging.debug("Las estadisticasFormateadas son: ")
		logging.debug(estadisticasFormateadas)
		logging.debug("")
		return estadisticasFormateadas

	# Simulacion.graficarResultados()
	def graficarResultados(self,resultados):
		""" Este metodo crea un objeto que realiza el dibujado de las graficas con mathplotlib (pyplot).
			Este metodo produce un grafico de barra con los resultados  de la simulacion.
			El diccionario de resultados se encuentra indexado por un nro para mantener el indice  
			acerca de cual es el grafico actual dibujado. Y por cada indice se mantiene un diccionario
			que contiene el nombre del link dibujado, el nombre de la variable y graficada y el
			rango de valores del grafico.
			Un ejemplo del formato que recibe el graficador es el siguiente:

			dicc={ 0:{ "nombreLink":"link1",  "variable": "n(i)", "rangoValores":{ 1 : 20, 2 : 1 } },
					  1:{ "nombreLink":"link1",  "variable": "w(i)", "rangoValores":{ 1 : 10 ,  2 : 1 } },

					  2:{ "nombreLink":"link3",  "variable": "w(i)", "rangoValores":{ 1 : 20, 2 : 1 } },
					  3:{ "nombreLink":"link3",  "variable": "w(i)", "rangoValores":{ 1 : 20, 2 : 1 } },

					  4:{ "nombreLink":"link6",  "variable": "w(i)", "rangoValores":{ 1 : 20, 2 : 1 } },
					  5:{ "nombreLink":"link6",  "variable": "w(i)", "rangoValores":{ 1 : 20, 2 : 1 } },
					   ...
					 }
			@param resultados: Resultados recogidos por la simulacion
			@type resultados: Diccionario """
		logging.debug("================== Inicio de simulacion.graficarResultados() ================== ")
		logging.debug("Resultados obtenidos de la simulacion: ")
		logging.debug(resultados)
		self.graficador=Graficador(resultados,self.cantidadCiclos)
		msgbox("Simulacion terminada exitosamente!",'Simulacion de trafico', ok_button="Aceptar")
		logging.debug("================== Fin de simulacion.graficarResultados() ================== ")
		logging.debug("")