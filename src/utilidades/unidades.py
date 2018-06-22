"""Este modulo define las unidades como Posicion o Cuadricula utilizadas para ubicar los elementos en la vista.
Tambien se define la unidad para agrupar dos alternativas de disparo. """
import random
class Posicion(object):
	""" Esta clase representa la posicion de un elemento dentro de la simulacion. Estos objetos son los vehiculos,
	las cuadriculas,y los semaforos."""
	def __init__(self,x,y):
		"""	Constructor de la clase Posicion.
			@param x: coordenada x del elemento
			@type x: Integer
			@param y: coordenada y del elemento
			@type y: Integer
		"""
		self.x=x
		self.y=y

	def getX(self):
		"""	Metodo getter del atributo 'x'"""
		return self.x

	def getY(self):
		"""	Metodo getter del atributo 'y'"""
		return self.y

class Cuadricula(object):
	""" La cuadricula es el objeto que mantiene la posicion actual del vehiculo dentro de  un carril de la simulacion. Cada carril,
		se divide por cuadriculas en una posicion determinada, que son ocupadas por vehiculos. 
		EL lugar (Place) en la Red de Petri mantiene la referencia a la cuadricula y el vehiculo mantiene una referencia al 
		lugar en la RP en la que esta ubicado.Por lo tanto, cuando la transicion se dispare debe indicar al
		vehiculo (si no existe otro vehiculo en la cuadricula siguiente) que avance, obteniendo la referencia al lugar de salida
		desde la transicion y la misma se pasara por argumento al metodo vehiculo.avanzar(). Entonces, el vehiculo solamente 
		necesitara cambiar su lugarRP por la que se le pase por argumento.

		Informacion adicional:
			-La cuadricula se crea en el metodo "crearRP()" y sus atributos son prefedinidos en el diccionario que define
				la estructura de la RP. Se debe pasar como atributos "posX" y "posY" del lugar de la RP.
			-Al momento de dibujar el vehiculo se debera solicitar su lugarRP y, a partir de este obtener
			la cuadricula y la posicion."""
	def __init__(self,posX,posY,ancho,alto,nombreLugarRP):
		""" Metodo constructor de la clase cuadricula.
			@param posX: Posicion X de la cuadricula
			@type posX: Integer
			@param posY:Posicion Y de la cuadricula
			@type posY: Integer
			@param ancho: Ancho de la cuadricula
			@type ancho:Integer
			@param alto: Alto de la cuadricula
			@type alto:Integer
			@param nombreLugarRP: Nombre del lugar en la red de Petri que representa la cuadricula.
			@type nombreLugarRP: String """
		self.posicion=Posicion(posX,posY)
		self.ancho=ancho
		self.alto=alto
		self.nombre=nombreLugarRP

	def getNombre(self):
		""" Metodo getter del atributo 'nombre'.
			@return: Nombre del lugar representado por la cuadricula
			@rtype: String """
		return self.nombre

	def getPosicion(self):
		""" Metodo getter del atributo 'posicion'.
			@return: Posicion de la cuadricula
			@rtype: Posicion """
		return self.posicion

	def getAncho(self):
		""" Metodo getter del atributo 'nombre'.
			@return: Ancho de la cuadricula
			@rtype: Integer """
		return self.ancho

	def getAlto(self):
		""" Metodo getter del atributo 'nombre'.
			@return: Alto de la cuadricula
			@rtype: Integer """
		return self.alto

class AlternativaDeDisparo(object):
	"""Esta clase representa una alternativa de disparo, la que consiste en agrupar dos o mas transiciones en la red de Petri
		que pueden ser disparadas en el mismo momento. Esta clase es instanciada por la red de Petri para cada una de las alternativas
		del conjunto de alternativas de disparo que mantiene la simulacion. Este conjunto de alternativas de disparo, es utilizado
		cuando se invoca al metodo de "temporizar()" en la RP, que efectua la iteracion de la coleccion de objetos AlernativaDeDisparo 
		y las dispara en el orden definido en esta coleccion.
		La seleccion de la transicion se realiza de manera aleatoria, y se mantiene un registro de las transiciones que fueron seleccionadas,
		por lo que no se selecciona nunca la misma transicion dos veces.
		Siempre se realiza un disparo aleatorio entre dos transiciones,
		con el objetivo de simular la aleatoriedad de la circulacion de vehiculos por un carril y los cambios de carril.
	"""
	def __init__(self,listaTransiciones):
		""" Constructor  de la clase AlternativaDeDisparo.
			@param listaTransiciones: Lista de nombres de las transiciones de la red de Petri que son alternativas.
			@type parametro: List """
		self.transiciones=listaTransiciones
		self.nrosTransicionesMarcadas=[]

	def getTransicionesAlt(self):
		""" Metodo getter de las transiciones alternativas.
			@return: Listado de nombres transiciones alternativas
			@rtype: List """
		return self.transiciones
	
	def elegirTransicionAleatoria(self):
		""" Este metodo retorna una transicion aleatoria de un conjunto de transiciones
			y si no existe ninguna disponible ,retorna "None".
			@return: Un nombre de transicion.
			@rtype: String. """
		result=random.randint(0,len(self.transiciones)-1)
		while result  in self.nrosTransicionesMarcadas:
			result=random.randint(0,len(self.transiciones)-1)
		self.nrosTransicionesMarcadas.append(result)
		return self.transiciones[result]

	def resetearAlternativas(self):
		""" Resetea el arreglo de transiciones que se seleccionaron previamente, para hacer una nueva
			seleccion."""
		self.nrosTransicionesMarcadas=None
		self.nrosTransicionesMarcadas=[]

	def estanAltAgotadas(self):
		""" Este metodo determina si aun quedan transiciones alternativas para seleccionar.
			@return: Valor que determina si existen transiciones alternativas.
			@rtype: Boolean"""
		if len(self.transiciones) == len(self.nrosTransicionesMarcadas):
			self.resetearAlternativas()
			return True
		else:
			return False
