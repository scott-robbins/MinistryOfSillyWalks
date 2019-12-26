from matplotlib.animation import FFMpegWriter
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
import imutils
import genetic
import time
import sys

'''      STATE PARAMETERS      '''
width = 250
height = 250
start = [125, 125]
n_flags = 250
'''     EVOLUTION PARAMETERS    '''
population_size = 2500
initial_energy = 300
mutation_rate = 0.75
selection_rate = 0.42
n_generations = 1250
fitness_tracker = []
frame_rate = 30
target = 10


class Crawler:
    x = 0
    y = 0
    color = [0, 0, 1]
    start = []
    energy = []
    potential_energy = 0
    genes = []

    def __init__(self, initial_position, potential_energy):
        self.start = initial_position
        self.x = initial_position[0]
        self.y = initial_position[1]
        self.genes, self.energy = imutils.generate_random_steps(initial_position,
                                                                potential_energy)
        self.potential_energy = len(self.energy)

    def show_steps(self, state):
        seed_state = state
        f = plt.figure()
        film = list()
        state[self.x,self.y,:] = [0,1,0]
        film.append([plt.imshow(state)])
        state[self.x, self.y, :] = 0
        for movmt in self.energy:
            try:
                [x, y] = movmt
                state[x, y, :] = [0, 1, 0]
                self.x, self.y = x, y
                film.append([plt.imshow(state)])
                state[self.x, self.y, :] = 0
            except IndexError:
                pass
        self.x = self.start[0]
        self.y = self.start[1]
        if raw_input('Do you want to save this animation?: (Y/N)').upper() == 'Y':
            file_name = raw_input('Enter Filename: ')
            save = True
        else:
            save = False
        a = animation.ArtistAnimation(f,film,interval=50,blit=True,repeat_delay=900)
        if save:
            writer = FFMpegWriter(fps=frame_rate,bitrate=1800)
            a.save(file_name,writer=writer)
            f.clear()
            if raw_input('Want to save with tracers too?: (Y/N)\n').upper() == 'Y':
                f = 'tracer_'+file_name
                self.save_steps_tracers(f, seed_state)
        plt.show()

    def save_steps_tracers(self, file_name, state):
        f = plt.figure();   film = list()
        state[self.x, self.y, :] = [0, 1, 0]
        film.append([plt.imshow(state)])
        state[self.x, self.y, :] = 0
        for movmt in self.energy:
            try:
                [x, y] = movmt
                state[x, y, :] = [0, 1, 0]
                self.x, self.y = x, y
                film.append([plt.imshow(state)])
            except IndexError:
                pass
        self.x = self.start[0]
        self.y = self.start[1]
        a = animation.ArtistAnimation(f, film, interval=50, blit=True, repeat_delay=900)
        writer = FFMpegWriter(fps=frame_rate, bitrate=1800)
        a.save(file_name, writer=writer)
        

def create_seed_state(n_flags, dims):
    seed = np.zeros((dims[0], dims[1], 3))
    flags = []
    while len(flags) < n_flags:
        try:
            [x, y] = imutils.spawn_random_point(dims)
            seed[y,x,:] = [1,0,0]
            flags.append([x,y])
        except IndexError:
            pass
    return seed, flags


def display_simulation_parameters():
    print '==============| SIMULATION PARAMETERS|==============\033[0m'
    print '[*] Dimensions:  [%d, %d]' % (width, height)
    print '[*] Start Point: [%d, %d]' % (start[0], start[1])
    print '[*] Total Flags: %d' % n_flags
    print '[*] N Generations:   %d' % n_generations
    print '[*] Crawler Energy:  %d' % initial_energy
    print '[*] Population Size: %d' % population_size
    print '[*] Mutation Rate:   %f' % mutation_rate
    print '[*] Selection Rate:  %f' % selection_rate
    print '\033[1m=====================================================\033[0m'


if __name__ == '__main__':

    tic = time.time()

    if '-brute' in sys.argv:
        brute_target = 3
        print '[*] Attempting Brute force search for %d Flag Captures' % brute_target
        best = 0;
        N = 0
        initial_state, flags = create_seed_state(n_flags=n_flags, dims=[width, height])
        world = imutils.create_world([width, height], flags)
        plt.imshow(world)
        plt.show()
        while (best < brute_target) or N < 1e6:
            basic = Crawler(start, potential_energy=300)
            world = imutils.create_world([width, height], flags)
            captured, endpt = genetic.run_steps(world, basic.genes, basic.start)
            best = len(captured)
            N += 1
            if N > 0 and N % 10000 == 0:
                print '[*] %d Iterations Simulated [%ss Elapsed]' % (N, str(time.time() - tic))
        fitness, captures = genetic.fitness_function(initial_state, basic, n_flags)
        print '==============================================================================='
        print '%d Total Iterations Simulated [%ss Elapsed]' % (N, str(time.time() - tic))
        print '%d Flags Captured' % len(captured)
        print 'Endpoint: [%d,%d]' % (endpt[1], endpt[0])
        print 'Fitness: %f' % fitness
        basic.show_steps(world)

    if 'run' in sys.argv:
        display_simulation_parameters()

        '''     Global Initial State contains N_Flags. Capturing these is the goal of Crawler '''
        initial_state, flags = create_seed_state(n_flags=n_flags, dims=[width, height])
        world = imutils.create_world([width, height], flags)
        print '[*] Starting Evolutionary Simulation of %d Generations ' % n_generations
		
        population = []  # Create Initial Population
        progress_bar = tqdm(total=n_generations)
        [population.append(Crawler(start, initial_energy)) for crawler in range(population_size)]
        for epoch in range(n_generations):
            population, best_score, most_fit, most_captures = genetic.process_population(population,
                                                                                         mutation_rate,
                                                                                         selection_rate,
                                                                                         [width, height],
                                                                                         flags, start,
                                                                                         initial_energy)
            fitness_tracker.append(best_score)
            if most_captures == target:
                print '[*] Target Solution Found [%ss Elapsed]' % str(time.time() - tic)
                break
            progress_bar.update(1)
        progress_bar.close()
        '''         SIMULATION FINISHED: Display Results    '''
        print '[*] Evolution Finished [%ss Elapsed]' % str(time.time() - tic)
        print '[*] Highest Fitness Score: %f' % best_score
        print '[*] Flag Captures: %d' % len(most_captures)

        plt.plot(np.array(fitness_tracker))
        plt.title('Fitness Score Evolution [Best Score %f]' % best_score)
        plt.grid()
        plt.xlabel('Epoch')
        plt.ylabel('Fitness')
        plt.show()

        print '[*] Animating Best Solution...'
        most_fit.show_steps(imutils.create_world([width, height], flags))



