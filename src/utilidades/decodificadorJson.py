# Lineas de prueba
# from decodificadorJson import *
# d=cargarJson("datos.json")

# Ejemplo de la salida de convertirUnicodeAStr().
# Conviertiendo objeto : {u'y': 160, u'x': 110, u'tamanio': 28, u'texto': u'TEXTO_AREA_L6_L5_1'}
# Conviertiendo objeto : {u'y': 190, u'x': 110, u'tamanio': 28, u'texto': u'TEXTO_AREA_L6_L5_2'}
# Conviertiendo objeto : {u'AREA_L2_L3': None, u'TITULO2': None, u'AREA_L5_L6_2': None, u'AREA_L5_L6_1': None, u'INTERSECCION': None, u'AREA_L4': None, u'TITULO': None, u'AREA_L1': None}
""" Este metodo alberga metodos auxiliares para convertir los datos leidos de un Json y decodificar 
	las claves y los valores 'unicode' en valores de tipo 'string'. Tambien contiene metodos auxiliares para ayudar a 
	evaluar strings y convertirlos en expresiones en Python que retornen algun valor. """
import json
import os
from constantes import *
def convertirUnicodeAStr(diccionario):
	""" Metodo auxiliar que recibe una lista ordenada, donde el primer elemento es la clave 
		de un objeto en Json y el seguno elemento es el valor de ese objeto.
		Este metodo es utilizado por json.load() de la siguiente manera:
			-Recorre los diccionarios que se encuentran definidos primero
			-Recorre el diccionario mas interior dentro de una posicion y retorna esos valores.
			-Procede con el resto de los dicionarios que se encuentran al mismo nivel.
			-Sube un nivel mas arriba en la jerarquia de jsons y repite todo de nuevo."""
	resultado={}
	# print "En convertirUnicodeAStr()..."
	# print ""
	for clave,valor in diccionario.iteritems():
		claveNueva=valorNuevo=""
		claveNueva=clave
		# print "En el bucle, clave %s..." % clave
		# print ""
		if clave!=None and isinstance(clave,unicode):
			claveNueva=str(clave)
		valorNuevo=valor
		if valor!=None and isinstance(valor,unicode):
			valorNuevo=str(valor)
		resultado[claveNueva]=valorNuevo
	return resultado

def cargarJson(nombre,path=""):
	""" Este metodo carga un archivo Json y lo retorna en forma de diccionario, convirtiendo 
		caracteres unicode en string, y valores en numeros.
		@param nombre: Nombre del archivo a convertir
		@type nombre: String
		@param path: Ruta donde se encuentra el archivo
		@type path: String
		@return: El objeto Json convertido a diccionario en Python
		@rtype: Diccionario """
	print "Leyendo archivo %s en directorio: %s " % (nombre,os.getcwd()+"/"+path+"/"+nombre)
	print ""
	f=open(path+"/"+nombre,"r")
	datosParseados={}
	datosParseados=json.load(f,object_hook=convertirUnicodeAStr)
	return datosParseados

# >>> dic={ "a":1,"b":2}
# >>> valor=eval('dic["a"]')
# >>> valor
def convertirExpresion(expresion):
	""" Este metodo retorna el resutlado de evaluar una expresion en Python en formato de string.
		Se invoca a este metodo cuando se necesitan evaluar expresiones donde se referencian
		a diccionarios exportados previamente.  
		@param expresion: Expresion que sera evaluada
		@type expresion: String
		@return: Retorna el resultado de haber evaluado una expresion
		@rtype: Valor """
	global dicEsquemas
	global dicTraficoPredefinido
	return eval(expresion)
