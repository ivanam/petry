from utilidades.constantes import DATOS_DE_AREAS
import logging
""" Este modulo define la clase Area empleada por la vista para el dibujado de los elementos de la via multiple."""
class Area(object):
	""" Esta clase que mantiene la informacion acerca de un area de la simulacion que sera dibujada. 
		La division por Areas funciona de la siguiente manera:
			1. Se divide la simulacion por objetos "Area", donde cada area mantiene los sig. atributos:
					-Nombre del area (area1,area2,area3,etc.)
					-Arreglo con los nombres de los lugares que pertenecen al area.
					-self.contieneSemarofos=True | False, que indica si el area contiene o no los semaforos,
			y en caso de que sea cierto cuando el usuario ciclee sobre esta area, se debera invocar al metodo
			"marcarRedSemaforos()".
					-self.lugaresRP. Se mantendra una coleccion de objetos (lugares de RP,semarofos),
			con los objetos del modelo que se deberan consultar por cambios. 
				-self.simulacion. Referencia a la simulacion.

			2. Cuando el usuario selecciona un area, se crea un objeto Area que representa dicha area y
			se encarga de refrescar periodicamente el escenario en esa area. Al ejecutarse por primera vez,
			la simulacion carga por defecto la interseccion con los semaforos.

			3. Si el usuario selecciona otra area, se descarta ese objeto y se crea el nuevo objeto Area, que representa
			a la nueva porcion del mapa. 
 			Esta clase se instancia cada vez que el selecciona una clase diferente desde el menu de clases. 
 			Las areas de la simulacion se dividen de la siguiente forma (Contemplando los carriles p1x como los p2x, en el caso
 			de que se tengan dos carriles.:
	 			-La Interseccion (AREA_INTERSECCION) que abarca semaforoLink1, semaforoLink3, semaforoLink6 y los sig. lugares:
	 				* p14, p15, p16 (incluyendo p24, p25, p26)
	 				*De LINK 1: p18.L1 (p28.L1), p14,p15,p16 (p24,p25,p26).
	 				*De Link 2: p30.L2, p31.L2.
	 				*De Link 3: p13.L3, p12.L3.
	 				*De Link 4: p17.L4, p18.L4,p19.L4 (p27.L4, p28.L4, p29.L4).
					*De LINK 5: p32.L5, p33.L5.
					*De LINK 6: p111.L6, p112.L6 (p211.L6, p212.L6)
	 
	 			-El LINK 4, se divide en las sig. areas:
	 				*AREA_L4 (Salida de la interseccion). Se contemplan lugares de p110.L4 a p118.L4 (p210.L4, p218.L4).
	 
	 			-El Link 6 (y LINK5) se divide en:
					*AREA_L6_L5_1 (Ingreso al Link 6). Se contemplan los lugares p14.L6 hasta p10 (p24.L6 hasta P20).
	 
	 				*AREA_L6_L5_2 (Continuacion del ingreso a LINK 6). Se contemplan lugares p110.L6 hasta p15.L6(p210.L6 hasta P25.L6).
	 				Esta area tambien contempla el lugar p34.L5 del LINK 5.
	 
	 			-El LINK 2 (y LINK 3), se dividen en las sig. areas: 
	 				*AREA_L2_L3: 
						*De LINK 3: p11.L3,p10.
	 					*De LINK 2: Se contemplan los lugares de p32.L2 hasta p37.L2.
	 				NOTA: Se omiten los lugares p38.L2, p39.L2 de la grafica por cuestiones de simplicidad.

	 			-El LINK 1, se divide en las sig. areas: 
	 				*AREA_L1_1 (Ingreso de trafico a L1). Se contemplan los lugares desde p10 hasta p17.L1
	 				(p20 hasta p27.L1). """
	@classmethod
	def getLugaresEnArea(self,nombreArea):
		""" Retorna un diccionario con los lugares divididos por viaMulitple a la que
			pertenecen.
			@param nombreArea: Nombre del area a buscar 
			@type nombreArea: String """
		# Se filtran solamente los nombres de los lugaresRP y las viasMultiples que pertenecen
		# al area, de toda la informacion de las areas. 
		diccLugares={}
		for clave,lugs in DATOS_DE_AREAS[nombreArea].iteritems():
			# Si es una viaMultiple se almacena la informacion.
			if clave=="viaX" or clave=="viaYDesc" or clave=="viaYAsc":
				diccLugares[clave]=lugs
		return diccLugares

	@classmethod
	def obtenerPathImagen(self,nombreArea):
		""" Retorna la ruta en la que se encuentra un area en particular.
			@param nombreArea: Nombre del area a buscar 
			@type nombreArea: String """
		return DATOS_DE_AREAS[nombreArea]["pathImagen"]

	@classmethod
	def obtenerContieneSemaforos(self,nombreArea):
		""" Determina si un area contiene los semaforos dado su nombre.
			@param nombreArea: Nombre del area a dibujar
			@type nombreArea: String """
		logging.debug("Leyendo area: "+str(nombreArea))
		logging.debug("")
		return DATOS_DE_AREAS[nombreArea]["contieneSemaforos"]

	@classmethod
	def getSemaforos(cls,nombre):
		""" Retorna los nombres de los semaforos que pertenecen a un area.
			@param nombre: Nombre del area para la que se buscaran los nombres de los semaforos.
			@type nombre: String"""
		return DATOS_DE_AREAS[nombre]["semaforos"]

	def __init__(self,nombreArea,simulacion):
		""" Constructor de la clase Area.
			@param nombreArea: Nombre del area
			@type nombreArea: String
			@param simulacion: Referencia a la simulacion
			@type simulacion: Simulacion """
		self.nombre=nombreArea
		self.contieneSemaforos=Area.obtenerContieneSemaforos(nombreArea)
		self.pathImagen=Area.obtenerPathImagen(nombreArea)
		self.simul=simulacion
		diccNombres=Area.getLugaresEnArea(self.nombre)
		# Se crea la coleccion de lugaresRP que pertenecen al Area.
		self.lugaresRP=self.obtenerLugaresRP(diccNombres)

	def getPathImagen(self):
		""" Metodo getter para el atributo 'pathImagen'.
			@return: Ruta donde se encuentra la imagen de fondo de un area
			@rtype: String """
		return self.pathImagen

	def getLugaresRP(self):
		""" Metodo getter para el atributo 'lugaresRP'.
			@return: Coleccion de lugares de la red de Petri que se encuentran dentro del area.
			@rtype: List """
		return self.lugaresRP

	def getContieneSemaforos(self):
		""" Metodo getter para el atributo 'contieneSemaforos'.
			@return: Flag que indica si un area contiene a los semaforos
			@rtype: Boolean """
		return self.contieneSemaforos

	def getNombre(self):
		""" Metodo getter para el atributo 'nombre'.
			@return: Nombre con el que se identifica al area
			@rtype: String """
		return self.nombre

	def getVehiculos(self):
		""" Metodo getter para el atributo 'vehiculos'.
			@return: Vehiculos que se encuentran circulando actualmente en un area
			@rtype: List """
		vehiculos=[]
		copiaLugares=self.lugaresRP
		for nombreLug,tupla in copiaLugares.iteritems():
			logging.debug("Iterando lugar %s " % nombreLug)
			logging.debug("")
			lug=tupla["lugarRP"]
			if not lug.is_empty():
				logging.debug("Lugar %s no vacio! " % nombreLug)
				logging.debug("")
				# Se debe hacer una copia de los objetos token en un lugarRP
				# ya que durante el dibujado se puede cambiar el tamanio del diccionario, lo que puede
				# producir una excepcion en tiempo de ejecucion. 
				tokens=lug.tokens.copy()
				for vehiculo,tipo in tokens.iteritems():
					logging.debug("Token: vehiculo=%s ; tipo=%s en lugar %s " % (vehiculo,tipo,nombreLug))
					logging.debug(" %s " % str(type(vehiculo).__name__))
					logging.debug("")
					#Si es un vehiculo se dibuja
					if str(type(vehiculo).__name__)=='Vehiculo':
						vehiculos.append(vehiculo)
		logging.debug("Vehiculos obtenidos son: %s" %(vehiculos))
		logging.debug("")
		return vehiculos

	def obtenerLugaresRP(self,nombreLugares):
		""" Este metodo obtiene los lugares de la red de Petri en base al diccionario con los nombres de los lugares
			y las viasMultiples.
	 		Retorna un diccionario de la forma:
	 		-dicc= {
	 			"p16.L1": { "viaMultiple": "viaX", "lugarRP": place ("p16.L1") }, 
	 			"p26.L1": { "viaMultiple": "viaX", "lugarRP": place ("p26.L1") }, 
	 			"p211.L6": { "viaMultiple": "viaYDesc", "lugarRP": place ("p211.L6") },
	 			...
	 		}
		 donde "object place" es una referncia a un objeto Place que mantiene el objeto Net 
		 de la libreraria de la Red de Petri.
		 @param nombreLugares: Nombre de los lugares de los que se desea obtener una referencia
		 @type nombreLugares: List
		 @return: Coleccion de lugares de la red de Petri
		 @rtype: List """
		logging.debug("=================== Inicio de obtenerLugaresRP() =================================")
		logging.debug("")
		colLugaresRP={}
		red=None
		# Se obtienen los demas lugares con un for
		for nombreVia,lugares in nombreLugares.iteritems():
			logging.debug("iterando con nombreVia: "+str(nombreVia)+ "; lugares: "+str(lugares))
			logging.debug("")
			# Se obtiene la referencia a la RP de la ViaMulitple de la simulacion.
			red=self.simul.obtenerRP(nombreVia)
			# Se recorren los lugares que se tienen que obtener de la ViaMultiple.
			for nombreLug in lugares:
				logging.debug("Agregando lugar: "+str(nombreLug))
				logging.debug("")
				# Si existe el lugar se agrega al diccionario con su nombre de viaMultiple
				lug1=red.place(nombreLug)
				dicc={"viaMultiple": nombreVia, "lugarRP":lug1 }
				colLugaresRP[str(lug1)]=dicc
			logging.debug("AL final de la iteracion colLugaresRP tiene: "+str(colLugaresRP))
			logging.debug("")	
		logging.debug("Los lugares del area finales obtenidos fueron: "+str(colLugaresRP))
		logging.debug("")
		logging.debug("=================== Fin de obtenerLugaresRP() =================================")
		logging.debug("")
		return colLugaresRP
