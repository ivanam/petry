""" Este modulo define la clase Graficador."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

class Graficador(object):
	""" Esta clase tiene como funcion graficar los resultados de las estadisticas recolectadas por la 
		simulacion. """
	def __init__(self,resultados,cantidadCiclos,graficoInicio=1):
		""" Constructor de Graficador.
			@param resultados: Conjunto de valores recogidos por la simulacion
			@type resultados: Diccionario
			@param cantidadCiclos: Cantidad de ciclos maxima simulada
			@type cantidadCiclos: Integer
			@param graficoInicio: Indice en el que comienza el grafico
			@type graficoInicio: Integer """
		self.cantidadCiclos=cantidadCiclos
		# Se obtiene por defecto el grafico que se mostrara por defecto al inicio (graficoInicio).
		# Por defecto es el dic. con INDICE=1.
		self.indice=graficoInicio
		tupla=resultados[self.indice]
		self.resultados=resultados
		self.fig, self.ax = plt.subplots()
		plt.subplots_adjust(bottom=0.2)
		self.fig.canvas.set_window_title('Estadisticas de la simulacion de trafico')
		#Configuraciones del grafico de barras
		bar_width = 0.35
		opacity = 0.4
		# "coordenadas" es una tupla con (elementosX,elementosY) donde elementosX son los numeros de ciclo (20 en total)
		# y elementosY son la cant. de vehiculos.
		# Se obtienen las coordenadas (x,y) para el primer grafico seleccionado.
		coordenadas=self.obtenerCoordenadas(tupla)
		# Coleccion de elementos que denota la escala de valores del ejeY. Esta coleccion y los
		# "valoresAGraficarY" deben tener la misma cantida de elementos.
		escalaEjeY = np.arange(len(coordenadas[1]))
		# Se crea un arreglo de ceros que se ira actualizando a medida
		# que se lean los resultados de la simulacion.
		valoresY=[]
		cant=self.cantidadCiclos
		for i in xrange(1,cant+1):
			valoresY.insert(i,0)
		error_config = {'ecolor': '0.3'}
		#Valores de Y ordenados para cada ciclo.
		#Se crea un arreglo de 20 valores con 0 por defecto en todas las posiciones
		valoresAGraficarY=coordenadas[1]
		i=0
		for elem in valoresAGraficarY:
			valoresY.pop(i)
			valoresY.insert(i,elem)
			i+=1
		self.rects1 = plt.bar(escalaEjeY, tuple(valoresY), bar_width,
                 alpha=opacity,
                 color='b',
                 error_kw=error_config,
                 label='Trafico simulado')

		# Se configuran los elementos visuales del grafico.
		titulo=self.resultados[self.indice]["nombreLink"]
		plt.title(titulo)
		plt.ylabel(tupla["nombreVariable"])
		plt.xlabel("Ciclos (k)")
		# index =[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
		index=range(1,21)
		rangoDeValoresX=tuple(index)
		rangoDeValoresY=rangoDeValoresX
		plt.xticks(index, rangoDeValoresX)
		plt.yticks(index, rangoDeValoresY)
		# plt.axes(rect); donde "rect" = [left, bottom, width, height] in normalized (0, 1) units.
		axprev = plt.axes([0.7, 0.000015, 0.1, 0.075])
		axnext = plt.axes([0.81, 0.000015, 0.1, 0.075])
		# Se configuran los botones con sus listeners.
		bnext = Button(axnext, 'Siguiente')
		bnext.on_clicked(self.next)
		bprev = Button(axprev, 'Anterior')
		bprev.on_clicked(self.prev)
		# Se agrega el texto con los numeros a las barras del grafico y se hace visible.
		self._agregarTextoABarras(self.rects1,self.ax,valoresY)
		plt.show()

	
	# Graficador._agregarTextoABarras()
	def _agregarTextoABarras(self,rects1,ax,valoresY):
		""" Agrega el valor especifico que tiene una coordenada Y en el grafico de barras en forma de texto, encima de la
			barra que lo representa.
			@param rects1: Conjunto de barras del grafico de barras
			@type rects1: Bar
			@param ax: Axis perteneciente al grafico
			@type ax: Axis
			@param valoresY: Valores en Y para los que agregara el texto
			@type valoresY:	Array """
		i=0
		# Metodo para alinear los valores de las barras del grafico.
		for rect in rects1:
		        xloc=rect.get_x()
		        yloc = rect.get_y()+rect.get_height()
		        rankStr=str(valoresY[i])
		        i+=1
		        ax.text(xloc, yloc, rankStr, horizontalalignment="left",
		            verticalalignment='center', color='black', weight='bold')

	def obtenerCoordenadas(self,tupla):
		""" Retorna una tupla, cuyos elementos son arreglos con los valores de las coordenadas X e Y de los valores
			del grafico.
			@param tupla: Elementos en X e Y que componen el grafico
			@type tupla: Tuple
			@return: Tupla de arreglos con los valores en X e Y en arreglos separados
			@rtype: Array """
		arregloX=[]
		arregloY=[]
		for clave,valor in tupla["rangoValores"].iteritems():
			arregloX.append(clave)
			arregloY.append(valor)
		return arregloX,arregloY

	# Simulacion.actualizar()
	def actualizar(self,tuplaCoord):
		""" Este metodo actualiza el grafico con nuevos valores cuando el usuario hace click sobre
			uno de los botones que cambia el numero de grafico. 
			@param tuplaCoord: Tupla con las coordenadas x e y del grafico
			@type tuplaCoord: Tuple """
		xdata=tuplaCoord[0]
		ydata=tuplaCoord[1]
		#Se borra el axis y sobre los ejes anteriores se reconfigura
		self.ax.cla()
		titulo=self.resultados[self.indice]["nombreLink"]
		self.ax.set_title(titulo)
		self.ax.set_ylabel(self.resultados[self.indice]["nombreVariable"])
		self.ax.set_xlabel("Ciclos (k)")
		bar_width = 0.35
		opacity = 0.4
		valoresY=[]
		cant=self.cantidadCiclos
		for i in xrange(1,cant+1):
			valoresY.insert(i,0)
		

		escalaEjeY=np.arange(1,self.cantidadCiclos+1)
		valoresAGraficarY=ydata

		i=0
		for elem in valoresAGraficarY:
			valoresY.pop(i)
			valoresY.insert(i,elem)
			i+=1

		error_config = {'ecolor': '0.3'}
		# Rectangulos del grafico de barras.
		self.rects1 = self.ax.bar(escalaEjeY,tuple(valoresY), bar_width,
                 alpha=opacity,
                 color='b',
                 error_kw=error_config,
                 label='Trafico simulado')

		#Las coordenadas a la izquieda (index) es un arreglod e elementos,
		# mientras que los valores en Y que se tinen que graficar es
		# una tupla de enteros. 
		#
		index =range(1,21)
		rangoDeValoresX=tuple(index)
		rangoDeValoresY=rangoDeValoresX

		# NOTA: Con subplot, se indica a que grafico se esta haciendo referencia,
		# ya que cuando se tienen varios graficos se conforma una grilla de elementos.
		# subplot(nrows, ncols, plot_number).
		plt.subplot(1,1,1)	
		plt.xticks(index, rangoDeValoresX)
		plt.yticks(index, rangoDeValoresY)
		self._agregarTextoABarras(self.rects1,self.ax,valoresY)
		plt.show()

	# Graficador.next()
	def next(self, event):
		""" Este metodo funciona como manejador del boton siguiente y, obtiene las coordenadas del grafico
			siguiente y solicita una actualizacion del grafico de barras.
			@param event: Evento enviado al manejador
			@type event:   """
		self.indice+=1
		if self.indice>len(self.resultados):
			self.indice=1
		tupla=self.resultados[self.indice]
		coordenadas=self.obtenerCoordenadas(tupla)
		self.actualizar(coordenadas)

	# Graficador.prev()
	def prev(self, event):
		""" Este metodo funciona como manejador del boton siguiente y, obtiene las coordenadas del grafico
			siguiente y solicita una actualizacion del grafico de barras.
			@param event: Evento enviado al manejador
			@type event:   """
		self.indice-=1
		if self.indice<1:
			self.indice=len(self.resultados)
		tupla=self.resultados[self.indice]
		coordenadas=self.obtenerCoordenadas(tupla)
		self.actualizar(coordenadas)
