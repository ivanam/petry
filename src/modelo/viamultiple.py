""" Este modulo define todo el comportamiento de la clase ViaMultiple y, esparce el comportamiento en los siguientes
	submodulos:
		-gettersysettersviamultiple.py. Modulo que define todos los getters y setters de la via multiple.
		-reddepetriviamultiple.py. Modulo que define metodos relacionados con el disparo de las transiciones y
		la manipulacion de la red de Petri desde la via multiple. """
import threading
from utilidades.constantes import CONSTANTES_LAYOUT,CANT_NO_CONTABILIZADA
from gettersysettersviamultiple import *
from reddepetriviamultiple import *
import time

class ViaMultiple(threading.Thread):
	""" La clase ViaMultiple se encarga de generar el trafico entrante y saliente de la autopista y mantiene una 
	referencia a la RP y al nombre de sus nodos de inicio/fin.  Esta clase tambien mantiene el color usado
	para el color que representa cada stream. La distribucion de colores en vias es la siguiente:
		*ViaMultiple1 --> Stream1,Stream2 -->Color Rojo
		*ViaMultiple2 --> Stream3,Stream4 -->Color Azul
		*ViaMultiple1 --> Stream5 -->Color Verde """

	#Asignacion de comportamiento de via multiple organizado en otros modulos.
	# Modulo de getters y setters
	getSimulacion=getSimulacion
	setSimulacion=setSimulacion
	setGeneradorTrafico=setGeneradorTrafico
	getGeneradorTrafico=getGeneradorTrafico
	getDuracionFaseEnVia=getDuracionFaseEnVia
	getCantTransicionesLink=getCantTransicionesLink
	setFasesTemporizadas=setFasesTemporizadas
	getFasesTemporizadas=getFasesTemporizadas
	getNombreSemaforoLink=getNombreSemaforoLink
	getCantCarriles=getCantCarriles
	getDicEstadisticas=getDicEstadisticas
	setDicEstadisticas=setDicEstadisticas
	getDiccTraficoPredefinido=getDiccTraficoPredefinido
	getNombre=getNombre
	getNodosInicio=getNodosInicio
	getNodosFin=getNodosFin
	setRedPetri=setRedPetri
	getRedPetri=getRedPetri
	setSemaforo=setSemaforo
	getSemaforo=getSemaforo
	setTransicionesSalidaLink=setTransicionesSalidaLink

	# Modulo de comportamiento relacionado a la red de Petri
	agregarToken=agregarToken
	crearRP=crearRP
	generarAltOrdenadas=generarAltOrdenadas

	def __init__(self,nombre, delayVehiculos, diccRP,
		viasCircHabilitadas,
		diccInicio,diccFin,diccTraficoPredefinido,cantCarriles,cantTransicionesLink,
		fasesARegistrar,nombreSemaforo,simulacion,transicionesSalidaLink=None):
		""" Metodo constructor de la clase ViaMultiple.
			@param nombre: El nombre de la viaMultiple
			@type nombre: String
			@param delayVehiculos: Retardo que simula la velocidad promedio de cirulacion de los vehiculos
			por una via multiple.
			@type delayVehiculos: Integer
			@param diccRP: Diccionario que contiene el esquema de la red de Petri para la via multiple.
			@type diccRP: Diccionario
			@param viasCircHabilitadas:
			@type viasCircHabilitadas:
			@param diccInicio: Diccionario que contiene los nombres de los lugares en la red de Petri 
			por los que los vehiculos ingresan a la misma.
			@type diccInicio: Diccionario
			@param diccFin:Diccionario que contiene los nombres de los lugares en la red de Petri 
			por los que los vehiculos ingresan a la misma.
			@type diccFin: Diccionario

			@param diccTraficoPredefinido: Coleccion que determina la frecuencia de ingreso del trafico en la via multiple,
			segun la fase en la que  se encuentre el semaforo.
			@type diccTraficoPredefinido: Diccionario

			@param cantCarriles: Cantidad de carriles de la via multiple.
			@type cantCarriles: Integer
			@param cantTransicionesLink: Indica la cantidad de transiciones en que un vehiculo se
			considera dentro del link que contiene la viaMultiple (Usado para el calculo de estadisticas).
			@type cantTransicionesLink: Integer

			@param fasesARegistrar: Coleccion con los nombres de las fases que se deben registrar y la duracion de 
			las mismas.
			@type fasesARegistrar: Diccionario

			@param nombreSemaforo: Nombre del semaforo que se encuentra sobre la via regulando el trafico
			@type nombreSemaforo: String
			@param simulacion: Referencia a la simulacion principal(main)
			@type simulacion: Simulacion
			@param transicionesSalidaLink: Cantidad de transiciones que conforman el modelo de la red de Petri de la via.
			Este dato se utiliza para calcular
			@type transicionesSalidaLink: Lista """
		threading.Thread.__init__(self,name="Thread-ViaMultiple->"+str(nombre))
		self.nombre=nombre
        #Este atributo permite generar vehiculos incrementalmente sin que sus Id's se repitan.
		self.cantVehiculos=1
		#La via de circulacion mantiene un diccionario de inicio y uno de fin
		#que tienen los nombres de los nodos de inicio  y de fin de la via
		self.nodosInicio=diccInicio
		self.nodosFin=diccFin
		#La ViaMultiple mantiene una coleccion de "viasCircHabilitadas", que son strings
		# con los nombres de las  vias a las que es posible acceder. Esta coleccion se 
		# usa en la temporizacion de la RP para que cuando un vehiculo se encuentra
		# en un lugar que es compartido por dos o mas vias de circulacion, este no 
		# sea tomado por una ViaMultiple a la que realmente no es posible acceder.
		# La coleccion de cambios de via se lee de esquemaRP.py ya que no cambiara en nigun momento.
		self.viasCircHabilitadas=viasCircHabilitadas
		#Se agrega la via misma como una via de circulacion valida, sino no se podran
		#disparar transiciones propias de la via. Este atributo se utiliza en el metodo "esViaValida()".
		self.viasCircHabilitadas.append(self.nombre)
		#La RP tiene la referencia a la ViaMultiple a la que pertence
		self.redPetri=self.crearRP(diccRP,self,nombre)
		self.bloqueo=threading.RLock()
		# La viaMultiple mantiene tiene una referencia del estado de la simulacion
		# y el delay correspondiente a los vehiculos que circulan por ella.
		# El atributo self.delayVehiculos es el tiempo promedio que esperan los vehiculos
		# en un lugar de RP, antes de pasar al siguiente lugar de RP,calculado en base a la 
		# velocidad de los vehiculos reales(Para automoviles=.45 y para colectivos=1.35 por defecto).
		self.simulacion=None
		self.delayVehiculos=delayVehiculos
		
		# Se mantiene una referencia al semaforo que pertenece a una via.
		# En base al estado de un semaforo, al nro de ciclo y al nombreVia
		# se puede determinar cuando debe ingresar un vehiculo.
		self.semaforo=None
		# El atributo self.trafPredefinido, permite a la ViaMultiple conocer cuanto tiempo
		# tiene que temporizar para un ciclo de la simulacion.
		self.trafPredefinido=diccTraficoPredefinido
		# Cada viaMultiple mantiene la cantidad de carriles que compone.
		# Este valor se utiliza para calcular la cantidad de vehiculos que ingresaron cuando se dispara
		# una transicion dentro de un ciclo de tiempo.
		self.cantCarriles=cantCarriles

		# Cada viaMultiple mantiene un diccionario de estadisticas (self.dicEstadisticas)
		# donde mantiene un registro formal del trafico que circula por la ViaMultiple en cada ciclo.
		# La clave es el ciclo de iteracion, mientras que el valor es la cantidad de vehiculos
		# generados en ese ciclo de tiempo. 
		# La cantidad de todos los ciclos se inicializa por defecto en cero.
		# El dicEstadisticas, se crea dinamicamente con la cantidad de ciclos que ingresa el usuario.
		
		self.dicEstadisticas= {}
		for pos in xrange(1,simulacion.getCantidadCiclos()+1):
			self.dicEstadisticas[pos]=CANT_NO_CONTABILIZADA

		# -Cada viaMultiple mantiene un arreglo "transicionesSalidaLink" que especifica los nombres de las 
		# transiciones que producen que se decremente la cant. de vehiculos actual en la viaMultiple.
		# Este atributo se usa para las estadisticas de manera que cuando el semaforo dispare alguna de las 
		# transiciones que producen el estado "ROJO" en el semaforo (para la viaMultiple),se incremente
		# la cant. de vehiculos.
		self.transicionesSalidaLink=transicionesSalidaLink
		#Este es el nombre que se usa para pedir la referencia del semaforo a la RedDeSemaforos. 
		self.nombreSemaforoLink=nombreSemaforo

		# Cada viaMultiple mantiene un diccionario que determina si un ciclo se encuentra totalmente temporizado
		# (todas las fases rojas o verde_amarillas se encuentran temporizadas). Esto permite que recien cuando se terminen
		# de temporizar todas las fases en un ciclo de una via, se salga y se espere a que la reddesemaforos
		# notifique que el proximo ciclo de tiempo comenzo.
		self.fasesTemporizadas={}
		self.fasesTemporizadas[1]=True
		for pos in xrange(2,simulacion.getCantidadCiclos()+1):
			self.fasesTemporizadas[pos]=False
		# Se indica cual es la cantidad de transiciones que tiene que recorrer un vehiculo para considerarse dentro
		# del link que contiene la viaMultiple (Usado para el calculo de estadisticas).
		self.cantTransicionesLink=cantTransicionesLink
		
		# -Se agrega un diccionario en la viaMultiple que tiene como nombre los nombres de las fases que se deben registrar,
		# como valor la duracion de dichas fases. Estos valores se emplean para el calculo de la cantidad de vehiculos
		# que permaneceran en la via cuando inicie el siguiente ciclo.
		self.fasesARegistrar=fasesARegistrar
		self.generadorTrafico=None
		self.simulacion=simulacion

	
	# Este metodo es llamado desde simulacion.detener(), y cuando una viaMUltiple no termino
	# de temporizar alguna de las fases. EN general, puede quedar inconcluso el ultimo ciclo (ciclo 20),
	# por lo que mayormente faltara temporizar solamente este ciclo. Sin embargo, se recorren y verifican
	# todos los ciclos de tiempo por si alguno no esta temporizado.
	def terminarCalculoDeEstadisticas(self):
		""" Este metodo revisa los registros de las estadisticas generadas durante la simulacion.Si algun evento no alcanza a ser manejado,
			por el menejador del generador de trafico que corresponda, se realiza el calculo de esa cantidad de vehiculos.
			@return: El generador de trafico de la via multiple
			@rtype: GeneradorTrafico"""
		logging.debug(" ============================= Inicio de terminarCalculoEstadisticas() ============================")
		logging.debug("")
		cantMaximaCiclos=self.simulacion.getCantidadCiclos()-1
		# Cuando se comienza por el primer CT se estan en realidad, calculando las estadisticas para la segunda fase.
		for nroCiclo,terminoCiclo in self.fasesTemporizadas.iteritems():
			if nroCiclo <= cantMaximaCiclos and (not terminoCiclo or self.dicEstadisticas[nroCiclo+1]==CANT_NO_CONTABILIZADA):
				estado='Detenido'
				logging.debug("Completando las estadisticas de via %s para el ciclo: %s " % (self.nombre,nroCiclo+1))
				logging.debug("")
				# -Se obtiene el intervalo de ingreso de vehiculos en el estado "Detenido" 
				# (Unico estado en que se calcula el calculo de ingreso de vehiculos).
				#- Se obtiene el "tiempo" de ingreso de los vehiculos y la "duracionFase" total de una fase.
				(tiempo,duracionFase)=self.getGeneradorTrafico()._obtenerIntervalo(estado,nroCiclo)
				logging.debug("tiempo= %s ; duracionFase= %s "%(tiempo,duracionFase))
				logging.debug("")
				# Se calculan las cantidades de temporizaciones en base al intervaloIngresoVehiculos ("tiempo") de la viaMultiple
				# en un ciclo y, a la duracion de la fase, la cantidad de temporizaciones de intervaloIngresoVehiculos
				# que se deben hacer dentro de la fase.
				(cantTemporizaciones,tiempoSobrante)=self.getGeneradorTrafico().calcularCantTemporizaciones(duracionFase,tiempo)
				logging.debug("cantTemporizaciones= %s ; tiempoSobrante= %s "%(cantTemporizaciones,tiempoSobrante))
				logging.debug("")
				# Se obtiene el intervalo de tiempo dentro de una fase de semaforo "Detenido" para el calculo de las
				# estadisticas.
				duracionFaseVia=self.getDuracionFaseEnVia(estado)
				# Se incrementan las estadisticas para el nroCiclo actual.
				self.incrementarEstadisticas2(nroCiclo+1,cantTemporizaciones,tiempo,duracionFaseVia,estado)
				logging.debug("Se incrementaron las estadisticas para el ciclo: %s  en la viaMultiple: %s"
				 % (nroCiclo,self.nombre))
				logging.debug("")
		logging.debug(" ============================= Fin de terminarCalculoEstadisticas() ============================")
		logging.debug("")

	def seDebeContabilizarTrafico(self,nombreFaseSemaforo):
		""" Este metodo determina si se debe contabilizar el trafico durante la fase del semaforo,
			en base al nombre de la fase ("EnAvance", "EnAvanceConPrecaucion","Detenido").
			@param nombreFaseSemaforo: Nombre de la fase en que se encuentra el semaforo
			@type nombreFaseSemaforo: String """
		resultado=False
		clave=""
		if nombreFaseSemaforo=="EnAvance" or nombreFaseSemaforo=="EnAvanceConPrecaucion":
			clave="fase_verde_amarilla"
		else:
			clave="fase_roja"	
		if self.fasesARegistrar.has_key(clave):
			resultado=True
		return resultado

	# viaMultiple.fasesYaTemporizada()
	def fasesYaTemporizada(self,cicloActual):
		""" Este metodo indica si ya se han temporizado todas las fases para un ciclo dado.
			@param cicloActual: Numero de ciclo
			@type cicloActual: Integer """
		return self.fasesTemporizadas[cicloActual]

	# ViaMultiple.estanTodasFasesTemporizadas()
	def estanTodasFasesTemporizadas(self,nroCiclo):
		""" Este metodo verifica si todas las fases (fase_roja y fase_verde_amarilla) en "nroCiclo",
			fueron temporizadas, si es asi retorna True. En caso contrario, retorna False.
			@param nroCiclo: Numero de ciclo para el que se producira la verificacion
			@type nroCiclo: Integer
			@return: Un valor booleano
			@rtype: Boolean """
		resultado=False
		diccPredefinido=self.getDiccTraficoPredefinido(nroCiclo)
		logging.debug("Diccionario de trafico predefinido obtenido: "+str(diccPredefinido)+" en nroCiclo: "+str(nroCiclo))
		logging.debug("")
		if diccPredefinido["fase_roja"]["estaTemporizada"] and diccPredefinido["fase_verde_amarilla"]["estaTemporizada"]:
			resultado=True
		logging.debug("Fin de estanTodasFasesTemporizadas() resultado= "+str(resultado))
		logging.debug("")
		return resultado


	def esTransicionALinkSalida(self,nombreTrans):
		""" Este metodo es llamado por la RP de la via multiple con un nombre de transicion
			y se retorna True si la transicion es una de las transiciones de salida del link.
			@param nombreTrans: Nombre de la transicion a verificar
			@type nombreTrans: String """
		logging.debug("Transicion enviada por parametro: "+str(nombreTrans))
		logging.debug("")
		result=False
		for t in self.transicionesSalidaLink:
			logging.debug("Transicion t iterada= "+t+ "; nombreTrans= "+nombreTrans+"; nombreTrans==t? = "+str(nombreTrans==t))
			logging.debug("")
		 	if nombreTrans==t:
		 		result=True
		 		break
		return result

	def actualizarDicEstadisticas(self,nroCiclo,cantVehiculos):
		""" Este metodo actualiza las estadisticas de vehiculos en viaMultiple,
			incrementando la cantidad que haya habido previamente.
			@param nroCiclo: Numero de ciclo para el que se actualizaran las estadisticas
			@type nroCiclo: Integer
			@param cantVehiculos: Cantidad de vehiculos que se deben actualizar en nroCiclo
			@type cantVehiculos: Integer """
		logging.debug("Antes de actualizarEstadisticas: "+str(self.dicEstadisticas)+
			"; cantVehiculos: "+str(cantVehiculos)+"; nroCiclo: "+str(nroCiclo) )
		logging.debug("")
		logging.debug("self.dicEstadisticas[nroCiclo]= "+str(self.dicEstadisticas[nroCiclo]))
		logging.debug("")
		self.dicEstadisticas[nroCiclo]= cantVehiculos
		logging.debug("Despues de actualizarEstadisticas: "+str(self.dicEstadisticas)+
			"; cantVehiculos: "+str(cantVehiculos)+"; nroCiclo: "+str(nroCiclo))
		logging.debug("")
		

	def actualizarDiccTraficoPredefinido(self,nroCiclo,dic):
		""" Este metodo actualiza la entrada del diccionario de trafico predefinido
			que corresponde a un numero de ciclo.
			@param nroCiclo: Numero de ciclo 
			@type nroCiclo: Integer
			@param dic: Diccionario de trafico predefinido
			@type dic: Diccionario """
		self.trafPredefinido[nroCiclo]=dic
	
	# ViaMultiple.run()
	def run(self):
		""" Este metodo invoca a la temporizacion de la red de Petri que mantiene la via multiple,
			luego detiene el movimiento de los vehiculos en esta via por un instante de tiempo, que varia 
			segun el tipo de vehiculo que circula por la misma. Estas operaciones, se ejecutan continuamente
			durante toda la simulacion hasta que esta termina o es cancelada por el usuario. """
		logging.debug("====================== Inicio de viaMultiple.run():"+str(self.nombre)+" ======================")
		logging.debug("")
		while not self.simulacion.terminoSimulacion():
			self.temporizar()
			logging.debug("luego de ViaMultiple.temporizar()")
			logging.debug("")
			self.despacharTrafico(self.getNodosFin())
			logging.debug("luego de self.despacharTrafico()")
			logging.debug("")
			#Se duerme el tiempo que tenga para temporizar la ViaMultiple
			time.sleep(self.delayVehiculos)
			logging.debug("viaMultiple.run(): Despues de dormirme self.delayVehiculos= "+str(self.delayVehiculos))
			logging.debug("")
		logging.debug("El thread de la ViaMultiple "+str(self.nombre)+" termino satisfactoriamente!")
		logging.debug("")
		logging.debug("====================== Fin de viaMultiple.run():"+str(self.nombre)+" ======================")
		logging.debug("")
	
	# viaMultiple.esViaValida()
	def esViaValida(self,nombreVia):
		""" Este metodo es llamado por la RP con el nombre de una via para permitir o no el disparo de una transicion,
			y por lo tanto conocer si un vehiculo puede cambiar de via.
			@param nombreVia: Nombre de la via multiple que se verificara 
			@type nombreVia: String
			@return: Valor que indica si la via es valida
			@rtype: boolean"""
		esValida=False
		if self.nombre==nombreVia:
			esValida=True
		else:
			for via in self.viasCircHabilitadas:
				if nombreVia==via:
					esValida=True
		logging.debug("")
		logging.debug("ViaMultipleOrigen: "+str(nombreVia)+";  viaMultiple.nombre: "+str(self.nombre)+
			"esValida: "+str(esValida))
		logging.debug("")
		return esValida


	#ViaMultiple.temporizar()
	def temporizar(self):
		""" Este metodo solicita a la red de Petri que dispare las transiciones que pertenecen a la via,
			lo que produce que se desplacen los vehiculos por la interseccion de trafico."""
		red=self.getRedPetri()
		red.temporizar(self,True)
		self.setRedPetri(red)

	# ViaMultiple.originarTrafico().
	def originarTrafico(self,nroCiclo):
		""" Este metodo introduce trafico a una via multiple en ambos carriles insertando el mismo en los nodosInicio
			de la red de Petri.
			El metodo de la via multiple 'originarTrafico()' es llamado por el generador de trafico cuando este se encuentra
			en alguna fase de semaforo (verde-amarilla o roja) para un ciclo de tiempo y ha transcurrido el intervalo de 
			tiempo necesario para que ingrese un vehiculo. Asi, el generador de trafico, recibe los eventos de cambio de fase
			de un semaforo, se encarga controlar la cantidad de temporizaciones que pueden ocurrir en un ciclo de tiempo,
			en una fase de semaforo especifica, como asi tambien de enviar datos parciales para que la via multiple 
			termine de calcular la cantidad de vehiculos y registre estas en las estadisticas.
			
			@param nroCiclo: Numero de ciclo en el que ingresara el trafico
			@type nroCiclo: Integer """
		diccInicio=self.getNodosInicio()
		redPetri=self.getRedPetri()
		tamanio=len(diccInicio)
		for k,v in diccInicio.iteritems():
			if redPetri.place(diccInicio[k]).is_empty():
				pathIcono=redPetri.place(diccInicio[k]).getPathIcono()
				lugarRP=self.redPetri.place(diccInicio[k])
				vehiculo=Vehiculo(self._generarIdVehiculo(),pathIcono,lugarRP,self,nroCiclo)
				redPetri.place(diccInicio[k]).add(vehiculo)
		self.setRedPetri(redPetri)

	# ViaMultiple.incrementarEstadisticas2().
	def incrementarEstadisticas2(self,nroCicloActual,cantTemporizaciones,instanteTiempo,duracionFase,nombreEstado):
		""" Este metodo segun la cantidad de carriles de la via, el numero de ciclo y la cantidad de temporizaciones
			(resultantes de haber dividido la duracion de la fase/intervalo de ingreso de vehiculos en esa fase),
			termina el calculo de la cantidad de vehiculos que quedaran en la via para el proximo ciclo y,
			efectua la actualizacion de las estadisticas.

			@param nroCicloActual: Numero de ciclo de tiempo
			@type nroCicloActual: Integer
			@param cantTemporizaciones: Cantidad de temporizaciones totales que son posibles. Esta cantidad se utiliza,
			para calcular cuantos de esos vehiculos, se quedaran detenidos en la fase roja del semaforo y, estaran al
			comienzo del siguiente ciclo.
			@type cantTemporizaciones: Integer

			@param instanteTiempo: Intervalo de ingreso de vehiculos a la via
			@type instanteTiempo: Integer
			@param duracionFase: Duracion total de la fase de un semaforo para el nroCicloActual 
			@type duracionFase: Integer
			@param nombreEstado: Nombre del estado del semaforo
			@type nombreEstado: String """
		cantVehiculosEnCiclo=deltaDesplazamiento=0
		# Si la cantTemporizaciones es mayor a cero, se procede con el calculo, sino se deja cantVehiculos con su
		# valor por defecto.
		if cantTemporizaciones!=0:
			instanteAcumulado=instanteTiempo
			# Se considera el desplazamiento que los vehiculos tienen que hacer, si el semaforo
			# esta en alguno de estos estados.
			if nombreEstado=="EnAvance" or nombreEstado=="EnAvanceConPrecaucion":
				deltaDesplazamiento= self.delayVehiculos * self.cantTransicionesLink
			for i in xrange(1,cantTemporizaciones+1):
				if nombreEstado=="EnAvance" or nombreEstado=="EnAvanceConPrecaucion":
					# Si el vehiculo esta en fase_verde_amarilla, se chequea que si el vehiculo esta en el Link de la viaMultiple
					# para cuando la fase verde_amarilla termina (es decir, para cuando la fase_verde_amarilla cambie a fase_roja),
					# si es asi se registra en las estadisticas.
					if (instanteAcumulado + deltaDesplazamiento) >= duracionFase:
						cantVehiculosEnCiclo+=self.getCantCarriles()
				else:
					# Si el vehiculo se genera durante la fase roja se incluye en las estadisticas
					if instanteAcumulado <= duracionFase:
						cantVehiculosEnCiclo+= self.getCantCarriles()
				# Se calcula cuando sera el siguiente instanteTiempo en que ingresaran los vehiculos.
				instanteAcumulado+=instanteTiempo
		logging.debug("cantVehiculosEnCiclo: "+str(cantVehiculosEnCiclo)+
			"; instanteTiempo: "+str(instanteTiempo)+"; cantTemporizaciones: "+str(cantTemporizaciones)+
			"; duracionFase: "+str(duracionFase))
		logging.debug("")
		self.actualizarDicEstadisticas(nroCicloActual,cantVehiculosEnCiclo)
		logging.debug("Se incrementaron las estadisticas para la viaMultiple!: nroCicloActual= "+
				str(nroCicloActual)+ "; self.viaMultiple.dicEstadisticas= "+str(self.getDicEstadisticas() ))
		logging.debug("")

	def despacharTrafico(self,diccFin):
		""" Este metodo se encarga de despachar el trafico en la RP, eliminando tokens de los 
			nodos de fin de la red de Petri. Recibe un diccionario con los nombres
			de los nodos de Fin de la RP(diccInicio).
			@param diccFin: Coleccion de nombres de nodos por los que los vehiculos abandonan la via multiple.
							i.e: diccFin={ 1: "p19", 2: "p29"}.
			@type diccFin: Diccionario """
		redPetri=self.getRedPetri()
		for k,v in diccFin.iteritems():
			if not redPetri.place(diccFin[k]).is_empty():
				#Se marca el vehiculo que se encuentra en un lugar
				#como que no figura en el escenario, para que en proximo
				#actualizacion que realice la vista elimine el sprite como
				# nodo hijo del escenario
				for coche in self.redPetri.place(diccFin[k]):
					coche.getLugarRP().empty()
		self.setRedPetri(redPetri)

	def _generarIdVehiculo(self):
		""" Este metodo obtiene en base al nombre de la via+(cantVehiculos+1)
			un idVehiculo unico.

			@return: Un identificador de vehiculo valido para la simulacion
			@rtype: String """
		self.cantVehiculos+=1
		return str(self.nombre)+str(self.cantVehiculos)