""" Este modulo contiene las modificaciones y las extensiones efectuadas a la red de Petri, 
    para adaptarla al problema actual. Las clases que contiene son PetriNet,Transition,Place y TransicionTemporizada.
    Para que estas extensiones se tomen por la libreria, este modulo se debe guardar en la siguiente ruta:
    /usr/local/lib/python2.7/dist-packages/snakes/plugins """

from snakes.nets import *
import traceback
import threading
import logging
import time
logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-9s) %(message)s',)

@snakes.plugins.plugin("snakes.nets")
def extend (module) :
    "Extends `module`"
    class Transition (module.Transition):
        """ Esta clase representa una transicion de la red de Petri y se utiliza para el armado de las transiciones
            que pertenecen a las vias multiples. Esta clase extiende la funcionalidad estandar de una transicion comun
            en la red de Petri (consumir tokens en los lugares que tienen arcos de entrada y producir tokens en los lugares 
            de salida a la transicion), incorporando metodos que pueden obtener el token (vehiculo) que se disparo en cada lugar
            y manipularlo para cambiar su color o la cuadricula en la que se encuentra ubicado. """
        
        def __init__ (self, name, guard=None) :
            """Add new keyword argument `hello`

            >>> PetriNet('N').hello()
            Hello from N
            >>> PetriNet('N', hello='Hi! This is %s...').hello()
            Hi! This is N...
            @param args: plugin options
            @keyword hello: the message to print, with
                `%s` where the net name should appear.
            @type hello: `str`
            """
            #NOTA: Este es el delay  que tiene que tardar la transicion en dispararse
            #y  varia segun el tipo de vehiculo (automovil | colectivo).
            self.delay=0
            module.Transition.__init__(self, name, guard)

    
        def setDelay(self,delay):
            """ Metodo setter para el atributo 'delay'.
                @param delay: Delay de la transicion actual en segundos
                @type delay: Integer """
            self.delay=delay

        def getDelay(self):
            """ Metodo getter para el atributo 'delay'
                @return: El delay en segundos para una transicion
                @rtype: Integer """
            return self.delay

        # Transition.disparar()
        def disparar(self, binding):
            """ Este metodo realiza el disparo de la transicion y actualiza los atributos del vehiculo que se desplazo
                segun corresponda.
                @param binding: Coleccion de substituciones a realizar para los arcos de entrada y salida de la transicion
                @type binding: Lista de Substitution """
            try:
                logging.debug("===========En transicion.disparar() ============")
                logging.debug("")
                #Se le solicita al objeto substitucion que retorne la referencia al objeto
                #NOTA. La funcion image() retorna una lista de los objetos asociados a una substitucion            
                #Se solicita el coche a la substitucion y si se obtiene, se lo avanza una posicion!
                coche=None
                coche=self.obtenerVehiculo(binding)
                if coche!=None:
                    #Se cambia el lugar en la RP a la que pertenece el vehiculo.
                    lugSalida=self.obtenerLugEnVia("salida")
                    #Se actualizan los colores del vehiculo.
                    coche.actualizarColores(lugSalida)
                    coche.avanzarALugar(lugSalida)
                    logging.debug( "Vehiculo "+str(coche.getIdVehiculo())+" desplazado al lugar "+str(lugSalida)+
                        ": X="+str(coche.getLugarRP().getCuadricula().getPosicion().getX())+
                        "; Y= "+str(coche.getLugarRP().getCuadricula().getPosicion().getY()) )
                    logging.debug("")
                #Se realiza el disparo de todas las substituciones con fire()
                for subst in binding:
                    logging.debug("Disparando:"+str(subst))
                    logging.debug("")
                    self.fire(subst)
                logging.debug("===========Fin de transicion.disparar() ===========")
                logging.debug("")        
            except Exception, e:
                logging.debug("")
                logging.debug("---------------------------------------------------------")
                logging.debug("EXCEPCION EN t.disparar(): ")
                logging.debug("---------------------------------------------------------")
                logging.debug(e)
                logging.debug("")

        def estaSigLugarVacio(self):            
            """ Este metodo verifica si el siguiente lugar esta vacio.
                @return: Valor indicando si esta vacio el siguiente lugar
                @rtype: Boolean """
            #Se obtiene la salida de la transicion (en reaidad es una coleccion de las salidas a la transicion.)
            #NOTA: self.output() retorna una tupla con el lugar de salida y la expression. Se accede solamente al lugar 
            #direccionando a 0 en la tupla.
            #Se toma un solo lugar ya que cada transicion solamente tiene un solo lugar de salida.
            lugarTentativo=self.obtenerLugEnVia("salida")
            if lugarTentativo.is_empty():
                return True
            else:
                return False

        # Transition.existenSubstituciones()
        def existenSubstituciones(self):
            """ Este metodo permite determinar si existen substituciones para una transicion determinada.
                @return: Un valor indicando si existen substituciones para consumir y producir tokens
                @rtype: Boolean """
            result=False
            if len(self.modes())>=1:
                result=True
            return result

        def obtenerLugEnVia(self,tipoLugar):
            """ Este metodo retorna el siguiente lugar en la via de circulacion que no es un "lugarCompartido"
                @param tipoLugar: El tipo de lugar (un lugar con arcos de entrada o de salida a la transicion)
                @type tipoLugar:  String
                @return: El siguiente lugar en la via multiple
                @rtype: Place """
            lugares=None
            if tipoLugar=="entrada":
                lugares=self.input()
            elif tipoLugar=="salida":
                lugares=self.output()
            for lugSiguiente in lugares:
                    if lugSiguiente[0].estaEnViaCirculacion():
                        return lugSiguiente[0]

        def obtenerVehiculo(self,bindings):
            """ Este metodo retorna el vehiculo asociado a la substitucion. Es usado por las transiciones especiales
                que mueven tanto los tokens enteros (usados para relacionar una via multple con un semaforo),
                como asi tambien los objetos vehiculo.
                @param bindings: Coleccion de substituciones
                @type bindings: Lista de Substitution """
            #Se guardan los tokens en una lista
            tokens=[]
            for subst in bindings:
                elementosLugar=subst.image()
                for e in elementosLugar:
                    tokens.append(e)
            for elem in tokens:
                if type(elem).__name__=='Vehiculo':
                    return elem
            return None

    class TransicionTemporizada (module.Transition):
        """ Esta clase define a las transiciones que son usadas durante los "tiempos de ciclo" en el semaforo
            de la Red de Petri en la red de semaforos.
            Realiza su propia temporizacion en base a la fase (en seg.) que tiene asignada. """
        def __init__ (self, name, guard=None) :
            """Add new keyword argument `hello`

            >>> PetriNet('N').hello()
            Hello from N
            >>> PetriNet('N', hello='Hi! This is %s...').hello()
            Hi! This is N...
            @param args: plugin options
            @keyword hello: the message to print, with
                `%s` where the net name should appear.
            @type hello: `str`
            """
            #Este atributo determina si la transicion es una transicion oblicua
            self.transOblicua=False
            self.duracionFase=0
            #Todas las transiciones del semaforo mantienen una lista de los semaforos
            # a los que deben indicar que modifiquen el estado. 
            self.semaforos=[]
            module.Transition.__init__(self, name, guard)

        # TransicionTemporizada.temporizar()
        def agregarSemaforo(self,sem):
            """ Este metodo agrega un semaforo a la coleccion de semaforos de la transicion temporizada.
                @param sem: Semaforo a agregar
                @type sem: Semaforo """
            self.semaforos.append(sem)

        # TransicionTemporizada.temporizar()
        def setDuracionFase(self,duracion):
            """ Metodo setter para el atributo 'duracion'.
                @param duracion: Duracion en segundos de la fase de la transicion.
                @type duracion: Integer """
            self.duracionFase=duracion
        
        # TransicionTemporizada.temporizar()
        def temporizar(self,enDebugging=True):
            """ Este metodo duerme el hilo de ejecucion de la RP de los semaforos y luego
                notifica a los semaforos que avancen al siguiente estado.
                @param enDebugging: Flag indicando si se deben mostrar los mensajes producidos por la temporizacion 
                de la transicion
                @type enDebugging: Boolean """
            if enDebugging:
                logging.debug("===================== Inicio de TransicionTemporizada.temporizar()===================== ")
                logging.debug("")
                logging.debug("Esperando fin de transicion: "+str(self.name)+" ...")
                logging.debug("")
            time.sleep(self.duracionFase)
            if enDebugging:
                logging.debug("Fin de temporizacion de transicion: "+str(self.name))
                logging.debug("")
            #Se dispara la transicion!
            subst=self.modes()[0]
            self.fire(subst)
            # Se modifica primero el estado de los semaforos
            for sem in self.semaforos:
                if enDebugging:
                    logging.debug( "Modificando semaforo: "+str(sem.getNombre())+"...")
                    logging.debug( "")
                sem.cambiarASigEstado()
                
                # Se notifica del cambio de estado a la viaMultiple afectada por el semaforo
                sem.notificarAViaMultiple()
                logging.debug("El semaforo "+str(sem.getNombre())
                    +" de la transicion: "+str(self)+ " notifico a su generadorTrafico!")
                logging.debug("")

            if enDebugging:
                logging.debug("TRANSICION "+str(self.name)+" DISPARADA!!!")
                logging.debug("")
                logging.debug("")
                logging.debug("===================== Fin de TransicionTemporizada.temporizar()===================== ")
                logging.debug("")
                logging.debug("")

    class Place(module.Place):
        """ Esta clase se extiende para que cada lugar mantenga la referencia a una cuadricula(con posX y posY)
        y asi cuando se dispare la transicion, poder cambiar la posicion fisica del vehiculo con la 
        cuadricula del lugar al que se dispara la transicion. """
        def __init__ (self, name, tokens=[], check=None):
            """Add new keyword argument `hello`

            >>> PetriNet('N').hello()
            Hello from N
            >>> PetriNet('N', hello='Hi! This is %s...').hello()
            Hi! This is N...

            @param args: plugin options
            @keyword hello: the message to print, with
                `%s` where the net name should appear.
            @type hello: `str` """
            #El lugarRP mantiene la referencia a la via de circulacion a la que pertence.
            #NOTA: Cada lugar en la RP solamente pertenece a una sola via de circulacion, aunque
            # otras vias multiples puedan hacer referencia a ella.
            # De ahi puede obtener el sentido de circulacion, el angulo de rotacion que tienen que tener los vehiculos.
            self.viaCirculacion=None
            self.cuadricula=None
            self.enViaCirculacion=False
            #Solo los lugares inicio que introducen crean el vehiculo tienen establecido
            # la ruta del icono del vehiculo.
            self.pathIcono=None
            #Cada lugar mantiene la referencia al streamSet al que
            # se encuentra asociado.
            self.streamSet=None
            #Esta flag permite determinar si un lugar es compartido por mas de una viaMultiple
            # self.esLugarCompartido=False
            #Se establece el atributo del bloqueo.
            self.bloqueo=None
            module.Place.__init__(self,name, tokens=tokens,check=check)

        
        def getPathIcono(self):
            """ Metodo getter para el atributo 'pathIcono'
                @return: El path del icono para el lugar actual.
                @rtype: String """
            return self.pathIcono

        def setPathIcono(self,s):
            """ Metodo setter para el atributo 'pathIcono'.
                @param s: Path del icono
                @type s: String """
            self.pathIcono=s

        def getStreamSet(self):
            """ Metodo getter para el atributo 'streamSet'
                @return: Un streamset
                @rtype: StreamSet """
            return self.streamSet

        def setStreamSet(self,s):
            """ Metodo setter para el atributo 'streamSet'.
                @param s: Streamset a setear
                @type s: StreamSet """
            self.streamSet=s


        def estaEnViaCirculacion(self):
            """ Indica si un lugar esta en la via de circulacion.
                @return: un valor indicando si el lugar se encuentra en via de circulacion.
                @rtype: Boolean """
            return self.enViaCirculacion

        def setEnViaCirculacion(self,estado):
            """ Metodo setter para el atributo 'enViaCirculacion'.
                @param estado: Estado del lugar
                @type estado: Boolean """
            self.enViaCirculacion=estado

        def setCuadricula(self,cuadricula):
            """ Metodo setter para el atributo 'cuadricula'.
                @param cuadricula: Cuadricula a la que pertenece el lugar
                @type cuadricula: Cuadricula """
            self.cuadricula=cuadricula

        def getCuadricula(self):
            """ Metodo getter para el atributo 'cuadricula'
                @return: Cuadricula a la que pertenece el lugar
                @rtype: Cuadricula """
            return self.cuadricula

        def setViaCirculacion(self,via):
            """ Metodo setter para el atributo 'viaCirculacion'.
                @param via: Via de circulacion a la que pertenece el vehiculo
                @type via: ViaMultiple """
            self.viaCirculacion=via

        def getViaCirculacion(self):
            """ Metodo getter para el atributo 'viaCirculacion'
                @return: Via de circulacion a la que pertenece el lugar
                @rtype: ViaMultiple """
            return self.viaCirculacion


    class PetriNet (module.PetriNet) :
        """Esta clase es una extension de la clase PetriNet de Snakes, que extiende la funcionalidad de esta
            para identificar vias validas de movimiento de vehiculos y seguir un orden de disparo para las transiciones.
            El orden de disparo de las transiciones se encuentra definido en el modulo "constantes" y consiste en comenzar 
            a disparar las transiciones que se encuentran en los links de salida y proceder hasta llegar a las transiciones
            que se encuentran en los links de entrada.  """
        def __init__ (self, name, **args) :
            """Add new keyword argument `hello`

            >>> PetriNet('N').hello()
            Hello from N
            >>> PetriNet('N', hello='Hi! This is %s...').hello()
            Hi! This is N...

            @param args: plugin options
            @keyword hello: the message to print, with
                `%s` where the net name should appear.
            @type hello: `str`
            """
            self._hello = args.pop("hello", "Hello from %s")
            self.viaCirculacion=None
            #NOTA: EL metodo pop() remueve los argumentos (sin clave de la lista *args) en base a un nombre.
            #El seguno argumento que acepta pop() es el valor por defecto en caso de que no se especifique un valor.
            # self._tiempoTemporizacion=args.pop("tiempo", 12)            
            self._alternativasDeDisparo=None
            module.PetriNet.__init__(self, name, **args)


        
        def setAlternativasDeDisparo(self,diccAlternativas):
            """ Este metodo permite establecer los pares de transiciones que deben ser evaluados juntos. De esta forma se mantiene
                un orden de recorrido de las transicioens y una coherencia en el disparo. 
                @param diccAlternativas: Una coleccion de alternativas de disparo
                @type diccAlternativas: Diccionario
                EL diccionario pasado como argumento tiene la siguiente estructura:
                        diccAlernativas={ 1:{ "t1": t11, "t2":t13} }  """
            self._alternativasDeDisparo=diccAlternativas

        def getAlternativasDeDisparo(self):
            """ Metodo getter para el atributo '_alternativasDeDisparo'
                @return: Coleccion de alternativas de disparo
                @rtype: Diccionario """
            return self._alternativasDeDisparo

        def hello (self) :
            "Ask the net to say hello"
            print(self._hello % self.name)

        def setViaCirculacion(self,via):
            """ Metodo setter para el atributo 'viaCirculacion'.
                @param via: Via de circulacion a la que pertenece el vehiculo
                @type via: ViaMultiple """            
            self.viaCirculacion=via

        def getViaCirculacion(self):
            """ Metodo getter para el atributo 'viaCirculacion'
                @return: Via de circulacion a la que pertenece el lugar
                @rtype: ViaMultiple """            
            return self.viaCirculacion


        # PetriNet.temporizar()
        def temporizar(self,viaMultiple,enDebugging=False):
            """ Este metodo realiza el disparo de la red de petri segun un orden predefinido (self._alternativasDeDisparo), 
                con el sentido de circulacion del carril para el calculo del OFFSET en X o Y, con un intervalo de temporizacion. 
                @param viaMultiple: Via multiple que se temporizara
                @type viaMultiple: ViaMultiple
                @param enDebugging: Flag que indica si se deben mostrar los mensajes de debugging.
                @type enDebugging: Boolean """
            if enDebugging:
                logging.debug("")
                logging.debug("+++++++++++++++++++++En el For de redPetri.temporizar()+++++++++++++++++++++")
                logging.debug("")
                logging.debug("")

            for posicionRecorrido,alternativa in  self._alternativasDeDisparo.iteritems():
                while not alternativa.estanAltAgotadas():

                    t=alternativa.elegirTransicionAleatoria()

                    substituciones=t.modes()
                    if len(substituciones)>=1:

                        if enDebugging:
                            logging.debug("")
                            logging.debug("CANT. SUBSTITUCIONES: "+str(len(substituciones)) )
                            logging.debug("")
                        
                        #Si el vehiculo esta en una via valida, se procede a realizar la seleccion de 
                        # las alternativas de disparo.
                        if self.estaVehiculoEnViaValida(self.getViaCirculacion(),t.obtenerVehiculo(substituciones)):
                            #Si el sig. lugar esta vacio  y existen substituciones se deben agregar las posiciones "ficticias" del coche
                            #para la animacion. 
                            if t.estaSigLugarVacio()==False and t.existenSubstituciones()==True:
                                if enDebugging:
                                    logging.debug("")
                                    logging.debug( "TRANSICION FALLIDA!!: "+str(t)+" con lugares : "+str(t.output()))
                                    logging.debug("")
                                    logging.debug("t.existenSubstituciones(): "+str(t.existenSubstituciones()) )
                                    logging.debug("")
                                    logging.debug( "t.estaSigLugarVacio(): "+str(t.estaSigLugarVacio()) )
                                    logging.debug("")

                            elif t.estaSigLugarVacio()==True and t.existenSubstituciones()==True:
                                if enDebugging:
                                    logging.debug("TRANSICION EXITOSA! SE PUDO AVANZAR POR UNA ALERNATIVA!!!")
                                    logging.debug("")
                                    logging.debug(";Nombre transicion: "+str(t)+"; Tipo Transicion : "+str(type(t)))
                                    logging.debug("")
                                    logging.debug("")
                                    logging.debug( "t.existenSubstituciones(): "+str(t.existenSubstituciones()) )
                                    logging.debug("")
                                    logging.debug( "t.estaSigLugarVacio(): "+str(t.estaSigLugarVacio()) )
                                    logging.debug("")

                                #NOTA: Cada transicion tiene una sola substitucion (retornada por modes[] como arreglo)
                                # substitucion=t.modes()[0]
                                substituciones=t.modes()
                                if enDebugging:
                                    logging.debug("SUBSTITUCIONES DE LA TRANSICION "+str(t)+" son: "+str(substituciones))
                                    logging.debug("")

                                try:
                                    if enDebugging:
                                        logging.debug("")
                                        logging.debug("VEHICULO EN VIA VALIDA! Disparando transicion ...")
                                        logging.debug("")
                                        
                                    # Se dispara la transicion.
                                    t.disparar(substituciones)

                                    #AL disparar la transicion se resetea el arreglo de alternativas y
                                    #se rompe con el bucle de iteracion de busqueda de alternativas
                                    #para detener la busqueda.
                                    alternativa.resetearAlternativas()
                                    break
                                except Exception, e:
                                    logging.debug( "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><")
                                    logging.debug( "ERROR no se pudo disparar al transicion con la substitucion: "+str(substituciones))
                                    logging.debug( "Tipo de la substitucion: "+str(type(substituciones)) )
                                    logging.debug("EXCEPCION: ")
                                    logging.debug( e)
                                    logging.debug( "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><")
                                    logging.debug( "")
                
                if enDebugging:
                    logging.debug("")
                    logging.debug("posicion: "+str(posicionRecorrido)+"; alternativa iterada: "+str(alternativa.getTransicionesAlt()))
                    logging.debug("substituciones de transicion: %s" % substituciones)
                    logging.debug("")
                    logging.debug("..................................................................")
                    logging.debug("")

        
        #Determina si un vehiculo generado en una via, realmente puede realizar un cambio de via
        def estaVehiculoEnViaValida(self,viaMultiple,vehiculo):
            """ Este metodo determina si un vehiculo puede desplazarse hacia una via multiple.
                @param viaMultiple: Via multiple
                @type viaMultiple: ViaMultiple
                @param vehiculo: Vehiculo a evaluar
                @type vehiculo: Vehiculo"""
            result=viaMultiple.esViaValida(vehiculo.getViaOrigen().getNombre())
            return result

    #Se retorna como una tupla el conjunto de elementos que se deben utilizar
    return Transition,TransicionTemporizada,PetriNet,Place