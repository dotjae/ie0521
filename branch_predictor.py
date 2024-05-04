from optparse import OptionParser
import gzip
from bimodal import *
from gshared import *
from pshared import *
from perceptron import *
from ie0521_bp import *
from tage import *

#Esto permite correr el programa de forma más intuitiva mediante el uso de argumentos
#Ustedes pueden agregar más opciones en caso de que sean necesarias
parser = OptionParser()
parser.add_option("-n", dest="bits_to_index")
parser.add_option("--bp", dest="branch_predictor_type")
parser.add_option("-g", dest="global_history_size")
parser.add_option("-l", dest="local_history_size")
parser.add_option("-t", dest="TRACE_FILE", default="../branch-trace-gcc.trace.gz")
# AQUI IRÍAN LAS OPCIONES EXTRA

(options, args) = parser.parse_args()


#Acá inicializamos el predictor a utilizar
#En cada caso instanciamos el predictor y luego usamos la función print_info
#para verificar que se esté utilizando correctamente los argumentos brindados.
# Si --bp 0 entonces usamos el bimodal
if options.branch_predictor_type == "0":
    branch_predictor = bimodal(int(options.bits_to_index))
    branch_predictor.print_info()
#Si --bp 1 entonces usamos g-shared
elif options.branch_predictor_type == "1":
    branch_predictor = gshared(int(options.bits_to_index),int(options.global_history_size))
    branch_predictor.print_info()
#Si --bp 2 entonces usamos p-shared
elif options.branch_predictor_type == "2":
    #Deben inicializar p-shared con los parámetros necesarios
    branch_predictor = pshared(int(options.bits_to_index), int(options.local_history_size))
    branch_predictor.print_info()
#Si --bp 3 entonces usamos perceptron
if options.branch_predictor_type == "3":
    #Deben inicializar perceptron con los parámetros necesarios
    branch_predictor = perceptron(int(options.bits_to_index),int(options.global_history_size))
    branch_predictor.print_info()  
#Si --bp 4 entonces usamos el que ustedes proponen
if options.branch_predictor_type == "4":
    #Deben inicializar su predictor con los parámetros necesarios
    branch_predictor = TAGE()
    branch_predictor.print_info()


#i = 0  #DEBUG
#Acá abrimos el trace 
with gzip.open(options.TRACE_FILE,'rt') as trace_fh:
    #Y luego lo recorremos, línea por línea

    count = 0
    for line in trace_fh:
        #Quitamos espacios extra al final y extraemos el PC y el resultado del salto
        line = line.rstrip()
        PC,result = line.split(" ")
     
        #Todos los predictores deben tener 2 funciones
        #1. prediction: que con el estado actual del predictor y el PC del salto 
        #               predicen si el salto se tomará, o no

        if options.branch_predictor_type == "4":
            prediction, alt_pred, provider_idx = branch_predictor.predict(PC)
        else:
            prediction = branch_predictor.predict(PC)

        #2. update:     con el estado actual del predictor, el PC del salto y el resultado real
        #               de la predicción actualizamos el estado del predictor para próximas predicciones
        
        if options.branch_predictor_type == "4":
            branch_predictor.update(PC, result, prediction, alt_pred, provider_idx)
        else:
            branch_predictor.update(PC, result, prediction)

        #NOTA:  el update DEBE HACERSE DESPUÉS del predict, pues en la realidad, el resultado del branch se
        #       obtendrá varios ciclos después de hacer la predicción


        # print("LINE: ", line, "\n")

        # count += 1
        # if count == 100:
        #     break
        
        #Este código de abajo es para sólo hacer las primeras 25 líneas del programa, de forma que sea más
        #fácil ir revisando el progreso que van haciendo 
        #i+=1           #DEBUG
        #if i == 25:    #DEBUG
        #    break      #DEBUG
        
#Una vez finalizado el archivo, se imprimen las estadísticas de la corrida
branch_predictor.print_stats()
