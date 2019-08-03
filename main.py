#!/usr/bin/python3

#=================================================================================
# Tuning engine based on tiny genetic programming plus, by moshe sipper
#=================================================================================

from random import random, randint, seed
from statistics import mean
from copy import deepcopy
from IPython.display import Image, display
from graphviz import Digraph, Source 

from genData import *
from GPTree import *
from GPSetup import *

#=============================
# tunner input
#=============================
# algorithm executable
executable = 'python3 randsearch.py'

# instances/features list
f = open('srt_instances.txt', 'r')
instances = [(line.split()) for line in f.readlines()[1:]]
f.close()
#=============================

# init stuff
seed() # init internal state of random number generator
dataset = generate_dataset()
population = init_population() 

# TODO to use in fitness
param = '10'
scores = [subprocess.run(executable.split() + [inst[0], param], stdout=subprocess.PIPE).stdout.decode('utf-8') for inst in instances]
print(scores)
fitness(population[0], executable, instances)


best_program = None
best_gen = 0
best_fitness = -1e20
fitnesses = [fitness(ind, executable, instances) for ind in population]

# evolve programs
for gen in range(GENERATIONS):        
    print('GEN:', gen)

    nextgen_population = []
    for i in range(POP_SIZE):
        parent1 = selection(population, fitnesses)
        parent2 = selection(population, fitnesses)
        parent1.crossover(parent2)
        parent1.mutation()
        nextgen_population.append(parent1)
    population = nextgen_population
    fitnesses = [fitness(ind, executable, instances) for ind in population]
    print(fitnesses)
    # if we have an improvement
    best_fitness_pop = max(fitnesses)
    if best_fitness_pop > best_fitness:
        best_fitness = best_fitness_pop
        best_gen = gen
        best_program = deepcopy(population[fitnesses.index(max(fitnesses))])
        print("________________________")



best_program.draw_tree("best_program", "\nbest gen: " + str(best_gen) + " | fitness: " + str(best_fitness))
