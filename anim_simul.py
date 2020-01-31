from __future__ import print_function

from buslinesim import Bus, Simulation, Event, BusStop, PrettyFig, Stats
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import truncnorm
import subprocess
import heapq


class AnimBus(Bus):
    def __init__(self):
        super(AnimBus, self).__init__()
        self.vjitter = np.random.uniform(-2, 2)
        

class AnimStats(Stats):
    def measure(self, cur_time, buses, stops, passengers):
        super(AnimStats, self).measure(cur_time, buses, stops, passengers)
        global counter
        fig = plt.figure(FigureClass=PrettyFig)
        print('Tiempo', sim.stats.t)
        print('Parada', [stop.position for stop in stops])
        plt.bar([stop.position for stop in stops],
                [len(stop.passengers) for stop in stops],
                width=1.5)
        for bus in [bus for bus in buses if bus.active]:
            print('Autobus', bus.position)
            plt.plot(bus.position, 16 + bus.vjitter, '>',
                     color='#A60628',
                     markersize=3 + len(bus.passengers)**(2.0/3.0))
        plt.text(26, 19, '{:.0f} min'.format(cur_time))
        plt.xlim(0, 50)
        plt.ylim(0, 20)
        plt.xlabel('Distancia en kilometros entre paradas (km)')
        plt.ylabel('Numero de pasajeros')
        #plt.title('Simulacion horas pico')
        plt.text(19, 20, 'llegada de personas media de 10 minutos.')
        plt.text(19, 21, 'intervalo bajo (cada 15 min sale un bus)')
        plt.text(19, 22, 'Numero de autobuses: 10')
        plt.text(1, 21, 'Simulación hora pico sin colas largas')

        plt.savefig('anim/fig{:05d}.png'.format(counter))
        print('anim/fig{:05d}.png'.format(counter))
        counter += 1

class AnimSimulation(Simulation):
    def run(self):
        """Run the simulation.  The simulation works by maintaining a heap
        queue of events.  The events are processed until the last bus reaches
        the last stop.

        """
        moved_passengers = []
        events = []

        # Initialize events queue.
        for stop in self.stops:
            heapq.heappush(events, Event(stop.next_arrival_time(), stop))

        buses = []
        # first bus starts early to avoid over accumulation of passengers at
        # bus stops.
        t = 0.5 * self.time_between_buses()
        for i in range(self.nb_buses):
            bus = AnimBus()
            buses.append(bus)
            heapq.heappush(events, Event(t, bus))
            t += self.time_between_buses()
        buses[-1].last = True

        # Initialize statistics collection.
        self.stats = AnimStats()
        heapq.heappush(events, Event(self.stats_time, self.stats))

        while events:
            event = heapq.heappop(events)
            t, obj = event.e_time, event.e_obj
            if isinstance(obj, BusStop):
                # New arrival at a bus stop.
                dest = obj.index + self.nb_stops_to_dest()
                obj.passenger_arrival(t, dest=dest)
                heapq.heappush(events, Event(t + obj.next_arrival_time(), obj))
            elif isinstance(obj, Bus):
                if not obj.active:
                    obj.active = True
                if obj.next_stop >= len(self.stops):
                    # Bus reached terminal: it empties and becomes inactive.
                    moved_passengers.extend(obj.empty(t))
                    if obj.last:
                        break
                elif self.stops[obj.next_stop].position == obj.position:
                    # Bus reached a bus stop.
                    bus_stop = self.stops[obj.next_stop]
                    # Passengers hop out.
                    wait_out, passengers = obj.hop_out(
                        stop_index=bus_stop.index,
                        cur_time=t,
                        hop_out_time=self.hop_out_time)
                    moved_passengers.extend(passengers)
                    # Passengers hop in.
                    wait_in = bus_stop.hop_in_bus(t, self.hop_in_time, obj)
                    obj.next_stop += 1
                    heapq.heappush(events, Event(t + wait_out + wait_in, obj))
                else:
                    # Bus finished loading passengers, move to next stop.
                    dist = self.stops[obj.next_stop].position - obj.position
                    heapq.heappush(events,
                                   Event(t + self.bus_speed() * dist, obj))
                    obj.position += dist
            elif isinstance(obj, Stats):
                obj.measure(t, buses, self.stops, moved_passengers)
                heapq.heappush(events, Event(t + self.stats_time, obj))

counter = 1

if __name__ == '__main__':
    #stop_pos = np.arange(0, 30, 2)
    stop_pos = [ 0,  4,  12,  16,  28, 32, 37, 40]
    nb_stops = len(stop_pos)
    mean_stops = nb_stops/2.0
    std_stops = nb_stops/4.0
    a, b = (1 - mean_stops)/std_stops, (nb_stops - mean_stops)/std_stops
    stops_to_dest = lambda: np.round(truncnorm.rvs(a, b, loc=mean_stops, scale=std_stops))
    sim = AnimSimulation(bus_stop_positions=stop_pos,
                     time_between_buses=lambda: 15,
                     nb_stops_to_dest=stops_to_dest,
                     passenger_arrival_times=lambda : np.random.exponential(10.0),
                     stats_time=1, nb_buses=10)
    sim.run()

    # Generate movie
    print('Generating movie...')
    subprocess.call(['ffmpeg', '-r', '10', '-i', 'anim/fig%05d.png', '-c:v',
                     'libx264', '-crf', '23', '-pix_fmt', 'yuv420p',
                     'movie.mp4'])
    print('Done!')




