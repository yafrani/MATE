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






def fitness(individual, executable, instances):
    #print(  str(individual.compute_tree(float(instances[0][1])))  )
    #for inst in instances: print('--->>',[float(i) for i in inst[1:]])

    scores = [subprocess.run(executable.split()+[inst[0], str( individual.compute_tree( [float(i) for i in inst[1:]] ) )], 
        stdout = subprocess.PIPE).stdout.decode('utf-8') for inst in instances]
    avg_score = mean( list(map(int, scores)) )
    return avg_score


#def error(self, individual, dataset):
#    return mean([abs(individual.compute_tree(ds[0]) - ds[1]) for ds in dataset])


