""" Este modulo define la clase Vehiculo de la simulacion."""
class Vehiculo(object):
	""" Esta clase representa los atributos de un vehiculo que circula por una via. Cada vehiculo que ingresa a la interseccion
		mantiene el lugar en la red de Petri (lugarRP) en donde se encuentra, el color del mismo que variara segun la viaMultiple
		en que se encuentre y la viaMultiple desde donde se haya generado.
	"""
	def __init__(self,idVehiculo,imagen,lugarRP,viaMultipleDeOrigen,nroCicloGenerado):
		""" Constructor de la clase vehiculo.
			@param idVehiculo: Identificador unico del vehiculo
			@type idVehiculo: String
			@param imagen: Atributo que especifica cual es el path relativo para buscar la imagen del vehiculo.
			@type imagen: String
			@param lugarRP: Lugar de la RP donde se encuentra el vehiculo.
			@type lugarRP: Place
			@param viaMultipleDeOrigen: Via mutliple que representa la via a la que pertenece el generadorTrafico que
											genero el vehiculo.
			@type viaMultipleDeOrigen: ViaMultiple
			@param nroCicloGenerado: Numero de ciclo en el que se genero el vehiculo.
			@type nroCicloGenerado: Integer
		"""
		self.idVehiculo=idVehiculo
		self.lugarRP=lugarRP
		self.imagen=imagen
		#El vehiculo establece la viaOrigen (viaMultiple) que lo genero, de manera que siempre pueda saber
		#los cambios de via validos que tiene incluso si se encuentra en un lugar de otra via.
		self.viaOrigen=viaMultipleDeOrigen
		#EL color del vehiculo y el nro de carril se utilizan para 
		#guardar el estado que tenia el vehiculo y poder dibujar
		# el color que corresponde al flujo original por el que iba,
		# cuando entra en otra viaMultiple.
		color=self.lugarRP.getStreamSet().obtenerColorStream(self.viaOrigen.getNombre())
		self.colorVehiculo=color
		self.nroCicloGenerado=nroCicloGenerado

	# vehiculo.getPathImagen()
	def getPathImagen(self):
		""" Metodo getter para el atributo 'imagen' 
			@return: path de la imagen
			@rtype: String
			"""
		return self.imagen

	def getNroCicloGenerado(self):
		""" Metodo getter para el atributo 'nroCicloGenerado' 
			@return: numero de ciclo en que el vehiculo fue generado
			@rtype: Integer
			"""
		return self.nroCicloGenerado

	# Vehiculo.actualizarColores()
	def actualizarColores(self,sigLugar):
		""" Se actualiza la combinacion de colores del vehiculo.
			@param sigLugar: El siguiente lugar de la red de Petri
			@type sigLugar: Place
		"""
		#Si las vias de circulacion son distintas, el color del vehiculo no debe actualizar
		#ya que aunque se mueva por otra via debe representar ese flujo.
		nombreViaOrigen=self.getViaOrigen().getNombre()
		# Se tiene que obtener el nro de carril y el limite de flujo del lugarActual (Los limites de flujo
		#son nombres de transiciones para el caso de los lugares que tienen un limite).
		color=sigLugar.getStreamSet().obtenerColorStream(nombreViaOrigen)
		self.setColores(color)
		
	# Vehiculo.setColores(tuplaColores)
	def setColores(self,color):
		""" Metodo setter para el atributo 'colorVehiculo'.
			@param color: Tupla de valores RGB
			@type color: Tupla
		"""
		self.colorVehiculo=color

	# Retorna una tupla con la combinacion RGB actual del vehiculo
	# vehiculo.getColores()
	def getColores(self):
		""" Metodo setter para el atributo 'colorVehiculo'.
			@param color: Tupla de valores RGB
			@type color: Tupla
		"""
		return self.colorVehiculo

	# vehiculo.getViaOrigen()
	def getViaOrigen(self):
		""" Metodo getter para el atributo 'viaOrigen'.
			@param color: 
			@type color: Tupla
		"""
		return self.viaOrigen

	# vehiculo.getViaOrigen()
	def getIdVehiculo(self):
		""" Metodo setter para el atributo 'idVehiculo'."""
		return self.idVehiculo
    
    # vehiculo.getViaCirculacion()
	def getViaCirculacion(self):
		""" Metodo getter para el atributo 'viaCirculacion'.
			@return: Via de circulacion en la que se encuentra el vehiculo actualmente
			@rtype: ViaMultiple
		"""
		return self.viaCirculacion


	# Vehiculo.getCuadricula()
	# Se obtiene la Cuadricula con las dimensiones en que esta ubicado un lugarRP
	# 
	def getCuadricula(self):
		""" Este metodo obtiene la cuadricula en que se encuentra localizada fisicamente en el escenario,
			un lugar en la red de Petri.
			@return: La cuadricula que corresponde al lugar de la red de Petri, en que se encuentra un vehiculo.
			@rtype: ViaMultiple
		"""
		return self.lugarRP.getCuadricula()

	# Vehiculo.avanzarALugar()
	def avanzarALugar(self,lug):
		""" Este metodo mueve el vehiculo hacia otro lugar en la red de Petri.
			@param lug: El lugar de la red de Petri
			@type lug: Place
		"""
		self.lugarRP=lug

	# Vehiculo.getLugarRP()
	def getLugarRP(self):
		""" Metodo getter para un lugar de la red de Petri.
			@return: LugarRP
			@rtype: Place
		"""
		return self.lugarRP



