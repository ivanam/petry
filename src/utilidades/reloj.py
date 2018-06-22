""" Este modulo encapsula la clase reloj utilizada como utilidad de la simulacion."""
import time,logging,threading
from utilidades.unidades import Posicion
class Reloj(threading.Thread):
	""" Esta clase encapsula el comportamiento y los datos del
		reloj que se muestra durante toda la ejecucion de la simulacion de trafico."""
	def __init__(self,posX=650,posY=50,tamanioLetra=26):
		""" Contructor de la clase Reloj.

			@param nombre: Nombre del reloj(opcional)
			@type nombre: String
			@param posX: Coordenada X del reloj en la vista
			@type posX: Integer
			@param posY: Coordenada Y del reloj en la vista
			@type posY: Integer
			@param tamanioLetra: Tamanio de la letra del reloj en la vista(opcional)
			@type nombre: Integer """
		threading.Thread.__init__(self,name="Thread-Reloj")
		self.minutos=self.segundos=self.tiempoTranscurrido=0
		self.debeContinuar=True
		self.posicion=Posicion(posX,posY)
		self.tamanioLetra=tamanioLetra

	def getTamanioLetra(self):
		""" Metodo getter para el atributo 'tamanioLetra' .
			@return: El tamanio de la letra
			@rtype: Integer	"""
		return self.tamanioLetra
		
	def getMinutos(self):
		""" Metodo getter para el atributo 'getMinutos' .
			@return: Los minutos transcurridos desde el inicio de la simulacion
			@rtype: Integer	"""
		return self.minutos

	def getSegundos(self):
		""" Metodo getter para el atributo 'segundos' .
			@return: Los segundos transcurridos desde el inicio de la simulacion
			@rtype: Integer	"""
		return self.segundos

	def getPosicion(self):
		""" Metodo getter para el atributo 'tamanioLetra' .
			@return: Posicion del reloj en la vista
			@rtype: Posicion	"""
		return self.posicion

	def detener(self):
		""" Este metodo detiene el thread reloj. """
		logging.debug("Reloj detenido!")
		logging.debug("")
		self.debeContinuar=False

	# Reloj.run()
	def run(self):
		""" Este metodo se encarga de controlar la ejecucion del reloj para que esta continue hasta que la simulacion
		finalice. Ademas, actualiza los atributos: segundos, minutos y tiempo transcurridos del reloj. """
		while self.debeContinuar:
			# Se duerme el reloj
			time.sleep(1)
			print "Se desperto reloj!"
			print ""
			self.segundos+=1
			self.modificado=True
			# Este campo es solo para conocimiento del programador.
			self.tiempoTranscurrido+=1
			if self.segundos>=60:
				self.segundos=0
				self.minutos+=1
			if self.minutos>=60:
				self.minutos=self.segundos=0
