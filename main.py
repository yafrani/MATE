#!/usr/bin/env python3

#=================================================================================
# Tuning engine (based on tiny genetic programming plus, by moshe sipper)
#=================================================================================

from random import random, randint, seed
from statistics import mean
from copy import deepcopy
from IPython.display import Image, display
from graphviz import Digraph, Source 

from sympy import simplify, symbols

from utils import *
from GP import *
from GPSetup import *

import platform
#print(platform.system()=='Linux')


#==========================================================
# tunner input
#==========================================================
# algorithm executable
with open('srt_executable.txt', 'r') as file:
    executable = file.read().replace('\n', '')

# instances/features list
f = open('srt_instances.txt', 'r')
instances = [(line.split()) for line in f.readlines()[1:]]
f.close()
#==========================================================


#==========================================================
# initialisation
#==========================================================
seed() # init internal state of random number generator
gp = GP()
gp.init_population()
best_program = None
best_gen = 0
best_fitness = -1e20
fitnesses = [fitness(ind, executable, instances) for ind in gp.population]
print("==>",fitnesses)
#==========================================================


#==========================================================
# evolve programs
#==========================================================
for gen in range(GENERATIONS):
    print('GEN:', gen)

    nextgen_population = []
    for i in range(POP_SIZE):
        parent1 = gp.selection(fitnesses)
        parent2 = gp.selection(fitnesses)
        parent1.crossover(parent2)
        parent1.mutation()
        nextgen_population.append(parent1)
    gp.population = nextgen_population
    fitnesses = [fitness(ind, executable, instances) for ind in gp.population]
    print(fitnesses)

    # if we have an improvement
    best_fitness_pop = max(fitnesses)
    if best_fitness_pop > best_fitness:
        best_fitness = best_fitness_pop
        best_gen = gen
        best_program = deepcopy(gp.population[fitnesses.index(max(fitnesses))])
    print("________________________")
#==========================================================


#==========================================================
# save best program and simplify
#==========================================================
best_program.draw_tree("best_program", "\nbest gen: " + str(best_gen) + " | fitness: " + str(best_fitness))

exp = best_program.infix_expression()
print(exp)
x, y = symbols('x,y')
sexp = simplify(exp)
print(sexp)
#==========================================================
