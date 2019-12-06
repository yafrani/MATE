from random import random, randint, seed
from statistics import mean
from copy import deepcopy

from GPTree import *
import GPSetup
import subprocess

import platform
#print(platform.system())


# GP population
class GP:

    def __init__(self, pop = None):
        self.population  = pop


    def init_population(self): # ramped half-and-half
        self.population = []
        for md in range(3, MAX_DEPTH + 1):
            for i in range(int(POP_SIZE/6)):
                t = GPTree()
                t.random_tree(grow = True, max_depth = md) # grow
                self.population.append(t) 
            for i in range(int(POP_SIZE/6)):
                t = GPTree()
                t.random_tree(grow = False, max_depth = md) # full
                self.population.append(t) 

    def selection(self, fitnesses): # select one individual using tournament selection
        #return deepcopy(population[randint(0, len(population)-1)]) 
        tournament = [randint(0, len(self.population)-1) for i in range(TOURNAMENT_SIZE)] # select tournament contenders
        tournament_fitnesses = [fitnesses[tournament[i]] for i in range(TOURNAMENT_SIZE)]
        return deepcopy(self.population[tournament[tournament_fitnesses.index(max(tournament_fitnesses))]]) 






def fitness2(individual, executable, instances):
    #print(  str(individual.compute_tree(float(instances[0][1])))  )
    #for inst in instances: print('--->>',[float(i) for i in inst[1:]])

    scores = [subprocess.run(executable.split()+[inst[0], str( individual.compute_tree( [float(i) for i in inst[1:]] ) )], 
        stdout = subprocess.PIPE).stdout.decode('utf-8') for inst in instances]
    avg_score = mean( list(map(int, scores)) )
    return avg_score


def fitness(individual, executable, instances):
    #print(  str(individual.compute_tree(float(instances[0][1])))  )
    #for inst in instances: print('--->>',[float(i) for i in inst[1:]])

    scores = []
    for inst in instances:
        param_value = individual.compute_tree( [float(i) for i in inst[1:]] )
        # if stochastic, repeat k times:
        scores.append( subprocess.run(executable.split()+[inst[0], str( param_value )], stdout = subprocess.PIPE).stdout.decode('utf-8') )
        #print('>>',param_value, '  ',inst[0], '  ', inst[1])

    # print(scores)

    avg_score = mean( list(map(float, scores)) )
    # print(avg_score)
    return avg_score
