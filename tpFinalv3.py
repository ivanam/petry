""" Este modulo define la clase Main."""
#COMANDO DE PRUEBA -->
# sudo python tpFinalv3.py > log.txt 2>&1
#

# Pydoc TAGS USADOS PARA DOCUMENTAR -->
# http://effbot.org/zone/pythondoc.html

import sys
sys.path.append("/home/rodrigo/FUNDAMENTOS-TEORICOS-INFORMATICA/TP-Final/TP-Final-2D")
##########################################################################################
############################## Imports de modulos del programador  y otros ###############
##########################################################################################
import threading
import logging
import os,signal
import sys

#Imports de modulos propios de la simulacion.
from utilidades.constantes import *
from utilidades.unidades import *
from modelo.semaforos import *
from modelo.viamultiple import *
from utilidades.decodificadorJson import *
from vista.vista import *
from modelo.simulacion import *
from utilidades.reloj import *

##########################################################################################
############################## Imports de PyDispatcher (EventDispatcher) ###################
##########################################################################################
import copy
import random
import weakref
import pygame
from pygame.locals import *
##########################################################################################
############## Configuracion del modulo de logging para los diferentes hilos ##############
##########################################################################################
import logging
logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-9s) %(message)s',)

# MENU DE OPCIONES:
# 	-00--> INTERSECCION
# 	-01--> LINK1
# 	-02--> LINK2-LINK3
# 	-04--> LINK4
# 	-05--> LINK6-LINK5-PARTE 1
# 	-06--> LINK6-LINK5-PARTE 2
class Main(object):
	""" Clase principal encargada de configurar la simulacion e iniciarla."""
	def imprimirFecha(self):
		logging.debug( "++++++++++++++++++++++++++++++++++++++++++++++++++++")
		logging.debug(time.strftime("Dia: %d/%m/%Y -- Hora: %H:%M:%S ")) 
		logging.debug("++++++++++++++++++++++++++++++++++++++++++++++++++++")
		logging.debug("")

	def esCadVacia(self,cad):
		""" Este metodo determina si una cadena se encuentra vacia.
			@param cad: Cadena a evaluar
			@type cad: String
			@return: Valor indicando si una cadena se encuentra vacia.
			@rtype: Boolean"""
		if bool(cad.strip())==False:
			return True
		return False

	def leerEsquema(self,nombreVia):
		""" Este metodo lee un archivo Json que corresponde a un esquema y retorna un diccionario,
			producto de haber parseado ese archivo json.
			@param nombreVia:Nombre de la via
			@type nombreVia: String """
		esquema=""
		if nombreVia=="viaX":
			esquema="EsquemaViaX.json"
		elif nombreVia=="viaYAsc":
			esquema="EsquemaViaYAsc.json"
		elif nombreVia=="viaYDesc":
			esquema="EsquemaViaYDesc.json"			
		print "Leyendo esquema %s de la via: %s" % (esquema,nombreVia)
		print ""
		listaElementos=cargarJson(esquema,"modelo/json/esquema")
		print "En leerEsquema(), archivo %s json cargado!" % esquema
		print ""
		print " ======================================================================================= "
		print "El archivo Json leido para %s es: %s" % (nombreVia,listaElementos)
		print " ======================================================================================= "

		for dic in listaElementos:
			if dic["tipo"]=="lugar":
				x=dic["posicion"]["x"]
				y=dic["posicion"]["y"]
				tuplaColores=()
				if isinstance(dic["posicion"]["x"],str):
					x=convertirExpresion(dic["posicion"]["x"])
				if isinstance(dic["posicion"]["y"],str):
					y=convertirExpresion(dic["posicion"]["y"])
				# Se convierten las expresiones de Python almacenadas como String en json. Siempre se verifica si el diccionario
				# tiene esas claves, ya que las transiciones no poseen algunos atributos.
				for nombreViaStream,expresion in dic["dicStreamSet"].iteritems():
					dic["dicStreamSet"][nombreViaStream]=convertirExpresion(expresion)

				if dic.has_key("pathIcono"):
					print "Convirtiendo expresion:  %s" % dic["pathIcono"]
					print ""
					dic["pathIcono"]=convertirExpresion(dic["pathIcono"])

				dic["posicion"]["x"]=x
				dic["posicion"]["y"]=y

		return listaElementos

	def cargarEsquemas(self):
		""" Este metodo carga los esquemas de las redes de Petri en un diccionario
			@return: Esquemas de las vias multiples
			@rtype: Diccionario """
		listaEsquemaX=self.leerEsquema("viaX")
		listaEsquemaYDesc=self.leerEsquema("viaYDesc")
		listaEsquemaYAsc=self.leerEsquema("viaYAsc")
		global dicEsquemas
		dicEsquemas["viaX"]=listaEsquemaX
		dicEsquemas["viaYDesc"]= listaEsquemaYDesc
		dicEsquemas["viaYAsc"]=listaEsquemaYAsc

		
	def cargarLugaresIniciales(self,nombre):
		""" Este metodo retorna un diccionario leido del archivo json en json/esquema, dado un nombre escenario
			@param nombre: Nombre de escenario que se cargara
			@type nombre: String 
			@return: Conjunto de valores para configurar el diccionario.
			@rtype: Diccionario """

		rutaEscenario="modelo/json/esquema/"+nombre
		dicCompleto=cargarJson("LugaresAInicializar.json",rutaEscenario)
		# Se obtiene solo la parte del diccionario que se desea retornar
		myDic= dicCompleto[nombre]
		# Se convierten todas las expresiones Python en formato String que hacen referencia a la constante
		# "tiposToken".
		for clave,valor in myDic.iteritems():
			valor["imagenVehiculos"]=convertirExpresion(valor["imagenVehiculos"])
		resultado={}
		resultado[nombre]=myDic
		logging.debug("Los lugares iniciales convertidos para el escenario %s son: %s" % (nombre,resultado))
		logging.debug("")
		return resultado


	def transformarDicTraficoPredefinido(self,dicTraficoPred):
		""" Este metodo recorre un diccionario de trafico predefinido, donde las claves son los 
			numeros de ciclo y un diccionario con los tiempos de las fases son la respuesta.
			@param dicTraficoPred: Diccionario de elementos
			@type dicTraficoPred: Diccionario
			@return: Valores de trafico predefinido con asignaciones evaluadas
			@rtype: Diccionario """
		dicNuevo={}
		for nroCiclo,dicTiemposCiclo in dicTraficoPred.iteritems():
			for nombreFase,dicFases in dicTiemposCiclo.iteritems():
				dicFases["duracionTotalFase"]=convertirExpresion(dicFases["duracionTotalFase"])
			dicNuevo[int(nroCiclo)]=dicTiemposCiclo
		return dicNuevo

	def cargarTraficoPredefinido(self,nombreEscenario):
		""" Este metodo lee las configuraciones de trafico predefinido de los archivos json,
			para las tres vias multiples.
			@param nombreEscenario: Nombre del escenario que se cargara
			@type nombreEscenario: String
			@return: El trafico predefinido para las tres vias
			@rtype:  Diccionario """
			#EL diccionario TRAFICO_PREDEFINIDO indexa por NOMBRE DE ViaMultiple y cada via multiple mantiene
			# en cada nro de ciclo, el intervalo de ingreso de vehiculos en cada fase de semaforo.
			#
			# -Cada ViaMultiple mantiene: 
			#							* El intervalo de ingreso de trafico en ambas vias de entrada.(FTj) 
			#							* La duracion total de una fase roja o amarilla-verde en una viaMultiple.
			#
			# Asi dividiendo el intervalo de ingreso de trafico sobre la duracion total de una fase en una viaMultiple
			# se puede calcular la cantidad de repeticiones que una temporizacion se puede hacer.El trafico siempre 
			# ingresa por ambos carriles.
		rutaEscenario="modelo/json/esquema/"+nombreEscenario
		logging.debug("Ruta para cargar el escenario: %s" % rutaEscenario)
		logging.debug("")
		dicTraficoViaX=cargarJson("TraficoPredefinidoViaX.json",rutaEscenario)
		global dicTraficoPredefinido
		dicTraficoPredefinido["viaX"]=self.transformarDicTraficoPredefinido(dicTraficoViaX["viaX"])
		dicTraficoViaYDesc=cargarJson("TraficoPredefinidoViaYDesc.json",rutaEscenario)
		dicTraficoPredefinido["viaYDesc"]=self.transformarDicTraficoPredefinido(dicTraficoViaYDesc["viaYDesc"])
		dicTraficoViaYAsc=cargarJson("TraficoPredefinidoViaYAsc.json",rutaEscenario)
		dicTraficoPredefinido["viaYAsc"]=self.transformarDicTraficoPredefinido(dicTraficoViaYAsc["viaYAsc"])

	# Descripcion de la distribucion de las transiciones en la red de semaforos con los estados de los semaforos:
	####################### Transiciones del semaforo del LINK1 #######################
	# COLOR VERDE!
	# t22=I6
	# COLOR AMARILLO!
	# t23=I7
	# COLOR ROJO!
	# t24=I8
	####################### Trueransiciones del semaforo del LINK6 #######################
	# COLOR VERDE!
	# t25=I1
	# COLOR AMARILLO!
	# t26=I2
	####################### Transiciones del semaforo del LINK3 #######################
	# COLOR VERDE!
	# t27= I1+I2 +I3 (I3 = 1 seg.)
	# DICC_FASES["i3"]
	# COLOR AMARILLO!
	# t28=I4
	###################### Transiciones extra (t29 y transiciones compartidas) ###################################
	# COLOR ROJO LINK3 
	# COLOR ROJO LINK6
	# t29=I5
	def cargarRedSemaforos(self):
		""" Este metodo se encarga de cargar el archivo json con el esquema de la red de semaforos.
			@return: Esquema de red de semaforos convertido a coleccion de Python
			@rtype: List """
		listaRedSemaforos=cargarJson("EsquemaRedDeSemaforos.json","modelo/json/esquema")
		for dic in listaRedSemaforos:
			if dic["tipo"]=="transicion":
				dic["duracionFase"]=convertirExpresion(dic["duracionFase"])
		return listaRedSemaforos


	def cargarConfiguracion(self):
		""" Este metodo carga la configuracion de los archivos json que son necesarias para la simulacion.
			@param dicTraficoPredefinido: Trafico predefinido
			@type dicTraficoPredefinido: Diccionario 
			@param dicTraficoPredefinido: Esquemas de las redes de Petri de las vias multiples
			@type dicTraficoPredefinido: Diccionario
			@return: Esquema de la red de Petri y configuraciones adicionales
			@rtype: Diccionario """

		dicDefinicionesVias={}
		dicDefinicionesVias=cargarJson("definicionViasMultiples.json","modelo/json/esquema")
		nombreVias=["viaX","viaYDesc","viaYAsc"]
		for nombVia in nombreVias:
			dicDefinicionesVias[nombVia]["nodosInicio"]=convertirExpresion(dicDefinicionesVias[nombVia]["nodosInicio"])
			dicDefinicionesVias[nombVia]["nodosFin"]=convertirExpresion(dicDefinicionesVias[nombVia]["nodosFin"])
			dicDefinicionesVias[nombVia]["esquema"]=convertirExpresion(dicDefinicionesVias[nombVia]["esquema"])

			dicDefinicionesVias[nombVia]["alternativasDisparo"]=convertirExpresion(dicDefinicionesVias[nombVia]["alternativasDisparo"])
			dicDefinicionesVias[nombVia]["viasCircHabilitadas"]=convertirExpresion(dicDefinicionesVias[nombVia]["viasCircHabilitadas"])
			dicDefinicionesVias[nombVia]["delayVehiculos"]=convertirExpresion(dicDefinicionesVias[nombVia]["delayVehiculos"])


			print "Fases a registrar: %s " % dicDefinicionesVias[nombVia]["fasesARegistrar"]
			print ""
			if dicDefinicionesVias[nombVia]["fasesARegistrar"].has_key("fase_roja"):
				dicDefinicionesVias[nombVia]["fasesARegistrar"]["fase_roja"]= convertirExpresion(dicDefinicionesVias[nombVia]["fasesARegistrar"]["fase_roja"])
			if dicDefinicionesVias[nombVia]["fasesARegistrar"].has_key("fase_verde_amarilla"):
				dicDefinicionesVias[nombVia]["fasesARegistrar"]["fase_verde_amarilla"]= convertirExpresion(dicDefinicionesVias[nombVia]["fasesARegistrar"]["fase_verde_amarilla"])

			dicDefinicionesVias[nombVia]["traficoPredefinido"]= convertirExpresion(dicDefinicionesVias[nombVia]["traficoPredefinido"])
		return dicDefinicionesVias

	def iniciar(self):
		""" Este metodo instancia la simulacion, la vista, el reloj y establece las relaciones entre ellos. """
		# Se inicializan todas las constantes de pygame.
		pygame.init()
		logging.debug("En main()")
		logging.debug("")
		self.imprimirFecha()


		# Se solicitan el nombre del escenario que el usuario desea simular y la cantidad de ciclos de tiempo
		v=Vista()
		diccDatosUsuario=v.solicitarInformacion()

		#DICCIONARIO DE LUGARES QUE SE DEBEN CARGAR COMO INCIADOS AL MOMENTO DE COMENZAR LA SIMULACION
		# NOTA: Este diccionario es solamente utilizado al comienzo de la simulacion para los escenarios
		# de prueba del paper (escenario 1 y escenario 2). Luego el trafico generado tiene que ser variable,
		# segun la fase en que se encuentre. 
		# Los lugares se inicializan como sigue:
		# 		-Para el Escenario1: el LINK 1 se inicializa con 4 lugares inicializados.
		# 		-Para el Escenario2: ???
		#TODO IMPORTANTE: REVISAR EN EL PAPER QUE LINKS SE REQUIEREN QUE ESTEN INICIALIZADOS PARA 
		# EL SEGUNDO ESCENARIO DE LA SIMULACION!
		#
		# ,"escenario2":{
		# 			"viaX":["","","",""],
		# 			"viaYAsc":["","","",""],
		# 			"viaYDesc":["","","",""],
		# }
		LUGARES_A_INICIALIZAR=self.cargarLugaresIniciales(diccDatosUsuario["nombreEscenario"])
		# Se carga el trafico predefinido para todas las vias
		self.cargarTraficoPredefinido(diccDatosUsuario["nombreEscenario"])

		# Se cargan los esquemas de todas las vias multiples.
		##############################################################################
		# Informacion acerca de la nomenclatura en los esquemas de las redes de Petri: 
		#		-Los identificadores de los lugares se son de la forma: 'p'+<CARRIL>+<NODO_DENTRO_DEL_CARRIL>
		#		i.e: p13_L1, es el lugar 3 del carril 1.
		#		-Los identificadores de las transiciones son de la forma: 't'+<ID_LUGAR_A_DONDE_LLEGAN>.
		# 		-Los nombres de los lugares son: P+ <nro_carril> + <nro_lugar>+"."+<NombreLink>
		# 		con los nombres de los links: {"L1", "L2", "L3","L4","L5","L6"}, siendo estos Link1,Link2, Link3, Link4,
		# 		Link5 y Link6 respectivamente.
		#		-Las transiciones cruzadas se leen t11_22, como la transicion que parte del lugar
		#		'p11'  hacia el lugar 'p22'.
		##############################################################################
		
		self.cargarEsquemas()
		#El diccionario final de la RP mantiene:
		#
		#	-"nodosInicio"/"nodosFin": diccionarios con los  nombres de los nodos de inicio/fin necesarios para la generacion de trafico.
		#	-"esquema": Diccionario con la definicion de los lugares y transiciones de la RP.
		#	-"alternativasDisparo": Diccionario con el orden de disparo de las transiciones de una via de circulacion.
		#	-"sentidoCiculacion": Cadena con el sentido de circulacion de la via (de entre tres posibles).
		#	-"anguloCirculacion": Entero con el angulo de circulacion de los vehiculos en la via.
		#	-"colores": Diccionario con los colores de la via de circulacion (definidos como combinacion RGB)
		diccRPFinal=self.cargarConfiguracion()

		# Se carga la red de semaforos desde el json en disco.
		diccSemaforos=self.cargarRedSemaforos()
		logging.debug("Los semaforos cargados fueron: %s " % diccSemaforos)
		logging.debug("")
		logging.debug("El diccRPFinal es:  %s " % diccRPFinal)
		logging.debug("")

		#Se mantiene un diccionario con la estructura  de la RP del semaforo y un diccionario de alternativas
		# que mantiene el orden del ciclo de las transiciones (ordenadas segun las fases). La estructura del diccionario 
		# de los semaforos es dist. a la de la RP de circulacion de carriles:
		#		-Los lugares no mantienen posiciones
		#		-Los lugares mantienen una lista de tokens [] para indicar si se encuentran marcados o no. Como tokens se utiliza
		#el nro del anio del nacimiento del autor.
		#		-Las transiciones no contienen el atributo "esTransicionCruzada" ya que no son parte de los carriles de circulacion.
		#		-Las transiciones mantienen la "duracionFase".
		#		-Las transiciones tienen un arreglo de "semaforosAsociados" a los que deben informar sobre el cambio de estado siempre
		#que se disparen.
		
		cantCiclosTiempo=0
		#Se incrementa la cantidad de ciclos de tiempo para incluir siempre el primer ciclo.
		cantCiclosTiempo=diccDatosUsuario["cantCiclosTiempo"]+1
		# Se obtiene el nombre del escenario que selecciono el usuario.
		simul=Simulacion(diccRPFinal,diccSemaforos,ordenTransicionesSemaforos,cantCiclosTiempo,
							diccDatosUsuario["nombreEscenario"],LUGARES_A_INICIALIZAR)

		# Se inicia un reloj para actualizar en el escLayer y llevar la cuenta del progreso de la simulacion.
		reloj= Reloj()
		simul.setReloj(reloj)
		reloj.setDaemon(True)
		reloj.start()
		logging.debug("Thread reloj comenzado!")
		logging.debug("")
		# Se asocia la vista con el modelo.
		v.setModelo(simul)
		v.setReloj(reloj)
		v.cargarAreaPorDefecto()
		# Se comienza la ejecucion de la vista
		t1=threading.Thread(target=v.mostrar,name="Thread-Vista")
		t1.start()
		simul.comenzar()
		# Se espera a que termine el thread de la parte grafica.
		t1.join()
		#NOTA: Utilizar este codigo para debuggear el Graficador sin tener que correr la simulacion!
		# dicc={
		# 		0: {'nombreVia': 'viaX', 'nombreLink': 'link1', 'tipoVariable': 'n', 'rangoValores': {1: 9, 2: 5}, 'nombreVariable': 'n(i): Cant. vehiculos en via'}, 
		# 		1: {'nombreVia': 'viaX', 'nombreLink': 'interseccion', 'tipoVariable': 'w', 'rangoValores': {1: 1, 2: 0}, 'nombreVariable': 'w(i): Cant.vehiculos esperando'}, 
		# 		2: {'nombreVia': 'viaYAsc', 'nombreLink': 'link3', 'tipoVariable': 'n', 'rangoValores': {1: 1, 2: 0}, 'nombreVariable': 'n(i): Cant. vehiculos en via'}, 
		# 		3: {'nombreVia': 'viaYAsc', 'nombreLink': 'interseccion', 'tipoVariable': 'w', 'rangoValores': {}, 'nombreVariable': 'w(i): Cant.vehiculos esperando'},
		# 	 	4: {'nombreVia': 'viaYDesc', 'nombreLink': 'link6', 'tipoVariable': 'n', 'rangoValores': {1: 0, 2: 2}, 'nombreVariable': 'n(i): Cant. vehiculos en via'}, 
		# 	 	5: {'nombreVia': 'viaYDesc', 'nombreLink': 'interseccion', 'tipoVariable': 'w', 'rangoValores': {}, 'nombreVariable': 'w(i): Cant.vehiculos esperando'}
		# 	 	}
		# simul.graficarResultados(dicc)

if __name__ == "__main__":
	m=Main()
	m.iniciar()