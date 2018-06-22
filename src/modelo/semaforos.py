""" Este modulo define las clases Semaforo, las clases que representan los distintos tipos de estados en que se puede
	encontrar un semaforo y la red de semaforos que agrupa a estos."""
import threading
from utilidades.unidades import *
from pydispatch import dispatcher

##########################################################################################
##############################Imports de snakes###########################################
##########################################################################################
from snakes.nets import *
import snakes.plugins as plugins

##########################################################################################
##############################Imports del plugin que extiende a Snakes####################
##########################################################################################
plugins.load('RedPetriV3', 'snakes.nets', 'RedPetriRodrigo')
from RedPetriRodrigo import *
import logging

class Semaforo(object):
	""" Esta clase mantiene la informacion referente al semaforo como su posicion, dimensiones,
		estado (rojo | amarillo | verde) y la logica para la modificacion del estado del semaforo."""
	def __init__(self,diccSemaforo):
		"""Constructor de semaforo.
		   @param diccSemaforo: Coleccion con el nombre, posicion y dimensiones del semaforo.
		   @type diccSemaforo: Diccionario.
		 """
		self.nombre=diccSemaforo["nombre"]
		self.posicion=Posicion(diccSemaforo["posicion"]["x"],
									diccSemaforo["posicion"]["y"])
		self.ancho=diccSemaforo["tamanio"]["ancho"]
		self.alto=diccSemaforo["tamanio"]["alto"]
		self.estado=Detenido(self)
		self.idSemaforo=0
		# El semaforo mantiene un atributo "esModificado" que es usado por la vista
		# en escLayer.actualizar() -> reddeSemarofos.dibujar() para determinar si
		# el semaforo cambio desde la ultima vez que se dibujo. Si no cambio, no se dibuja.
		# NOTA: Este atributo es True solamente cuando cambia por primera vez el semaforo.
		self.esModificado=False
		# Despachador para notificar del cambio de estado en un semaforo
		self.dispatcher=dispatcher
		self.generador=None

	# Semaforo.notificarAViaMultiple()
	def notificarAViaMultiple(self):
		""" Este metodo utiliza la libreria de eventos PyDispatcher para generar un evento que notifique 
			a las viasMultiples que ha ocurrido un cambio de estado en el semaforo. Este metodo
			es invocado desde el plugin de red de Petri. """
		# NOTA: Se notifica solo si el estado del semaforo es "EnAvance" o "Detenido".
		# ("EnAvance", "EnAvanceConPrecaucion","Detenido")
		logging.debug("Estado actual del semaforo %s es: %s ;" %(self.nombre,self.estado.getNombre()))
		logging.debug("")
		if self.estado.getNombre() == "EnAvance" or self.estado.getNombre() == "Detenido":
			nombreThread="Thread-GeneradorTrafico-"+str(self.generador.getViaMultiple().getNombre())
			t=threading.Thread(target=self.notificarCambioEstado,name= nombreThread,args=(self,))
			t.setDaemon(True)
			t.start()

	# Semaforo.notificarCambioEstado()
	def notificarCambioEstado(self,mensajero):
		""" Este metodo es llamado por notificarAViaMultiple(), y es utilizado como funcion auxiliar
			para producir un evento. 
			@param mensajero: objeto que se envia junto con el mensaje del evento.
			@type mensajero: Instancia de semaforo
			"""
		logging.debug("En semaforo.notificarCambioEstado() ...")
		logging.debug("")
		nombreEvento="cambio_estado_"+str(self.generador.getViaMultiple().getNombre())
		self.dispatcher.send(signal=nombreEvento,sender=self,mensajero=self)
		logging.debug("nombreSemaforo: %s Despues de semaforo.notificarCambioEstado()  ..." %
			self.nombre)
		logging.debug("")
		return

	# Semaforo.setGenerador()
	def setGenerador(self,g):
		""" Metodo que establece un generador de trafico a un Semaforo.
			@param g: generador que se registra ante el semaforo
			@type g: Instancia de GeneradorTrafico """
		self.generador=g

	# Semaforo.registrarGenerador()
	def registrarGenerador(self):
		""" Metodo que registra un handler (metodo de un objeto) con el nombre de evento que
			al que debe reaccionar."""
		nombreEvento="cambio_estado_"+str(self.generador.getViaMultiple().getNombre())
		self.dispatcher.connect( self.generador.manejadorCambioEstado, 
				signal=nombreEvento, sender=self)
		logging.debug("Todas las seniales registradas!")
		logging.debug("")
	
	# Semaforo.setIdSemaforo()
	def setIdSemaforo(self,idSem):
		""" Metodo setter para el atributo 'idSemaforo'.
			@param idSem: Nombre que identifica al semaforo.
			@type idSem: String. """
		self.idSemaforo=idSem

	# Semaforo.setGenerador()
	def getNombre(self):
		""" Metodo getter para el atributo 'nombre'.
			@return: Nombre del semaforo.
			@rtype: String. """
		return self.nombre

	# Semaforo.getEstado()
	def getEstado(self):
		""" Metodo getter para el atributo 'estado'.
			@return: Estado del semaforo.
			@rtype: Estado. """
		return self.estado

	# Semaforo.setEstado()
	def setEstado(self,estado):
		""" Metodo setter para el atributo 'estado'."""
		self.estado=estado

	# Semaforo.getPosicion()
	def getPosicion(self):
		""" Metodo getter para el atributo 'posicion'.
			@return: La posicion en la que se encuentra el semaforo.
			@rtype: Posicion. """
		return self.posicion

	# Semaforo.estaModificado()
	def estaModificado(self):
		""" Metodo getter para el atributo 'esModificado'.
			@return: Flag que indica si el semaforo esta modificado.
			@rtype: Boolean. """
		return self.esModificado

	
	# Semaforo.getColores()
	def cambiarASigEstado(self):
		""" Este metodo cambia el estado del semaforo a un estado coherente
			segun el estado actual del mismo."""
		self.estado.avanzarASigEstado()
		self.esModificado=True

	# Semaforo.getColores()
	def getColores(self):
		""" Este metodo retorna la tupla con la combinacion de colores de un semaforo."""
		return self.estado.getColores()

	# Semaforo.getPosicion()
	def getAncho(self):
		""" Metodo getter para el atributo 'ancho'.
			@return: Ancho del semaforo.
			@rtype: Integer. """
		return self.ancho

	# Semaforo.getPosicion()
	def getAlto(self):
		""" Metodo getter para el atributo 'alto'.
			@return: Alto del semaforo.
			@rtype: Integer.
			"""
		return self.alto

class Estado(object):
	""" Esta clase encapsula la tupla con la combinacion de colores RGB para el semaforo. """
	def __init__(self):
		pass
	#Estado.getColores()
	def getColores(self):
		""" Metodo getter para los colores del semaforo. 
			Retorna un diccionario, de la forma (RGBA) cuyas claves son los nombres de los colores y,
			los datos los valores de los colores en formato RGB."""
		return {"rojo": self.colorR,"azul":self.colorB,"verde": self.colorG,"alfa":160}
	#Estado.avanzarASigEstado()
	def avanzarASigEstado(self):
		"""Metodo implementado en las subclases de estado."""
		pass
	#Estado.getNombre()
	def getNombre(self):
		"""Metodo getter para el nombre de un estado. Retorna un String que representa el nombre del estado actual.
			Se utiliza para comparaciones al momento de efectuar las temporizaciones."""
		return str(self.__class__.__name__)

class EnAvance(Estado):
	""" Subclase de Estado que representa un semaforo en estado 'verde'."""
	def __init__(self,semaforo):
		""" Constructor de semaforo.
			@param semaforo:Semaforo al que pertenece el estado
			@type semaforo: Semaforo
			"""
		Estado.__init__(self)
		self.colorR=0
		self.colorG=214
		self.colorB=71
		self.semaforo=semaforo	

	def avanzarASigEstado(self):
		""" Este metodo modifica el semaforo para que este simbolice el estado 'Amarillo'."""
		self.semaforo.setEstado(EnAvanceConPrecaucion(self.semaforo))

class EnAvanceConPrecaucion(Estado):
	""" Subclase de Estado que representa un semaforo en estado 'amarillo'."""
	def __init__(self,semaforo):
		""" Constructor de semaforo.
			@param semaforo:Semaforo al que pertenece el estado
			@type semaforo: Instancia de Semaforo
			"""
		Estado.__init__(self)
		self.colorR=255
		self.colorG=216
		self.colorB=20
		self.semaforo=semaforo

	def avanzarASigEstado(self):
		""" Este metodo modifica el semaforo para que este simbolice el estado 'Rojo'."""
		self.semaforo.setEstado(Detenido(self.semaforo))

class Detenido(Estado):
	""" Subclase de Estado que representa un semaforo en estado 'rojo'."""
	def __init__(self,semaforo):
		Estado.__init__(self)
		self.colorR=204
		self.colorG=0
		self.colorB=0
		self.semaforo=semaforo
	
	def avanzarASigEstado(self):
		""" Este metodo modifica el semaforo para que este simbolice el estado 'Verde'."""
		self.semaforo.setEstado(EnAvance(self.semaforo))

class RedDeSemaforos(threading.Thread):
	""" Esta clase abstrae el funcionamiento de una red de semaforos, mantiene una referencia a los semaforos
		que la componen como asi tambien, a la red de Petri de cada uno. 
		Esta clase mantiene el orden de disparo de las transiciones de la red de Petri de los 3 semaforos,
		y se encarga de administrar el ciclo de tiempo (CT) actual. Ademas, se encarga de registrar los
		generadoresTrafico con los eventos y, cuando ocurre un cambio de ciclo de tiempo los notifica para que actualicen
		el numero de ciclo que mantienen.
		Ademas, se encarga de notificar a la simulacion cuando se ha alcanzado la cantidad maxima de CTs especificados
		por el usuario.
		------------------------------------------------------------------------------------------------------
		Terminologia asociada al funcionamiento de la red de semaforos:
			- TIEMPO DE CICLO (cycle time) --> Tiempo desde una fase roja hasta la siguiente fase roja.
			- DIVISON VERDE (Green split) -->  Fraccion de tiempo dentor de un ciclo de tiempo, en el que la 
			luz verde se encuentra habilitada.	
			- FASE --> Intervalo de tiempo durante la cual una combinacion dada de seniales de trafico en el area
			mantiene su estado. """
	def __init__(self,simulacion,diccRedSemaforos,ordenDisparoCiclos,cantCiclos):
		""" Constructor de RedDeSemaforos.
			@param simulacion: simulacion a la que pertenece la redDeSemaforos
			@type simulacion: Instancia de Simulacion
			@param diccRedSemaforos: Conjunto de valores que simboliza la posicion, alto,ancho y nombre de cada semaforo, ademas
										 del esquema de Red de Petri de toda la RedDeSemaforos.
			@param ordenDisparoCiclos: Conjunto de clave-valor de orden de disparo-nombre de transicion a disparar.
			@type ordenDisparoCiclos: Diccionario.
			@param cantCiclos: Cantidad maxima de ciclos que se deben temporizar en la simulacion.
			@type cantCiclos: Integer.
		"""
		threading.Thread.__init__(self,name="Thread-RedDeSemaforos")
		self.simulacion=simulacion
		#NOTA: El ciclo 1 es el estado inicial de la RP, por lo que los ciclos que ingresa el usuario
		# son la cantidad de cilos que se hacen a partir del ciclo 1. por ej. si el usuario ingresa
		# dos ciclos, se contara hasta el nroCiclo 3.
		#
		self.cantCiclos=cantCiclos
		self.ordenDisparoCiclos=ordenDisparoCiclos
		diccAtributosSem=[
					{"nombre": "semaforoLink1", "posicion":{"x":120, "y": 180}, "tamanio":{"ancho":15,"alto":200} ,"idSem":1 },
					{"nombre": "semaforoLink3", "posicion":{"x":500, "y": 390}, "tamanio":{"ancho":115,"alto":15} ,"idSem":2 },	
					{"nombre": "semaforoLink6", "posicion":{"x":150, "y": 150}, "tamanio":{"ancho":350,"alto":15} ,"idSem":3 }
		]
		self.semaforos={}
		for sem in diccAtributosSem:
			self.semaforos[sem["nombre"]]=Semaforo(sem)
			self.semaforos[sem["nombre"]].setIdSemaforo(sem["idSem"])
		# El semaforo del link1 arranca el ciclo en verde por lo que tiene que terminar encuentra
		# verde cuando termina el sig. ciclo.
		self.semaforos["semaforoLink1"].setEstado(EnAvance(self.semaforos["semaforoLink1"]))
		self.redPetri=self.crearRP(diccRedSemaforos)
		# La RedDeSemaforos mantiene un atributo para concoer el ciclo actual. El generadorTrafico de cada via
		# cuando genere trafico solicitara a la simulacion, que pedira al objeto redDeSemaforos este atributo.
		# De esta manera cada vehiculo mantendra el "nroCicloGenerado" que indicara el numero de ciclo en el que
		# el vehiculo fue generado. Esto sera utilizado por la redDeSemaforos en el metodo
		# "contabilizarVehiculos()", para contabilizar los vehiculos que solamente fueron generados
		# durante el ciclo actual.
		# 
		self.nroCiclo=0
		# EL dispatcher es para los eventos que seran producidos!
		self.dispatcher=dispatcher
		# Se mantienen las seniales que se notificaran
		self.seniales={}

	# RedDeSemaforos.getNroCicloActual()	
	def getNroCicloActual(self):
		""" Metodo getter para el atributo 'nroCiclo'.
			@return: Numero de ciclo actual.
			@rtype: Integer."""
		return self.nroCiclo

	# RedDeSemaforos.setNroCicloActual()	
	def setNroCicloActual(self,nroCiclo):
		""" Metodo setter para el atributo 'nroCiclo'."""
		self.nroCiclo=nroCiclo

	# RedDeSemaforos.agregarGenerador()
	def agregarGenerador(self,gen):
		""" Este metodo asocia un generador de trafico con el evento de cambio de ciclo de la redDeSemaforos. Asi, cuando ocurra
		un evento de cambio de ciclo, se notificara al generador de trafico que actualizara su nro de ciclo actual.
		@param gen: generador de trafico
		@type gen: GeneradorTrafico
		"""
		# Se agrega el tipo de senial que recibe cada generador (el nombre de la viaMultiple sobre la que 
		# genera el trafico)
		nombreEvento="cambio_ciclo_"+str(gen.getViaMultiple().getNombre())
		self.seniales[gen.getViaMultiple().getNombre()]=nombreEvento
		# 
		# Se asocia el nombre del evento que se va a producir con el metodo de la referencia a "generadorTrafico",
		# indicando que solamente "Semaforos" sera el objeto que debera enviar
 		# ese tipo de seniales y que el generadorVia debera llamar a manejadorTemporizar() cuando
 		# la senial venga de este objeto!
 		# 
 		self.dispatcher.connect( gen.manejadorCambioCiclo,signal=nombreEvento, sender=self)
 
	# RedDeSemaforos.informarAGeneradores()
	def informarAGeneradores(self):
		""" Este metodo informa a los generadoresTrafico de cada una de las viasMultiples que 
			se ha producido un cambio de ciclo.
		"""
		# Se recorere la col. de generadores para informar sobre el cambio
		for nombreViaGenerador,nombreEvento in self.seniales.iteritems():
			logging.debug("Avisando a via %s del cambio de ciclo " % nombreViaGenerador)
			logging.debug("")
			self.dispatcher.send(signal=nombreEvento,sender=self,mensajero=self)
		logging.debug("Se notifico a todas las vias!! ")
		logging.debug("")

	def getCantCiclos(self):
		""" Metodo getter para el atributo 'cantCiclos'
			@return: cantidad de ciclos maxima
			@rtype: Integer
		"""
		return self.cantCiclos

	def getRedPetri(self):
		""" Metodo getter para el atributo 'redPetri'
			@return: la red de Petri que representa a la red de semaforos.
			@rtype: PetriNet
		"""
		return self.redPetri

	# redDeSemaforos.getSemaforos()
	def getSemaforos(self):
		""" Metodo getter que retorna el diccionario de semaforos que estan en la RedDeSemaforos.
			@return: Coleccion de semaforos
			@rtype: Diccionario
		"""
		return self.semaforos

	# redDeSemaforos.getSemaforo(nombre)
	def getSemaforo(self,nombre):
		""" Metodo getter que retorna un semaforo segun su nombre.
			@param nombre: nombre del semaforo
			@type nombre: String
			@return: Coleccion de semaforos
			@rtype: Diccionario
		"""
		return self.semaforos[nombre]

	# RedDeSemaforos.run()
	def run(self):
		""" Este metodo recorre la RP de la red de semaforos, segun el orden establecido en el paper (almacenado como diccionario, donde la clave
			determina el orden a ejecutar y el valor es nombre de la transicion), y temporiza cada transicion. 
			El recorrido de todas las transiciones como lo especifica el paper, se repite tantas veces como lo haya especificado el 
			usuario con la cantidad de ciclos. Este recorrido de todas las transiciones de la red de semaforos,
			se denomina ciclo de tiempo o CT en el paper.

			Informacion adicional sobre los CTs:
				-El plan de tiempos comienza en la fase "I6", con el semaforo del Link 1 en verde.
				-Los ciclos de tiempo (CT's) comienzan se miden desde el inicio del ciclo (dado un ciclo K, ni(k)
				se mide como la cant. de vehiculos que se encuentran al comienzo del ciclo K en el LINK 1).
				ESTO SIGNIFICA QUE LOS DATOS DEL CICLO 2, por ejemplo, se van a medir antes del inicio del ciclo 2.
				-Los ciclos de tiempo terminan en la fase "I5".
		"""
		logging.debug("==================INICIO de RedSemaforos.temporizar() ==================")
		logging.debug("Maxima cant. de ciclos="+str(self.cantCiclos))
		logging.debug("")
		# Se espera a que todas las viasMultiples esten listas para recibir las notificaciones!
		# 
		while not self.simulacion.estaTodoListo():
			logging.debug("Esperando a los GeneradoresTrafico------------------------------->>>>>")
			logging.debug("")
		logging.debug("Despues de simulacion.estaTodoListo()...")
		logging.debug("")
		while self.getNroCicloActual() <= self.cantCiclos-1:
			if self.getNroCicloActual()==0:
				# Se actualiza el nroCicloActual del semaforo asi comienza en NROCICLO=1.
				self.setNroCicloActual(self.getNroCicloActual()+1)
				self.informarAGeneradores()
			logging.debug("RedDeSemaforos CICLO DE SEMAFORO : "+str(self.nroCiclo))
			logging.debug("")
			for clave,nombreTransicion in self.ordenDisparoCiclos.iteritems():
				# Si es la transicion que comienza un nuevo ciclo, se incrementa el nroCiclo.
				if nombreTransicion =="t29":
					logging.debug("Se entro al if: nombreTransicion="+str(nombreTransicion)+"; self.getNroCicloActual()="+str(self.getNroCicloActual()))
					self.setNroCicloActual(self.getNroCicloActual()+1)
					logging.debug("Se incremento el nroCiclo!!!")
					logging.debug("")
					self.informarAGeneradores()
				# if self.getNroCicloActual() > self.cantCiclos:
				if self.getNroCicloActual() >= self.cantCiclos:
					break
				self.redPetri.transition(nombreTransicion).temporizar()
				logging.debug("ordenDisparoCiclos: clave="+str(clave)+"; nombreTransicion: "+str(nombreTransicion)+
					"; nroCiclo: "+str(self.getNroCicloActual()))
				logging.debug("")
		logging.debug("")
		logging.debug("==================FIN de RedSemaforos.temporizar() ==================")
		#Se detiene la simulacion una vez que los ciclos de semaforos transcurrieron
		self.simulacion.detener()
		logging.debug ("Simulacion detenida!")
		logging.debug("")

	# RedDeSemaforos.crearRP()
	#
	def crearRP(self,dicc):
		""" Este metodo encarga de generar la RP a partir de un diccionario con las especificaciones de la misma.
			Para ello, se pasa por parametro un arreglo de diccionarios que mantiene el tipo de elemento a agregar ("transicion" o "lugar")
			y las caracteristicas del mismo. En el caso de la transicion, se brindan los lugares de entrada y salida de la misma y,
			como elemento que se produce en cada lugar siempre se toma que son objetos vehiculos. Los tipos "Transicion" en el diccionario
			tienen ademas el campo "posicion", que permite determinar el recorrido a seguir en la RP cuando se disparan las transiciones.
			
			Un ejemplo de especificacion para dos lugares y una transicion que los une es el siguiente:
 			{ "tipo":"lugar", "nombre":"p10", "posicion": { "x": 0, "y": 500} },
				{"tipo":"lugar","nombre":"p11", "posicion": { "x": 100, "y": 500} },
		 		{ "tipo":"transicion", "nombre":"t11", "input_places": [{"nombrelugar" : 'p10', "nombreVariable":"vehiculo"}] ,
		 				"output_places": [{ "nombrelugar": 'p11', "nombreVariable": "vehiculo"}] }, ... }

		 @param dicc: Conjunto de lugares y transiciones para la red de Petri
		 @type dicc: Diccionario
		 @return: La red de Petri de la red de semaforos
		 @rtype: PetriNet
		"""
		red=PetriNet("RedPetriSemaforos") 
		for d in dicc:
			if d["tipo"]== "lugar":
				p=Place(d["nombre"])
				for tok in d["tokens"]:
					p.add(tok)
				red.add_place(p)
			elif d["tipo"]== "transicion":
				#Se crean todas las transiciones con el mismo token, se establece la duracion de la fase
				#  y se agregan los semaforos que la transicion afecta!
				t=RedPetriRodrigo.TransicionTemporizada(d["nombre"])
				t.setDuracionFase(d["duracionFase"])
				nombreSemaforosAsoc=d["semaforosAsociados"]
				for nombreSem in nombreSemaforosAsoc:
					t.agregarSemaforo(self.semaforos[nombreSem])
				red.add_transition(t)
				for lugEntrada in d["input_places"]:
					red.add_input(lugEntrada["nombrelugar"], d["nombre"],Value(91) )
				for lugSalida in d["output_places"]:
					red.add_output(lugSalida["nombrelugar"], d["nombre"], Value(91) )
		return red