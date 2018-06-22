""" Este modulo mantiene el comportamiento relacionado a la red de petri, como agregar un token a un lugar,
	crear la red de petri y generar alternativas ordenadas de disparo."""

from utilidades.constantes import CONSTANTES_LAYOUT
from utilidades.unidades import *

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

from streamset import *
import logging
from vehiculos import *


def agregarToken(self,nombreLug,imagenVehiculo):
	""" Agrega un token en un lugar determinado de la red de Petri.
		@param nombreLug: Nombre del lugar al que se le agregara un token tipo vehiculo
		@type nombreLug: String
		@param imagenVehiculo: Path a la imagen que representara al vehiculo.
		@type imagenVehiculo: String """
	lugRP=self.redPetri.place(nombreLug)
	v=Vehiculo(self._generarIdVehiculo(),imagenVehiculo,lugRP,self,1)		
	#EL vehiculo mantiene una referencia a la "viaOrigen" que lo genero.
	self.redPetri.place(nombreLug).add(v)

#ViaMultiple.crearRP()
def crearRP(self,dicc,viaMult,nombreVia):
	""" Este metodo tiene como objetivo de generar la red de Petri con un diccionario de elementos.
		Para ello se pasa un arreglo de diccionarios que mantiene el tipo de elemento a agregar ya sea "transicion" o "lugar").
		En el caso de los lugares, el diccionario mantiene el nombre del lugar en la red de Petri, la posicion
		que ocupa este en el escenario y si este es un lugar fisico en la via multiple de la simulacion, o si 
		es un lugar que se emplea para interconectarse con la red de Petri del semaforo.
		Con respecto a la transicion, se brindan los lugares de entrada y salida de la misma y
		como elemento producido por las transiciones de salida,se toma que estos son objetos Vehiculo.
		Los tipos "Transicion" en el diccionario tienen ademas el campo "posicion", que permite determinar
		el recorrido a seguir en la RP cuando se disparan las transiciones.

		Un ejemplo de la organizacion de un diccionario que recibe este metodo es el siguiente:
		{ "tipo":"lugar", "nombre":"p10", "posicion": { "x": 0, "y": 500}, "enViaCirculacion":True },
			{"tipo":"lugar","nombre":"p11", "posicion": { "x": 100, "y": 500} },
				{ "tipo":"transicion", "nombre":"t11", "input_places": [{"nombrelugar" : 'p10', "nombreVariable":"vehiculo"}] ,
					"output_places": [{ "nombrelugar": 'p11', "nombreVariable": "vehiculo"}] }, ... }


		@param dicc: Descripcion de los lugares y las transiciones que describen la red de Petri de la via
		@type dicc: Diccionario
		@param viaMult: Referencia a la via multiple
		@type viaMult: ViaMultiple
		@param nombreVia: Nombre de la via multiple
		@type nombreVia: String
		@return: Red de petri
		@rtype: PetriNet """
	red=PetriNet("RedPetriTrafico") 
	#Se indica la vm a la que pertence la RP
	red.setViaCirculacion(viaMult)
	for d in dicc:
		if d["tipo"]== "lugar":
			p=Place(d["nombre"])
			#Se crea la cuadricula del lugar y se la agrega
			# a la RP.
			pos=d["posicion"]
			# Se obtiene el ancho y alto de la cuadricula.
			# 
			ancho=CONSTANTES_LAYOUT[nombreVia]["ANCHO"]
			alto=CONSTANTES_LAYOUT[nombreVia]["ALTO"]
			# Se crea la cuadricula con la posicion (x,y) el ancho, alto y el nombre
			# del lugarRP que representa.
			cuad= Cuadricula(pos["x"],pos["y"],ancho,alto,d["nombre"])
			
			if d["enViaCirculacion"]==True:
				p.setEnViaCirculacion(True)
				p.setCuadricula(cuad)
				#Al lugar se la asigna la via de circulacion a la que pertence!
				p.setViaCirculacion(self)

			#Se crea el streamSet del lugar y se lo setea
			st=StreamSet(d["dicStreamSet"])
			p.setStreamSet(st)
			#Si el lugar tiene esta clave es un lugar de inicio y debe
			#contener el path del icono que debe usar el vehiculo.
			if d.has_key("pathIcono"):
				p.setPathIcono(d["pathIcono"])
			red.add_place(p)
		elif d["tipo"]== "transicion":
			t=RedPetriRodrigo.Transition(d["nombre"])
			red.add_transition(t)
			for lugEntrada in d["input_places"]:
				red.add_input(lugEntrada["nombrelugar"], d["nombre"],Variable(lugEntrada["nombreVariable"]))
			for lugSalida in d["output_places"]:
				red.add_output(lugSalida["nombrelugar"], d["nombre"],  Variable(lugSalida["nombreVariable"]))
	return red	

# viaMultiple.generarAltOrdenadas()
def generarAltOrdenadas(self,diccAlternativasDisparo):
	""" Este metodo genera las alternativasDeDisparo con las transiciones y las asigna
		a la red de Petri. Recibe un diccionario de arreglos de la forma: 
			d={ 
				1:[t11,t12],
				....
			}
		Donde la clave es la posicion de recorrido y el valor es un arreglo con las transiciones que pueden
		dispararse en ese lugar.

		@param diccAlternativasDisparo: Coleccion con los datos para generar las alternativas de disparo
		@type diccAlternativasDisparo: Diccionario"""
	alternativasOrdenadas={}
	#Se guardan en un diccionario las alternativas de disparo con la posicion de recorrido como clave.
	for clave,transiciones in diccAlternativasDisparo.iteritems():
		#Por cada posicion se recorre el arreglo con los nobmres de las transiciones y se las obtiene de la RP
		transObtenidas=[]	
		for nombreTrans in transiciones:
			t=self.redPetri.transition(nombreTrans)
			transObtenidas.append(t)
		#Se crea el objeto alternativasDeDisparo con el arreglo de transiciones y se
		alternativa=AlternativaDeDisparo(transObtenidas)
		alternativasOrdenadas[clave]=alternativa
	logging.debug("==================== viaMultiple.generarAlternativasOrdenadas() ============================== ")	
	logging.debug("")
	logging.debug("MOSTARNDO ALTERNATIVAS PARA LA ViaMultiple: "+str(self.nombre))
	logging.debug("")
	for clave,alt in alternativasOrdenadas.iteritems():
		logging.debug(" clave: "+str(clave)+"; alternativaOrdenada con transiciones: "+str(alt.getTransicionesAlt()))
		logging.debug("")
	#Una vez agregadas todas las transiciones se setea en la RP
	self.redPetri.setAlternativasDeDisparo(alternativasOrdenadas)
