""" Este modulo mantiene todos los getters y setters de la via multiple."""
import copy
# Se agrega una referencia a la simulacion desde la viaMultiple. Esto permite que el generadorTrafico de la via
# detecte en cada ciclo que temporiza la via, si la simulacion termino.
def getSimulacion(self):
	""" Metodo getter para el atributo 'simulacion'.
		@return: La simulacion a la que pertenece la via multiple
		@rtype: Simulacion """
	return self.simulacion

#ViaMultiple.setSimulacion()
def setSimulacion(self,simul):
	""" Metodo setter para el atributo 'simulacion'.
		@param simul: Simulacion a la que pertenece la via multiple
		@type simul: Simulacion """	
	self.simulacion=simul

def setGeneradorTrafico(self,genTraf):
	""" Metodo setter para el atributo 'generadorTrafico'.
		@param genTraf: Generador de trafico al que la simulacion pertenece
		@type genTraf: GeneradorTrafico"""
	self.generadorTrafico=genTraf

def getGeneradorTrafico(self):
	""" Metodo getter para el atributo 'generadorTrafico'.
		@return: El generador de trafico de la via multiple
		@rtype: GeneradorTrafico"""
	return self.generadorTrafico

def getDuracionFaseEnVia(self,nombreFaseSemaforo):
	""" En base a un nombre de fase en via, se retorna el valor de la duracion de la fase 
		en que se tiene que registrar  el trafico.
		@param nombreFaseSemaforo: Nombre de la fase del semaforo
		@type nombreFaseSemaforo: String """
	if nombreFaseSemaforo=="EnAvance" or nombreFaseSemaforo=="EnAvanceConPrecaucion":
		return self.fasesARegistrar["fase_verde_amarilla"]
	else:
		return self.fasesARegistrar["fase_roja"]

# viaMultiple.getCantTransicionesLink()
def getCantTransicionesLink(self):
	""" Metodo getter para el atributo 'cantTransicionesLink'.
		@return: La cantidad de transiciones de un link
		@rtype: Integer """
	return self.cantTransicionesLink


# ViaMultiple.setFasesTemporizadas()
def setFasesTemporizadas(self,nroCiclo):
	""" Este metodo se utiliza para marcar a un numero de ciclo como temporizado completamente, es decir, que
		sus todas sus fases ya se han temporizado.
		@param nroCiclo: Numero de ciclo cuyas fases ya se han temporizado completamente.
		@type nroCiclo: Integer """
	self.fasesTemporizadas[nroCiclo]=True

# ViaMultiple.getFasesTemporizadas()
def getFasesTemporizadas(self):
	""" Metodo getter para el atributo 'fasesTemporizadas'.
		@return: La cantidad de fases que se han temporizado hasta el momento
		@rtype: Integer """
	return self.fasesTemporizadas

def getNombreSemaforoLink(self):
	""" Metodo getter para el atributo 'nombreSemaforoLink'.
		@return: Nombre del semaforo que controla el link de entrada ubicado en la via multiple
		@rtype: String """
	return self.nombreSemaforoLink

def getCantCarriles(self):
	""" Metodo getter para el atributo 'cantCarriles'.
		@return: La cantidad de carriles de la via multiple
		@rtype: Integer """
	return self.cantCarriles

def getDicEstadisticas(self):
	""" Metodo getter para el atributo 'dicEstadisticas'.
		@return: El diccionario de las estadisticas recolectadas para la via multiple
		@rtype: Diccionario """
	return self.dicEstadisticas

def setDicEstadisticas(self,dic):
	""" Metodo setter para el atributo 'dicEstadisticas'.
		@param dic: Estadisticas
		@type dic: Diccionario """
	self.dicEstadisticas=dic

def getDiccTraficoPredefinido(self,cicloActual):
	""" Retorna el trafico para un numero de ciclo pasado por parametro.
		@param cicloActual: Numero de ciclo para el que se solicitara la cantidad de vehiculos.
		@type cicloActual: Integer"""
	return self.trafPredefinido[cicloActual]

# ViaMultiple.getNombre()
def getNombre(self):
	""" Metodo getter para el atributo 'nombre'.
		@return: El nombre de la via multiple
		@rtype: String """
	return self.nombre

# ViaMultiple.getNodosInicio()
def getNodosInicio(self):
	""" Metodo getter para el atributo 'nodosInicio'.
		@return: Los nodos de inicio (aquellos por los que ingresan los vehiculos).
		@rtype: Diccionario """
	return self.nodosInicio

# ViaMultiple.getNodosFin()
def getNodosFin(self):
	""" Metodo getter para el atributo 'nodosFin'.
		@return: Los nodos de fin (aquellos por los que los vehiculos son despachados
		de la simulacion).
		@rtype: Diccionario """
	return self.nodosFin


#viaMultiple.getRedPetri() 	
def setRedPetri(self,red):
	""" Metodo setter para el atributo 'PetriNet'.
	@param red: Red de Petri que se seteara
	@type red: PetriNet """
	self.bloqueo.acquire()
	self.redPetri=red
	self.bloqueo.release()

#viaMultiple.getRedPetri() 
def getRedPetri(self):
	""" Metodo getter para el atributo 'redPetri'.
		@return: La red de Petri que mantiene una via multiple
		@rtype: PetriNet """
	self.bloqueo.acquire()
	copia=copy.copy(self.redPetri)
	self.bloqueo.release()
	return copia
	
def setSemaforo(self,sem):
	""" Metodo setter para el atributo 'semaforo'.
		@param sem: Referencia al semaforo de la via multiple.
		@type sem: Semaforo """		
	self.semaforo=sem

def getSemaforo(self):
	""" Metodo getter para el atributo 'semaforo'.
		@return: Semaforo que regula la circulacion de los vehiculos de la via multiple
		@rtype: Semaforo """
	return self.semaforo

def setTransicionesSalidaLink(self,transiciones):
		""" Metodo setter para el atributo 'transicionesSalidaLink'.
			@param transiciones: Listado de transiciones de salida
			@type transiciones: List """
		self.transicionesSalidaLink=transiciones