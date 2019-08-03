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
import subprocess

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

# TODO to use in fitness
param = '10'
scores = [subprocess.run(executable.split() + [inst[0], param], stdout=subprocess.PIPE).stdout.decode('utf-8') for inst in instances]
print(scores)

# init stuff
seed() # init internal state of random number generator
dataset = generate_dataset()
population = init_population() 
best_of_run = None
best_of_run_error = 1e20 
best_of_run_gen = 0
fitnesses = [fitness(ind, dataset) for ind in population]
max_mean_size = [0] # track maximal mean size for plotting
axarr, line, xdata, ydata = prepare_plots()

# evolve programs
for gen in range(GENERATIONS):        
    nextgen_population = []
    for i in range(POP_SIZE):
        parent1 = selection(population, fitnesses)
        parent2 = selection(population, fitnesses)
        parent1.crossover(parent2)
        parent1.mutation()
        nextgen_population.append(parent1)
    population = nextgen_population
    fitnesses = [fitness(ind, dataset) for ind in population]
    print('FITNESSES: ',fitnesses)
    errors = [error(ind, dataset) for ind in population]
    if min(errors) < best_of_run_error:
        best_of_run_error = min(errors)
        best_of_run_gen = gen
        best_of_run = deepcopy(population[errors.index(min(errors))])
        print("________________________")
        best_of_run.draw_tree("best_of_run",\
                              "gen: " + str(gen) + ", error: " + str(round(best_of_run_error,3)))
    #plot(axarr, line, xdata, ydata, gen, population, errors, max_mean_size)
    if best_of_run_error <= 1e-5: break




endrun = "_________________________________________________\nEND OF RUN (bloat control was "
endrun += "ON)" if BLOAT_CONTROL else "OFF)"
print(endrun)
s = "\n\nbest_of_run attained at gen " + str(best_of_run_gen) + " and has error=" + str(round(best_of_run_error,3))
best_of_run.draw_tree("best_of_run",s)
