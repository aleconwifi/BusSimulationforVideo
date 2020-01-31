
from buslinesim import Bus, Simulation, Event, BusStop, PrettyFig, Stats
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import truncnorm
from scipy import stats
import subprocess
import heapq
import pandas as pd
import matplotlib.pyplot as plt

def parametros(paradas, intervalo, dist_pasajeros, cant_autobuses, tiempo_screen=1, vel_autobus=0.83):
    """ paradas: (array np) donde cada posicion es la distancia en Km entre una parada y otra
        intervalo: (INT) es cada cuantos minutos un autobus sale min/autobus
        dist_pasajeros: (FLOAT) ""Tiempo entre dos llegadas sucesivas de pasajeros a una parada de autobús min/pasajero
        cant_autobuses: (INT) es la cantidad de autobuses que van a salir en la simulacion
        tiempo_screen: (INT)  "Tiempo en que la simulacion hace un screen para mostrar resultados (por default es cada minuto)
    """
    stop_pos = paradas
    nb_stops = len(stop_pos)
    mean_stops = nb_stops/2.0
    std_stops = nb_stops/4.0
    a, b = (1 - mean_stops)/std_stops, (nb_stops - mean_stops)/std_stops
    stops_to_dest = lambda: np.round(truncnorm.rvs(a, b, loc=mean_stops, scale=std_stops))
    sim = Simulation(bus_stop_positions=stop_pos,
                     time_between_buses=lambda: intervalo,
                     nb_stops_to_dest=stops_to_dest,
                     passenger_arrival_times=lambda : np.random.exponential(dist_pasajeros),
                     stats_time=1, nb_buses=cant_autobuses, bus_speed=lambda: truncnorm.rvs(-2, 2, loc=vel_autobus, scale=0.1))
    sim.run()
    diccionario = {
        'AVG_passenger_satisfaction': np.mean(sim.stats.satisfaction),
        'Passengers_arrived_destination': len(sim.stats.travel_times),
        'AVG_total_travel_time': np.mean(sim.stats.travel_times),
        'Passengers_who_waited': len(sim.stats.waited_times),
        'Average_queue_timeout': np.mean(sim.stats.waited_times),
        'AVG_number_stops_passenger_travels': np.mean(sim.stats.nb_stops_traveled),
        'Stops_trend_passenger': int(stats.mode(sim.stats.nb_stops_traveled)[0]),
        'Histogram_intervals': int(sim.stats._nb_bins(len(sim.stats.travel_times))),
        'AVG_passengers_carried_bus': np.mean(sim.stats.total_passengers[-1])
       }
    return diccionario, sim


def df_passengers_activebus(sim):
    sim.stats.t = np.array(sim.stats.t)
    avg_nb_passengers = [nb_passengers.mean() for nb_passengers in sim.stats.nb_passengers_in_active_buses]
    tiempos = sim.stats.t.tolist()
    horas= sim.stats.t/60
    horas = horas.tolist()
    horas = [ '%.2f' % elem for elem in horas ]
    dict = {'Minutes': tiempos, 'Hours': horas, 'passengers in active buses': avg_nb_passengers}  
    dfnropasajbuses = pd.DataFrame(dict) 
    return dfnropasajbuses

def df_number_activebus(sim):
    sim.stats.t = np.array(sim.stats.t)    
    list_ = sim.stats.nb_active_buses
    times = sim.stats.t.tolist()
    hours= sim.stats.t/60
    hours = hours.tolist()
    hours = [ '%.2f' % elem for elem in hours ]
    dict = {'Minutes': times, 'Hours': hours, 'Active Buses': list_}  
    df_Number_Activebus = pd.DataFrame(dict) 
    return df_Number_Activebus

def df_queues_at_stops(sim):
    sim.stats.t = np.array(sim.stats.t)    
    times = sim.stats.t.tolist()
    hours= sim.stats.t/60
    hours = hours.tolist()
    hours = [ '%.2f' % elem for elem in hours ]
    dict = {'Minutes': times, 'Hours': hours, 'Queue by stop': sim.stats.len_queues_at_stops,'Sum of all queues': np.sum(sim.stats.len_queues_at_stops, axis=1)}  
    df_Queues_At_Stops = pd.DataFrame(dict)         
    return df_Queues_At_Stops

def _nb_bins(x):
    """Use Rice rule for number of bins in histograms."""
    x = np.array(x)
    return np.ceil(2 * x ** (1.0/3.0))

def time_system(sim):
    tiempo_en_sistema = {"Frecuency travel_times": sim.stats.travel_times }
    dftimesystem = pd.DataFrame(tiempo_en_sistema)
    dftimesystem = dftimesystem['Frecuency travel_times'].value_counts(sort=False, bins=int(_nb_bins(len(sim.stats.travel_times)))).to_frame()
    return dftimesystem

def time_waiting(sim):
    time_waited_times = {"Frecuency waited_times": sim.stats.waited_times }
    dfwaited_times = pd.DataFrame(time_waited_times)
    dfwaited_times = dfwaited_times['Frecuency waited_times'].value_counts(sort=False, bins=int(_nb_bins(len(sim.stats.waited_times)))).to_frame()
    return dfwaited_times

def number_stops_traveled(sim):
    number_stops_traveled = {"Frecuency stops_traveled": sim.stats.nb_stops_traveled }
    df_stops_traveled = pd.DataFrame(number_stops_traveled)
    df_stops_traveled = df_stops_traveled['Frecuency stops_traveled'].value_counts(sort=False, bins=int(_nb_bins(len(sim.stats.nb_stops_traveled)))).to_frame()
    return df_stops_traveled


def satisfaction(sim):
    number_satisfaction = {"Probability satisfaction": sim.stats.satisfaction }
    df_satisfaction = pd.DataFrame(number_satisfaction)
    return df_satisfaction

def satisfaction(sim):
    number_satisfaction = {"Probability satisfaction": sim.stats.satisfaction }
    df_satisfaction = pd.DataFrame(number_satisfaction)
    return df_satisfaction

def numberpassengers(sim):
    numberpassengers = {"Number Passengers by stop": sim.stats.total_passengers }
    df_numberpassengers = pd.DataFrame(numberpassengers)
    return df_numberpassengers


if __name__ == '__main__':
    dicc, sim = parametros([ 0,  4,  15,  18,  30, 35, 42, 50], 5,15, 15)
    print(dicc)
   
    df = df_passengers_activebus(sim)
    print(dicc)


