""" 
	Definicion de las constantes utilizadas por la simulacion de trafico.
"""
###########################################################################################
########################## Constantes que involucran el texto del menu  ###################
##########################	de la vista	       			 ##################################
###########################################################################################
TEXTO_TITULO="Areas de la simulacion:"
TEXTO_INTERSECCION="00: Area interseccion   "
TEXTO_AREA_L1="01: Area Link1           "
TEXTO_AREA_L2_L3="02:Area Link2-Link3     "
TEXTO_AREA_L4="04:Area Link 4          "
TEXTO_AREA_L6_L5_1="05:Area Link6-Link5-pt.2"
TEXTO_AREA_L6_L5_2="06:Area Link6-Link5-pt.1"

# Constantes usadas para levantar los distintos fondos segun la tecla pulsada.
# 
# MENU DE OPCIONES:
# 					1: Se carga la interseccion con sus lugares
# 					2: Se carga el AREA_L1 con sus lugares
# 					3: Se carga el AREA_L2 con sus lugares
# 					4: Se carga el AREA_L3 con sus lugares
# 					5: Se carga el AREA_L4 con sus lugares
OPCION_MENU_INTERSECCION=48
OPCION_MENU_AREA_L1=49
OPCION_MENU_AREA_L2_L3=50
OPCION_MENU_AREA_L4=52
OPCION_MENU_AREA_L6_L5_1=53
OPCION_MENU_AREA_L6_L5_2=54

###########################################################################################
########################## Constantes de las dimensiones del mapa  ########################
###########################################################################################
MAPA_ANCHO=900
MAPA_ALTO=600

########################################################################################################################################
#################################################### Constantes usadas por la red de Petri #############################################
########################################################################################################################################

########################################################################################################################################
######################################## Definicion de los tipos de tokens que pueden producir los lugares #############################
########################################################################################################################################

#Delays en segundos de los tipos de vehiculo que circulan por las vias
delayAutomovil=.45
delayColectivo=1.35
tiposToken={
			"automovil":{"pathIcono":"data/audi.png","delay":delayAutomovil },
			"colectivo":{"pathIcono":"data/audi.png","delay":delayColectivo }
}

############################################################################################################
#################################### MAPEO DE LOS COLORES SEGUN LOS LINKS ##################################
############################################################################################################

# La distribuicion de colores se lee "ColorA1(L1,L4) es el color de los vehiculos que siguen el flujo
#  desde LINK 1 hacia LINK 4 " y es la siguiente:
#	-Color A1 (L1,L4):
#			*nroCarril: 1 -->(214,0,0) #ROJO FUERTE

#	-Color A2 (L1,L2):
#			*nroCarril: 2 --> (255,204,51) #AMARILLO

#	-Color A3 (L6,L2):
#			*nroCarril: 1 --> (102,255,51) #VERDE CLARO

#	-Color A4 (L6,L4):
#			*nroCarril: 2 --> (255,20,177) #ROSA

#	-Color A5 (L3,L5):
#			*nroCarril: 1 --> (20,60,255) #AZUL
#
mapeoColores={
		"a1":(214,0,0),
		"a2":(255,255,0),
		"a3":(10,255,10),
		"a4":(255,0,204),
		"a5":(20,60,255)
}

#####################################################################################################################################
######################################### Definicion de la Via de circulacion X (Link1) #############################################
#####################################################################################################################################

#NOTA: Las vias de circulacion tienen:
#									-3 lugares de entrada en la RP (p11,p12,p13 y p21,p22,p23 ).
#									-2 lugares de salida en la RP, que dependen de la numeracion en la RP.


#NOTA: La cant. de lugares reales es la sig. :
#									-Link 1 --> 16 lugares (8 lugares por via)   (18 lug. en total por lugares p10 y p20)
#									-Link 2 --> 9 lugares 						 (10 lug. en total) 
#									-Link 4 --> 24 lugares (12 lugares por via ) (24 lug. en total)
#									-Link 6 --> 24 lugares (12 lugares por via ) (26 lug. en total)
#									-Link 3 --> 3 lugares 						 (3 lug. en total)
#									-Link 5 --> 4 lugares 						 (4 lug. en total)
#
#									TOTAL DE LUGARES EN LA RP= 85 Lugares de viaMultiple + 6 Lugares de Interseccion.
#
#									TOTAL DE LUGARES EN LA RP= 91 LUGARES + 1 PANTALLA = 92 lugares en z-order=1.
#											

##############################################################################################################################
###################################### Definicion de los Ij's(Tabla 3-Fixed signal timing plans) #############################
##############################################################################################################################
#NOTA: Este diccionario define la duracion de los I's que figuran en la tabla y se usan para la definicion del tiempo de los 
# semaforos como asi tambien para calcular cuanto durara la fase_roja o fase_verde_amarilla de un semaforo en total!
#
DICC_FASES={
			"i1":31,
			"i2":4,
			"i3":1,
			"i4":4,
			"i5":2,
			"i6":22,
			"i7":4,
			"i8":2
}

#CONSTANTES PARA EL CONTROL DE LA DISPOSICION DE LUGARES EN EL ESCENARIO.
#NOTA: El diccionario de cada viaMultiple mantiene la "DISTANCIA" entre lugares, para los
#lugares de esa via.
#
CONSTANTES_LAYOUT={
	"viaX": {"ANCHO": 50, "ALTO":40, "DISTANCIA": 50 },
	"viaYDesc": {"ANCHO":40 , "ALTO":50, "DISTANCIA": 50  },
	"viaYAsc": {"ANCHO": 40, "ALTO": 50, "DISTANCIA": 50 }
}


################################################################################################
################################ Alternativas de disparo para la viaX ##########################
################################################################################################

#Se crea un arreglo de objetos "AlternativaDeDisparo" en base a un diccionario
#que tiene el orden de disparo de las altenativas y los nombres de las tranisciones que conforman
#dichas altenativas.
#Las dos ultimas "alternativas de disparo" son los inicios  de la RP, por lo que no se evaluan contra
#Alternativas de disparo para la ViaMultipleX
#
diccAlternativasDisparoX={
			47:["t21.L1"],
			46:["t11.L1"],
			45:["t22.L1","t21_12.L1"],
			44:["t12.L1","t11_22.L1"],
			43:["t23.L1","t22_13.L1"],
			42:["t13.L1","t12_23.L1"],
			41:["t14.L1","t13_24.L1"],
			40:["t24.L1","t23_14.L1"],

			39:["t15.L1","t14_25.L1"],
			38:["t25.L1","t24_15.L1"],
			37:["t16.L1","t15_26.L1"],
			36:["t26.L1","t25_16.L1"],

			
			35:["t17.L1","t16_27.L1"],
			34:["t27.L1","t26_17.L1"],
			33:["t18.L1","t17_28.L1"],
			32:["t28.L1","t27_18.L1"],


			#Inicio a la zona de interseccion
			31:["t24"],
			30:["t14"],

			#Conexiones entre LINKS(sin cambio de carril): t16, t26
			#Viro de los vehiculos a la derecha
			28:["t25"],
			27:["t15"],
			#Viro de los vehiculos a la derecha
			26:["t26"],
			25:["t16"],

			#Conexiones entre LINKS (sin cambio de carril): t17,t27
			24:["t27.L4"],
			23:["t17.L4"],

			22:["t28.L4","t27_18.L4"],
			21:["t18.L4","t17_28.L4"],
			20:["t29.L4","t28_19.L4"],
			19:["t19.L4","t18_29.L4"],

			18:["t210.L4","t29_110.L4"],
			17:["t110.L4","t19_210.L4"],
			16:["t211.L4","t210_111.L4"],
			15:["t111.L4","t110_211.L4"],
			14:["t212.L4","t211_112.L4"],
			13:["t112.L4","t111_212.L4"],
			12:["t213.L4","t212_113.L4"],
			11:["t113.L4","t112_213.L4"],
			10:["t214.L4","t213_114.L4"],
			9:["t114.L4","t113_214.L4"],
			8:["t215.L4","t214_115.L4"],
			7:["t115.L4","t114_215.L4"],
			6:["t216.L4","t215_116.L4"],
			5:["t116.L4","t115_216.L4"],
			4:["t217.L4","t216_117.L4"],
			3:["t117.L4","t116_217.L4"],
			2:["t218.L4","t217_118.L4"],
			1:["t118.L4","t117_218.L4"]
}

# Se crea un diccionario que mantiene el nombre de los lugares de inicio y fin en la RP
diccInicioViaX={ 1: "p10", 2: "p20"}
diccFinViaX={ 1: "p118.L4", 2: "p218.L4"}

#Se mantiene un diccionario con los nombre de ViaMultiple a los que se puede acceder
viasCircHabilitadasViaX=["viaYDesc"]

####################################################################################################
################################ Alternativas de disparo para la viaYDesc ##########################
####################################################################################################

diccInicioViaYDesc={ 1: "p10", 2: "p20"}
diccFinViaYDesc={ 1:"p39.L2"}


diccAltDisparoYDesc={
	38:["t21.L6"],
	37:["t11.L6"],
	36:["t22.L6","t21_12.L6"],
	35:["t12.L6","t11_22.L6"],
	34:["t23.L6","t22_13.L6"],
	33:["t13.L6","t12_23.L6"],
	32:["t24.L6","t23_14.L6"],
	31:["t14.L6","t13_24.L6"],	
	30:["t25.L6","t24_15.L6"],
	29:["t15.L6","t14_25.L6"],	
	28:["t26.L6","t25_16.L6"],
	27:["t16.L6","t15_26.L6"],	
	26:["t27.L6","t26_17.L6"],
	25:["t17.L6","t16_27.L6"],	
	24:["t28.L6","t27_18.L6"],
	23:["t18.L6","t17_28.L6"],	
	22:["t29.L6","t28_19.L6"],
	21:["t19.L6","t18_29.L6"],	
	20:["t210.L6","t29_110.L6"],
	19:["t110.L6","t19_210.L6"],	
	18:["t211.L6","t210_111.L6"],
	17:["t111.L6","t110_211.L6"],
	16:["t212.L6","t211_112.L6"],
	15:["t112.L6","t111_212.L6"],

	#NOTA: Algunas transiciones como t24 y t14 se agregan luego de 
	# que se agregan los lugares compartidos en el metodo _completarVias()
	14:["t24"],
	13:["t14"],
	12:["t25A"],
	11:["t24A"],
	10:["t30A","t30B"],
	9:["t31.L2"],
	8:["t32.L2"],
	7:["t33.L2"],
	6:["t34.L2"],
	5:["t35.L2"],
	4:["t36.L2"],
	3:["t37.L2"],
	2:["t38.L2"],
	1:["t39.L2"]
}



#Se mantiene un diccionario con los nombre de ViaMultiple a los que se puede acceder
viasCircHabilitadasViaYDesc=[ "viaX"]

###################################################################################################
################################ Alternativas de disparo para la viaYAsc ##########################
###################################################################################################

diccInicioViaYAsc={ 1: "p10"}
diccFinViaYAsc={ 1:"p35.L5"}

diccAltDisparoYAsc={
	1:["t35.L5"],
	2:["t34.L5"],
	3:["t33.L5"],
	4:["t32.L5"],
	#Se tiene que pasar por el lugar t24 para llegar al final de la via.
	5:["t16"],
	6:["t26"],
	7:["t13.L3"],
	8:["t12.L3"],
	9:["t11.L3"]
}

#Se mantiene un diccionario con los nombre de ViaMultiple a los que se puede acceder.
viasCircHabilitadasViaYAsc=[]

#Arreglo de diccionarios que mantiene el orden de disparo de las transiciones que pertenecen al semaforo.
ordenTransicionesSemaforos={
	1:"t22",
	2:"t23",
	3:"t24",
	4:"t25",
	5:"t26",
	6:"t27",
	7:"t28",
	8:"t29"
}

# Informacion acerca de la disposicion de las Areas de la simulacion. La informacion se organiza de la sig. forma:
# 	-Cada entreda del dicionario DATOS_DE_AREAS tiene campos que representan el nombre de la ViaMultiple en la simulacion.
# 	-Cada viaMultiple tiene los nombres de los lugares que pertenecen al area y tienen que refrescarse.
# Esta informacion es utilizada por la vista para el dibujado de los elementos sobre el diccionario.
# 
DATOS_DE_AREAS={
	#INTERSECCION.
	# 				*De LINK 1: p18.L1 (p28.L1), p14,p15,p16 (p24,p25,p26).
	# 				*De Link 2: p30.L2, p31.L2.
	# 				*De Link 3: p13.L3, p12.L3.
	# 				*De Link 4: p17.L4, p18.L4,p19.L4 (p27.L4, p28.L4, p29.L4).
	#				*De LINK 5: p32.L5, p33.L5.
	#				*De LINK 6: p111.L6, p112.L6 (p211.L6, p212.L6)
	"INTERSECCION":{
				#TODO: Corregir esto para que haya una clave "lugares" que contenga a "viaX","viaYDesc" y "viaYAsc"

				#L1
				"viaX":[
					"p18.L1","p28.L1",
					"p14","p15","p16", "p24","p25","p26",
					"p17.L4","p18.L4","p19.L4","p27.L4","p28.L4","p29.L4"
				],
				#L6
				"viaYDesc":[
					"p111.L6", "p112.L6",
					"p211.L6", "p212.L6",
					"p30.L2","p31.L2"
				],
				#L3,L5
				"viaYAsc": [
					"p13.L3","p12.L3",
					"p32.L5","p33.L5"
				],
				"pathImagen":"data/Interseccion.jpg",
				# Solo el area que abarca los semaforos mantiene una coleccion a sus id's.
				"contieneSemaforos":True,
				"semaforos": [
							"semaforoLink1",
							"semaforoLink3",
							"semaforoLink6"
				]
	},


	# *AREA_L1_1 (Ingreso de trafico a L1). Se contemplan los lugares desde p10 hasta p17.L1
	# (p20 hasta p27.L1).
	"AREA_L1":{
			"viaX":[
				"p10","p20",
				"p11.L1","p12.L1","p13.L1","p14.L1","p15.L1","p16.L1","p17.L1",
				"p21.L1","p22.L1","p23.L1","p24.L1","p25.L1","p26.L1","p27.L1"
			],
			"pathImagen":"data/Area_L1_V2.jpg",
			"contieneSemaforos":False
	},

	# *AREA_L2_L3: 
		# *De LINK 3: p11.L3,p10.
		# *De LINK 2: Se contemplan los lugares de p32.L2 hasta p37.L2.
		# NOTA: Se omiten los lugares p38.L2, p39.L2 de la grafica por cuestiones de simplicidad.
	"AREA_L2_L3":{

		"viaYDesc":[
			"p32.L2","p33.L2","p34.L2","p35.L2","p36.L2","p37.L2"
		],
		"viaYAsc":[
			"p10","p11.L3"
		],
		"pathImagen":"data/Area_L2_L3.jpg",
		"contieneSemaforos":False

	},
	# AREA_L4 (Salida de la interseccion). Se contemplan lugares de p110.L4 a p118.L4 (p210.L4, p218.L4).
	"AREA_L4":{
		"viaX":[
			"p110.L4","p111.L4","p112.L4","p113.L4","p114.L4","p115.L4","p116.L4","p117.L4","p118.L4",
			"p210.L4","p211.L4","p212.L4","p213.L4","p214.L4","p215.L4","p216.L4","p217.L4","p218.L4"
		],
		"pathImagen":"data/Area_L4.jpg",
		"contieneSemaforos":False
	},
	#NOTA: Las areas AREA_L6_L5_1 y AREA_L6_L5_2 utilizan la misma imagen, ya que es la misma cantidad de lugares.
	# 
	# *AREA_L6_L5_1 (Ingreso al Link 6). Se contemplan los lugares p14.L6 hasta p10 (p24.L6 hasta P20).
	# 

	"AREA_L6_L5_1":{

		"viaYDesc":[
			"p10","p20",
			"p11.L6","p12.L6","p13.L6","p14.L6",
			"p21.L6","p22.L6","p23.L6","p24.L6"
		],
		"pathImagen":"data/AreaL6L5.jpg",
		"contieneSemaforos":False
	},


	#  *AREA_L6_L5_2 (Continuacion del ingreso a LINK 6). Se contemplan lugares p110.L6 hasta p15.L6. Esta
# area tambien contempla el lugar p34.L5 del LINK 5.
	"AREA_L6_L5_2":{

		"viaYDesc":[
			"p15.L6","p16.L6","p17.L6","p18.L6","p19.L6","p110.L6",
			"p25.L6","p26.L6","p27.L6","p28.L6","p29.L6","p210.L6"
		],
		"viaYAsc":[
				"p34.L5",
				"p35.L5"
		],
		"pathImagen":"data/AreaL6L5.jpg",
		"contieneSemaforos":False
	}

}
# VARIABLE GLOBAL PARA INDICAR UNA CANTIDAD DE VEHICULOS INVALIDA
CANT_NO_CONTABILIZADA="a"

# Constantes usadas para la validacion de cantidad de ciclos ingresados por el usuario
CANT_MINIMA_CICLOS_INGRESADOS_USR=1
CANT_MAXIMA_CICLOS_INGRESADOS_USR=20

################################### Variables Globales usadas para la configuracion de cada via multiple ###################################
# Estos valores luegos seran configurados y manipulados por los modulos que leen archivos json.
dicEsquemas={}
dicTraficoPredefinido={}




