""" Este modulo define la clase GeneradorTrafico."""
import threading
import logging
import time

class GeneradorTrafico():
	""" Esta clase se encarga de recibir los eventos de cambio de ciclo y de cambio de estado de un semaforo,
		y de controlar e indicar a la via multiple cuando se tiene que introducir el trafico en los nodos de inicio.
		Tambien envia a la via multiple datos necesarios para que esta finalice y registre los datos estadisticos."""
	def __init__(self,simulacion,via):
		""" Metodo constructor de GeneradorTrafico.
			@param simulacion: Simulacion a la que pertenece
			@type simulacion: Simulacion
			@param via: Via multiple sobre la que administran el trafico
			@type via: ViaMultiple """
		self.simulacion=simulacion
		#Se mantiene el nro de ciclo actual que se incrementa con cada temporizacion.
		#Esto permite solicitarle a la simulacion en base al nro de ciclo que se tiene que 
		# temporizar y a la ViaMultiple, la temporizacion de los semaforos en cada fase.
		self.cicloActual=0
		self.viaMultiple=via

	# GeneradorTrafico.getViaMultiple()	
	def getViaMultiple(self):
		""" Metodo getter para el atributo 'viaMultiple'.
			@return: Via multiple en la que el generador de trafico opera
			@rtype: ViaMultiple """
		return self.viaMultiple

	# GeneradorTrafico.getCicloActual()
	def getCicloActual(self):
		""" Metodo getter para el atributo 'cicloActual'.
			@return: El ciclo de tiempo actual al momento de invocar al metodo
			@rtype: Integer """
		return self.cicloActual

	# GeneradorTrafico.manejadorCambioCiclo()
	def manejadorCambioCiclo(self,mensajero):
		""" Handler para cuando la redSemaforos notifica que cambio el ciclo. 
			@param mensajero: Red de semaforos
			@type mensajero: RedSemarofos """
		# Se inicia un nuevo Thread para que temporice los ciclos
		nombreThread="Thread-GeneradorTrafico-"+str(self.getViaMultiple().getNombre())
		t=threading.Thread(target=self.actualizarCiclo,name= nombreThread,args=(mensajero,))
		t.setDaemon(True)
		t.start()

	# GeneradorTrafico.actualizarCiclo()
	def actualizarCiclo(self,mensajero):
		""" Este metodo solicita a la RedDeSemaforos el nroCicloActual y actualiza la referencia actual al mismo que posee.
			Esto se utiliza para que el GeneradorTrafico de cada viaMultiple, sepa que intervaloIngresoVehiculos 
			y duracionFase debe solicitar en el ciclo actual y con esto calcular la cantidad de temporizaciones.

			@param mensajero: Se envia la referencia a la redDeSemaforos (o "mensajero") que produjo el evento.
			@type mensajero: RedSemarofos """
		logging.debug("DESPERTE! generando trafico por %s " % self.viaMultiple.getNombre())
		logging.debug("")
		# Si la simulacion termino, no se adquiere el bloqueo, y se termina antes de tiempo la temporizacion
		# de la viaMultiple.
		if self.viaMultiple.getSimulacion().terminoSimulacion():
			logging.debug("En generadorTrafico.run()! La simulacion ya termino! Saliendo desde generadorTrafico %s..." % self.viaMultiple.getNombre() )
			logging.debug("")
			return
		self.cicloActual=mensajero.getNroCicloActual()
		logging.debug("numero de ciclo actualizado a: "+str(self.cicloActual))
		logging.debug("")
		logging.debug("self.cicloActual="+str(self.cicloActual)+"; RedDeSemaforos.cantCiclos="+str(self.simulacion.getRedSemaforos().getCantCiclos()))
		logging.debug("")
		# Si el ciclo a temporizar es mayor o la simulacion termino, no se continua.
		if self.cicloActual > self.simulacion.getRedSemaforos().getCantCiclos():
			logging.debug("Terminando la generacion de trafico en GeneradorTrafico.run() !!!")
			logging.debug("")
			return
		logging.debug("====================== Fin de generadorTrafico.run() de viaMultiple: "+self.viaMultiple.getNombre()+" ======================")
		logging.debug("")
		return

	# GeneradorTrafico.manejadorCambioEstado()
	def manejadorCambioEstado(self,mensajero):
		""" Este metodo se encarga de recibir el evento de cambio de estado de un semaforo,  que es producido
			por el mismo y  este temporiza el ciclo y el estado que sea necesario. """
		estado=mensajero.getEstado().getNombre()
		logging.debug("NroCiclo: %s Se registro el cambio de estado al estado: %s " % (self.cicloActual,estado))
		logging.debug("")
		if self.cicloActual==0:
			self.cicloActual+=1
		self.temporizarCiclo(self.cicloActual,estado)
 
	# generadorTrafico.temporizarCiclo()
	def temporizarCiclo(self,cicloActual,estado):
		""" Este metodo con informacion del estado de un semaforo, calcula la cantidad de veces que se puede temporizar
			con un intervalo dado y realiza esas temporizaciones. Luego si resta esperar un tiempo en dicha fase de semaforo
			temporiza ese tiempo.
			@param cicloActual: Numero de ciclo que se temporizara
			@type cicloActual: Integer
			@param estado: Estado del semaforo que pertence a la via multiple que gestiona el generador de trafico
			@type estado: String """
		logging.debug("Via DESPERTADA! Cambio el estado del semaforo en ciclo: "+str(cicloActual))
		logging.debug("")
		logging.debug(" NroCiclo: "+str(cicloActual)+"; Estado del semaforo:="+str(estado))
		logging.debug("<<----------------------------------------------------------------->>")
		logging.debug("")
		(tiempo,duracionFase)=self._obtenerIntervalo(estado)
		# Se verifica si todas las fases en el ciclo fueron actualizadas y se marcan si es asi!
		if self.viaMultiple.estanTodasFasesTemporizadas(cicloActual):
			logging.debug("Todas las fases del ciclo : "+str(cicloActual) + " temporizadas correctamente!!")
			logging.debug("")
			self.viaMultiple.setFasesTemporizadas(cicloActual)
			logging.debug("Despues de _obtenerIntervalo(), dicFasesTemporizadas actualizado: "+
				str(self.viaMultiple.getFasesTemporizadas()))
			logging.debug("")
		# Si se esta en un estado que tiene un tiempo (intervaloIngresoVehiculos) para temporizar,
		# se calculan las cantidad de temporizaciones de X seg.
		if tiempo>0:
			logging.debug(" Despues de llamar a obtenerIntervalo(), se retorno (tiempoIngreso,duracionFase)=("+
				str(tiempo)+","+str(duracionFase)+")" )
			logging.debug("")
			# Se calculan las cantidades de temporizaciones en base al intervaloIngresoVehiculos ("tiempo") de la viaMultiple
			# en un ciclo y, a la duracion de la fase, la cantidad de temporizaciones de intervaloIngresoVehiculos
			# que se deben hacer dentro de la fase.
			(cantTemporizaciones,tiempoSobrante)=self.calcularCantTemporizaciones(duracionFase,tiempo)
			logging.debug("cantTemporizaciones= "+str(cantTemporizaciones)+"; tiempoSobrante= "+str(tiempoSobrante))
			logging.debug("")
			duracionFaseVia=0
			if self.viaMultiple.seDebeContabilizarTrafico(str(estado)):
				logging.debug("Contabilizando vehiculos: estado del semaforo="+str(estado)+
					"; nroCicloActual= "+str(cicloActual+1))
				logging.debug("")
				# Esta "duracionFaseVia" es usada con fines estadisticos.
				duracionFaseVia=self.viaMultiple.getDuracionFaseEnVia(str(estado))
				self.viaMultiple.incrementarEstadisticas2(cicloActual+1,cantTemporizaciones,tiempo,duracionFaseVia,str(estado))
			else:
				logging.debug("Los vehiculos no se contabilizan: estado del semaforo="+str(estado)+
					"; nroCicloActual= "+str(cicloActual+1))
				logging.debug("")

			# Se temporizan la cantTemporizaciones de "tiempo" en una fase determinada.
			for i in xrange(1,int(cantTemporizaciones)+1):
				logging.debug("Esperando en via "+str(self.viaMultiple.getNombre())+" ...")
				logging.debug("")
				# Se espera intervaloIngresoVehiculos ("tiempo").
				time.sleep(tiempo)
				logging.debug("Trafico generado en la via "+str(self.viaMultiple.getNombre())+
					" en el instante: "+str(tiempo* i))
				logging.debug("")
				logging.debug("Generando el trafico de la via: "+str(self.viaMultiple.getNombre()))
				logging.debug("")
				#Se le pide  a la viaMultiple que originar el trafico en sus nodos de inicio.
				self.viaMultiple.originarTrafico(cicloActual+1)
				logging.debug("Luego de generadorTrafico.actualizarEstadisticas()!")
				logging.debug("")
		logging.debug("Termino temporizarCiclo()!!")
		logging.debug("")

	# generadorTrafico._obtenerIntervalo().
	def _obtenerIntervalo(self,estado,nroCiclo=None):
		""" Este metodo obtiene FTinput (tiempos de disparo de las transiciones de entrada
			para los vehiculos) segun la definicion de la tabla de escenario(escenario 1 o escenario 2).
			
			@param estado: Estado que representa al semaforo
			@type estado: String
			@param nroCiclo: Numero de ciclo para el que se temporizara. Si no se especifica un ciclo por parametro,
			se obtiene el intervalo para el ciclo actual.
			@type nroCiclo: Integer 
			@return: Retorna una tupla con el intervaloIngreso de vehiculos y la duracion de la fase de semaforo
			total en esa ViaMultiple.
			@rtype: Tuple """
		tiempo=0
		duracion=0
		cicloActual=self.cicloActual
		if nroCiclo!=None:
			cicloActual=nroCiclo
		# Se obtiene de la viaMultiple el dic. de trafico predefinido de la ViaMultiple.
		diccTraf=self.viaMultiple.getDiccTraficoPredefinido(cicloActual)
		logging.debug("En _obtenerIntervalo, diccTraf leido con nroCiclo: "+str(cicloActual)+" es:  ")
		logging.debug(str(diccTraf))
		logging.debug("")
		if estado=='EnAvance' or estado=='EnAvanceConPrecaucion' :
				tiempo=diccTraf["fase_verde_amarilla"]["intervaloIngresoVehiculos"]
				duracion=diccTraf["fase_verde_amarilla"]["duracionTotalFase"]
				#Se actualiza el estado de la fase!
				diccTraf["fase_verde_amarilla"]["estaTemporizada"]=True
		elif estado=='Detenido':
					tiempo=diccTraf["fase_roja"]["intervaloIngresoVehiculos"]
					duracion=diccTraf["fase_roja"]["duracionTotalFase"]
					diccTraf["fase_roja"]["estaTemporizada"]=True
		# Se actualiza el nuevo estado del dic. de trafico predefedinido de la viaMultiple.
		self.viaMultiple.actualizarDiccTraficoPredefinido(cicloActual,diccTraf)
		return (tiempo,duracion)

	def calcularCantTemporizaciones(self,duracionFase,duracionIntervalo):
		""" Este metodo calcula la cantidad de temporizaciones que se pueden hacer 
			dado un intervalo de temporizacion (frecuencia de ingreso de vehiculos a la via)
			y la duracion de la fase ( fase_roja o fase_verde_amarrilla). 

			@param duracionFase: Duracion de una fase en segundos
			@type duracionFase: Integer
			@param duracionIntervalo: Duracion de un intervalo de ingreso de vehiculos a la via en segundos
			@type duracionIntervalo: Integer
			@return: La cantidad de temporizaciones y el resto de la division (es el tiempo
					que no alcanza para que ingrese trafico nuevo,
					y se debe esperar antes de preguntar por el estado del semaforo.)
			@rtype: Tuple """
		# Se utiliza la division entera para la cantidad de temporizaciones que deben hacerse de "duracionIntervalo"
		# y se calcula el resto de la division para conocer el tiempoEspera (sin producir ningun vehiculo).
		cantTemporizaciones=int(duracionFase // duracionIntervalo)
		tiempoEspera=0
		# Si hay que temporizar en este ciclo un tiempo>0, se obtiene el resto.
		if cantTemporizaciones > 0:
			tiempoEspera=float(duracionFase % duracionIntervalo)
		return (cantTemporizaciones, tiempoEspera)