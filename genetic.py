import numpy as np
import imutils
import crawler
import random


def run_steps(state, choices, start):
    flags_captured = []
    for opt in choices:
        [x, y] = start
        directions = {1: [x-1, y-1], 2: [x, y-1], 3: [x+1, y-1],
                      4: [x-1, y],   5: [x, y],   6: [x+1, y],
                      7: [x-1, y+1], 8: [x, y+1], 9: [x+1, y+1]}

        try:
            [x, y] = directions[opt]
            if (state[x,y,1] and state[x,y,2]) == 0 and state[x,y,0] == 1:
                if [x,y] not in flags_captured:
                    flags_captured.append([x, y])
            start = [x, y]
        except IndexError:
            pass
    return flags_captured, [x, y]


def fitness_function(state, crawler, n_flags):
    captured, endpoint = run_steps(state,crawler.genes,crawler.start)
    displacement = imutils.get_displacement(crawler.start, endpoint)
    fitness = displacement/float(crawler.potential_energy) + ((100*len(captured))/float(n_flags))**2
    return fitness, captured


def genes2positions(choices, start):
    movement = []
    for opt in choices:
        [x, y] = start
        directions = {1: [x-1, y-1], 2: [x, y-1], 3: [x+1, y-1],
                      4: [x-1, y],   5: [x, y],   6: [x+1, y],
                      7: [x-1, y+1], 8: [x, y+1], 9: [x+1, y+1]}
        move = directions[opt]
        movement.append(move)
        start = move
    return movement


def mutation(organism, ratio):
    genes = organism.genes
    n_changes = int(len(genes)*ratio)
    swaps = list(np.random.random_integers(1, 9, n_changes))
    mutate = random.sample(range(0, len(genes)), n_changes)
    for index in mutate:
        genes[index] = swaps.pop()
    return genes


def process_population(crawler_population, mutation_rate, selection, dims, flags, start, energy):
    fitness_scores = {};    look_fit = {}
    captures = {}
    for crawl in crawler_population:
        world = imutils.create_world(dims, flags)
        score, captured = fitness_function(world, crawl, len(flags))
        fitness_scores[crawl] = score
        look_fit[score] = crawl
        captures[crawl] = captured
    best_score = np.array(look_fit.keys()).max()
    mean_score = np.array(look_fit.keys()).mean()
    std_dev = np.array(look_fit.keys()).std()
    most_fit = look_fit[best_score]
    most_captures = captures[most_fit]

    '''  kill/replenish the weakest  '''
    worst_fitness = np.array(look_fit.keys() < mean_score)
    weakest = np.array(look_fit.values())[worst_fitness.nonzero()]
    for doomed in weakest:
        crawler_population.remove(doomed)
        crawler_population.append(crawler.Crawler(start, energy))

    ''' Now apply mutation_ratio to introduce random variation in gene pool '''
    mutate = np.random.random_integers(0, 1000, len(crawler_population)) < int(mutation_rate * 1000)
    # np.random.shuffle(crawler_population)
    crawler_index = 0
    for do_mutation in mutate:
        individual = crawler_population[crawler_index]
        try:
            f = fitness_scores[individual]
        except KeyError:
            world = imutils.create_world(dims, flags)
            score, capt = fitness_function(world, individual, len(flags))
            fitness_scores[individual] = score
        if do_mutation and f < (mean_score+std_dev) and individual not in captures.keys():
            individual.genes = mutation(individual, selection)
            individual.energy = genes2positions(individual.genes, start)
        individual.x, individual.y = start
        crawler_index += 1

    '''     Often Hitting Minima's that introduce plateaus in training performance,
            using crossover with parent/children would likely help get past this into
            even better solutions                                                 '''
    return crawler_population, best_score, most_fit, most_captures

