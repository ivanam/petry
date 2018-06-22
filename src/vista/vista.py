# coding= utf-8
########################################################################################################
############################## Imports de Pygame #######################################################
########################################################################################################
#
import pygame
from pygame.locals import *
from utilidades.decodificadorJson import *
from easygui import *
import sys
import logging
from area import *
from utilidades.constantes import CANT_MINIMA_CICLOS_INGRESADOS_USR,CANT_MAXIMA_CICLOS_INGRESADOS_USR


""" Este modulo contiene la clase Vista y SpriteVehiculo. """
class Vista(object):
	""" Esta clase se utiliza para dibujar los elementos que forman parte de la simulacion en la pantalla, como
		semaforos, vehiculos y cudriculas.  """
	def __init__(self,areaPorDefecto="INTERSECCION"):
		""" Metodo constructor de la vista.
			@param areaPorDefecto: Area que se muestra por defecto al iniciar la simulacion
			@type areaPorDefecto: String """
		self.modelo=self.screen=self.reloj=None
		# Esto se mantiene para cambiar entre distintos fondos cuando el usuario presiona una tecla de las
		# del menu.
		self.areaCargada=areaPorDefecto
		# Tambien se mantiene una referencia al objeto area actual.
		self.area=None
		# Se mantiene el layout del menu de la simulacion (indexado por el nombre del objeto area) y el
		# titulo que se ubica encima de las opciones del menu.
		# Los nombres de las areas son: 
		# 		-"INTERSECCION"
		# 		-"AREA_L1"
		# 		-"AREA_L2_L3"
		# 		-"AREA_L4"
		# 		-"AREA_L6_L5_1"
		# 		-"AREA_L6_L5_2"
		layoutAux={}
		layoutAux=cargarJson("menu.json","vista/json/vista")
		self.layoutMenu=self.transformarTextosMenu(layoutAux)
		self.screen = pygame.display.set_mode((MAPA_ANCHO, MAPA_ALTO))
		print "Vista creada!"
		print ""

	def transformarTextosMenu(self,layoutAux):
		""" Este metodo retorna un diccionario con donde las referencias a las constantes que tienen los textos 
			del menu principal han sido evaluadas.
			@param layoutAux: Diccionario con expresiones sin evaluar
			@return layoutAux: Diccionario
			@return: Diccionario con expresiones de los elementos del menu evaluadas
			@rtype: Diccionario """
		for clave,elementos in layoutAux.iteritems():
			elementos["texto"]=convertirExpresion(elementos["texto"])
		return layoutAux

	def dibujarMenu(self):
		""" Este metodo  dibuja el menu de opciones con las letras que debe presionar el usuario para cambiar de area
			en la pantalla."""
		for itemMenu,dicItem in self.layoutMenu.iteritems():
			# Se obtiene el nombre de la cuadricula y se adjunta al objeto font de pygame.
			font1= pygame.font.Font(None, dicItem["tamanio"])
			colorTexto=pygame.Color(0,0,0,100)
			label = font1.render(dicItem["texto"], True, colorTexto)
			# Se centra el texto obteniendo el Rect correspondiente al texto creado.
			posX=dicItem["x"]
			posY=dicItem["y"]
			rectFont1=label.get_rect(centerx =posX, 
				centery=posY)
			self.screen.blit(label, rectFont1)

	def obtenerPathArea(self):
		""" Este metodo obitene el path de la imagen de background que se encuentra cargada actualmente.
			@return: Ruta de la imagen del area
			@rtype: String """
		return self.area.getPathImagen()

	def setModelo(self,mod):
		""" Metodo setter para el atributo 'modelo'
			@param mod: Referencia a la simulacion
			@type mod: Simulacion """
		self.modelo=mod
		
	def setReloj(self,r):
		""" Metodo setter para el atributo 'reloj'
			@param r: Referencia al reloj
			@type r: Reloj """
		self.reloj=r

	# Vista.mostrar()
	def mostrar(self):
		""" Este metodo carga e inicializa la vista para que se muestre en pantalla. """
		self.screen = pygame.display.set_mode((MAPA_ANCHO, MAPA_ALTO))
		pygame.display.set_caption("Simulacion de Trafico")
		# Se crea un reloj que controle el tiempo de simulacion.
		clock = pygame.time.Clock()

		while True:
			for eventos in pygame.event.get():
				if eventos.type == QUIT:
					print "Saliendo de la simulacion!"
					print ""
					self.modelo.cancelar()
					sys.exit(0)
				elif eventos.type == KEYDOWN:
					self.cargarArea(eventos.key)
			self.actualizar()
		return 0

	# Vista.actualizarReloj()
	def actualizarReloj(self):
		""" Este metodo actualiza el reloj mostrado en la vista."""
		# Se obtiene el nombre de la cuadricula y se adjunta al objeto font de pygame.
		textoReloj="Tiempo transcurrido: %s min. %s seg. " % (self.reloj.getMinutos(),self.reloj.getSegundos())
		font1= pygame.font.Font(None, self.reloj.getTamanioLetra())
		colorTexto=pygame.Color(0,0,0,100)
		label = font1.render(textoReloj, True, colorTexto)
		# Se centra el texto obteniendo el Rect correspondiente al texto creado.
		rectFont1=label.get_rect(centerx = self.reloj.getPosicion().getX(), 
			centery=self.reloj.getPosicion().getY())
		self.screen.blit(label, rectFont1)
	
	# Vista.limpiarCanvas()
	def limpiarCanvas(self):
		""" Este metodo borra el escenario anterior, pintandolo completamente de negro."""
		self.screen.fill((255,255,255))

	# Vista.actualizar()
	def actualizar(self):	
		""" Este metodo carga el fondo de la pantalla y le indica a pygame con 
			pygame.display.flip() que refresque la vista con los nuevos cambios. """
		self.limpiarCanvas()
		# Se carga la imagen de fondo de la simulacion.
		# logging.debug("En actualizar()...")
		# logging.debug("")
		imagenFondo=self.cargarFondo()
		self.screen.blit(imagenFondo,(0,0))

		# Se dibujan las cuadriculas que pertenecen al modelo.
		# Se obtiene un diccionario con los lugaresRP dependiendo del area.
		# La forma del diccionario es la siguiente:
		# 	-dicc= {
		# 			"p16.L1": { "viaMultiple": "viaX", "lugarRP": place ("p16.L1") },
		# 			...
		# 			}
		cuadriculasRP=self.area.getLugaresRP()
		# logging.debug("Diccionario de cuadriculasRP --> %s" % cuadriculasRP)
		# logging.debug("")
		for nro,dicCuadricula in cuadriculasRP.iteritems():
			# logging.debug(" ITERANDO SOBRE CUADRICULA %s ..." % nro)
			# logging.debug("")
			self.dibujarCuadricula(dicCuadricula["lugarRP"].getCuadricula())			
		for v in self.area.getVehiculos():
			sp= SpriteVehiculo(self,v)
			# Se pasa la referencia al canvas o "Surface" como primer argumento
			sp.actualizar(self.screen, v.getCuadricula().getPosicion().getX()+35,
				v.getCuadricula().getPosicion().getY()+25,
				v.getColores())
			self.screen.blit(sp.getImage(),sp.getRect())

		# Se actualizan los semaforos, si el area cargada actualmente los contiene.
		# NOTA: Si una area no contiene semaforos, estos se borran automaticamente de la vista,
		# por self.screen.fill().
		if self.area.getContieneSemaforos():
			for nombreSem,semaforo in self.modelo.getRedSemaforos().getSemaforos().iteritems():
				self.dibujarSemaforo(semaforo)
		# Se actualiza el Reloj y el menu.
		self.actualizarReloj()
		self.dibujarMenu()
		pygame.display.flip()

	# Vista.getArea()
	def getArea(self):
		""" Metodo getter para el atributo 'area'.
			@return: Area actual cargada
			@rype: Area """
		return self.area

	# Vista.cargarAreaPorDefecto()
	def cargarAreaPorDefecto(self):
		""" Este metodo se utiliza para cargar el area la primera vez que se inicializa la vista. """
		self.area=Area(self.areaCargada,self.modelo)

	# vista.cargarAreaPorDefecto()
	def cargarArea(self,codigoFondo):
		""" Metodo manejador que se llama cuando el usuario presiona una tecla correspondiente a uno de los numeros 
			de area en el menu principal.
			@param codigoFondo: Codigo del area que se cargara
			@type codigoFondo: Integer """
		nombreArea=""
		if codigoFondo == OPCION_MENU_INTERSECCION:
			nombreArea="INTERSECCION"
		elif codigoFondo == OPCION_MENU_AREA_L1:
			nombreArea="AREA_L1"
		elif codigoFondo == OPCION_MENU_AREA_L2_L3:
			nombreArea="AREA_L2_L3"
		elif codigoFondo == OPCION_MENU_AREA_L4:
			nombreArea="AREA_L4"
		elif codigoFondo == OPCION_MENU_AREA_L6_L5_1:
			nombreArea="AREA_L6_L5_1"
		elif codigoFondo == OPCION_MENU_AREA_L6_L5_2:
			nombreArea="AREA_L6_L5_2"
		# Nombre del areaCargada actualmente
		if nombreArea!="":
			# logging.debug("Cargando area: "+str(nombreArea)+"...")
			# logging.debug("")
			self.areaCargada=nombreArea
			self.area=Area(nombreArea,self.modelo)
		# else:
			# logging.debug("Tecla no valida!")
			# logging.debug("")
			
	# vista.cargarFondo()
	def cargarFondo(self):
		""" Este metodo obtiene la ruta de una imagen e invoca a otro metodo que abra la imagen y que la cargue. """
		pathFondo=self.obtenerPathArea()
		fondo= self.cargarImagen(pathFondo)
		return fondo

	# vista.cargarImagen()
	def cargarImagen(self,filename,transparent=False):
		""" Este metodo obtiene la imagen que corresponde al area (desde un archivo adjunto al proyecto).
			@param filename: Nombre de la imagen
			@type filename:String
			@param transparent: Atributo para controlar la transparencia de la imagen
			@type transparent: Boolean
			@return: Imagen leida
			@rtype: Surface """
		try: 
			image = pygame.image.load(filename)
		except pygame.error, message:
			print "Error %s : %s" % (pygame.error,message)
			raise SystemExit, message
		image = image.convert()
		if transparent:
			color = image.get_at((0,0))
			image.set_colorkey(color, RLEACCEL)
		return image

	# Vista.dibujarCuadricula()
	def dibujarCuadricula(self,cuadricula):
		""" Dibuja un rectangulo sobre la vista que representa al lugarRP sobre el que
			el vehiculo se encuentra en un momento dado.
			@param cuadricula: Cuadricula a dibujar
			@type cuadricula: Cuadricula """
		# Se crea una representacion del color
		color=pygame.Color(204,51,255,200)
		# Se crea un objeto "Rect" que es usado para dibujar figuras rectangulares y manipular sprites en  pygame.
		# Rect(left, top, width, height) -> Rect
		# getPosicionX
		rectCuadricula=pygame.Rect( cuadricula.getPosicion().getX(),cuadricula.getPosicion().getY(),
		 	cuadricula.getAncho(),cuadricula.getAlto())
		pygame.draw.rect(self.screen,color,rectCuadricula)
		# Se obtiene el nombre de la cuadricula y se adjunta al objeto font de pygame.
		nombreLug=cuadricula.getNombre()
		font1= pygame.font.Font(None, 18)
		colorTexto=pygame.Color(0,0,0,100)
		label = font1.render(nombreLug, True, colorTexto)
		# Se centra el texto obteniendo el Rect correspondiente al texto creado.
		rectFont1=label.get_rect(centerx =cuadricula.getPosicion().getX()+20 , 
			centery=cuadricula.getPosicion().getY()-10)
		self.screen.blit(label, rectFont1)

	# Vista.dibujarSemaforo()
	def dibujarSemaforo(self,semaforo):
		""" Dibuja un semaforo sobre la vista.
			@param semaforo: Semaforo a dibujar
			@type semaforo: Semaforo """
		rojo=azul=verde=alpha=0
		if semaforo.getEstado().getNombre()=="Detenido":
			rojo=255
			verde=0
			azul=0
		elif semaforo.getEstado().getNombre()=="EnAvance":
			rojo=0
			verde=255
			azul=0
		elif semaforo.getEstado().getNombre()=="EnAvanceConPrecaucion":
			rojo=245
			verde=245
			azul=0		
		alpha=100
		# Se crea una representacion del color
		color=pygame.Color(rojo,verde,azul,alpha)
		# Rect(left, top, width, height) -> Rect
		rectCuadricula=pygame.Rect( semaforo.getPosicion().getX(),semaforo.getPosicion().getY(),
		 	semaforo.getAncho(),semaforo.getAlto())		
		# Se obtiene el nombre de la cuadricula y se adjunta al objeto font de pygame.
		textoSemaforo=semaforo.getNombre()
		font1= pygame.font.Font(None, 18)
		colorTexto=pygame.Color(0,0,0,100)
		label = font1.render(textoSemaforo, True, colorTexto)
		# Se centra el texto obteniendo el Rect correspondiente al texto creado.
		rectFont1=label.get_rect(centerx =semaforo.getPosicion().getX()+20 , 
			centery=semaforo.getPosicion().getY()-10)
		self.screen.blit(label, rectFont1)
		pygame.draw.rect(self.screen,color,rectCuadricula)

	# Vista.solicitarInformacion()
	def solicitarInformacion(self):
		""" Este metodo solicita al usuario que ingrese la cantida de ciclos de tiempo que desea simular.
			@return: Conjunto de valores que el usuario ha ingresado.
			@rtype: Diccionario """
		diccDatosUsuario={}
		# Se solicita al usuario que seleccione el escenario que desea simular
		choices =["Escenario1", "Escenario2"] 
		choice = choicebox("¿Que escenario desea simular?", "Seleccion del escenario a simular", choices)
		if choice == None:
			try:
				sys.exit(1)
			except Exception, e:
				raise e			
		diccDatosUsuario["nombreEscenario"]=choice
		#Este tipo de msgbox retorna un arreglo de valores que tiene una correspondencia uno a uno con
		# el arreglo de parametros a solicitar (ultimo parametro de "multenterbox()")		
		result=multenterbox("Ingrese los intervalos en segundos indicados","Simulacion",["Cantidad de ciclos de tiempo"])
		if result==None:
			try:
				sys.exit(1)
			except Exception, e:
				raise e
		else:
			try:
				# Si esta fuera de los limites admitidos se rechaza.
				if int(result[0])<CANT_MINIMA_CICLOS_INGRESADOS_USR or int(result[0])+1 > CANT_MAXIMA_CICLOS_INGRESADOS_USR:
					msgbox("Error! El valor de la cantidad de ciclos no puede ser menor a %s  ni mayor a %s " % 
						(CANT_MINIMA_CICLOS_INGRESADOS_USR,CANT_MAXIMA_CICLOS_INGRESADOS_USR-1))
					sys.exit(1)
				diccDatosUsuario["cantCiclosTiempo"]=int(result[0])
			except Exception, e:
				msgbox("Error de tipo de datos!")
				# logging.debug("EXCEPCION AL INGRESAR LOS DATOS: ")
				# logging.debug(e)
				# logging.debug("")
				try:
					sys.exit(1)
				except SystemExit, e:
					pass
					# logging.debug("Cancelando la simulacion...")
					# logging.debug("")
		return diccDatosUsuario

class SpriteVehiculo(pygame.sprite.Sprite):
	""" Clase que representa al sprite de un vehiculo y mantiene atributos tales como su posicion, su idVehiculo,
		y la referencia al canvas para el redibujado. """
	def __init__(self,vista,vehiculo):
		""" Constructor de SpriteVehiculo.
			@param vista: Referencia a la vista de la simulacion.
			@type vista: Vista
			@param vehiculo: Referencia al vehiculo.
			@type vehiculo: Vehiculo """
		pygame.sprite.Sprite.__init__(self)
		self.vista=vista
		self.idVehiculo=vehiculo.getIdVehiculo()
		self.image = vista.cargarImagen(vehiculo.getPathImagen(), True)
		# Area rectangular de la imagen de pygame
		self.rect = self.image.get_rect()
		# Se define el centro de la pantalla como el centro del vehiculo
		self.rect.centerx = vehiculo.getCuadricula().getPosicion().getX()
		self.rect.centery = vehiculo.getCuadricula().getPosicion().getY()

	# Sprite.getIdVehiculo()
	def getIdVehiculo(self):
		""" Metodo getter para el atributo 'idVehiculo'.
			@return: El id del vehiculo actual.
			@rtype: String """
		return self.idVehiculo

	# Sprite.getImage()
	def getImage(self):
		""" Metodo getter para el atributo 'image'.
			@return: El descriptor de la imagen abierta anteriormente
			@rtype: Surface """
		return self.image

	# Sprite.getRect()
	def getRect(self):
		""" Metodo getter para el atributo 'rect'.
			@return: El area rectangular para la imagen
			@rtype: Rect """
		return self.rect

	# spriteVehiculo.actualizar()
	def actualizar(self,canvas,posX,posY,colores):
		""" Este metodo actualiza la posicion del sprite del vehiculo, como asi tambien
			el circulo de color, que simboliza el Streamset (color que se le da a un vehiculo circulando en un sentido)
			sobre el que circula el vehiculo.
			@param canvas: Referencia a la vista
			@param canvas:Vista
			@param posX: Coordenada X
			@type posX: Integer
			@param posY: Coordenada Y
			@type posY: Integer
			@param colores: Conjunto de colores
			@type colores: Tuple """
		self.rect.centerx=posX
		self.rect.centery=posY
		self.actualizarColores(canvas,colores,posX,posY)
		
	# spriteVehiculo.actualizarColores()
	def actualizarColores(self,canvas,tuplaColores,x,y):
		""" Dibuja un circulo sobre el sprite, que simboliza el color que tiene el stream
			sobre el que se encuentra. """
		print "Actualizando colores..."
		print ""
		rojo,verde,azul=tuplaColores[0],tuplaColores[1],tuplaColores[2]
		# Se dibuja un circulo sobre la posicion del sprite.
		# circle(Surface, color, pos, radius, width=0)
		print "actualizarColores() --> x: %s ; y: %s" % (x,y)
		print ""
		radio=15
		pygame.draw.circle(canvas,(rojo,verde,azul),(int(x),int(y)),int(radio))
		print "Actualizado color!"
		print ""

