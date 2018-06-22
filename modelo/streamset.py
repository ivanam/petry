""" Este modulo define la clase StreamSet. """
class StreamSet(object):
	""" Esta clase representa al conjunto de streams de colores que un lugar puede producir, segun la "viaOrigen"
		de la que provenga el vehiculo. """
	def __init__(self,dicStreams):
		""" Constructor del Stramset que acepta un diccionario. Este mantiene el streamSet indexa cada tupla RGB de color
			y usa como clave el nombre de la via de origen del vehiculo.
			Ejemplo del lugar p14:
				dic={ "viaX": mapeoColores["a1"],"viaYDesc": mapeoColores["a3"] }
		"""
		self.colStreams={}
		self.colStreams=dicStreams
	#Este metodo obtiene el color de un stream
	def obtenerColorStream(self,nombreViaOrig):
		""" Este metodo obiene el codigo de un color en RGB para un nombre de viaMultiple.
			La invocacion a obtenerColorStream() se realiza desde la clase vehiculo, cuando se crea una instancia de este y,
			cuando se invoca a actualizarColores(). De esta forma cada vez que se necesite actualizar el color de un vehiculo,
			la responsabilidad se delega al siguiente lugarRP al que el vehiculo se desplace.
			@param nombreViaOrig: Nombre de la viaMultiple de origen.
			@type nombreViaOrig: String
			@return: color en RGB
			@rtype: Integer """
		col=self.colStreams[nombreViaOrig]
		return col
