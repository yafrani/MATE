#from random import random, randint, seed
from statistics import mean
from copy import deepcopy

from GPTree import *
import GPSetup

import subprocess
import random

import platform
from sympy import simplify, symbols
#print(platform.system())


# GP population
class GP:

    def __init__(self, pop = None):
        self.population  = pop

    # Randomely initialise population
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


    # Tournament selection
    def selection(self): # select one individual using tournament selection
        #return deepcopy(population[randint(0, len(population)-1)]) 
        tournament = [randint(0, len(self.population)-1) for i in range(TOURNAMENT_SIZE)] # select tournament contenders
        tournament_fitnesses = [self.population[tournament[i]].fitness for i in range(TOURNAMENT_SIZE)]
        return deepcopy(self.population[tournament[tournament_fitnesses.index(max(tournament_fitnesses))]]) 


    # Evolve population
    def evolution(self):

        #==========================================================
        # initialisation
        #==========================================================
        # generate initial population
        self.init_population()
        '''
        best_program = None
        best_gen = 0
        best_fitness = -1e20
        '''
        # evaluate population
        for ind in self.population:
            fitness(ind, executable, instances)
        # sort population
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        # DEB: print population
        i=1
        for program in self.population:
            exp = program.infix_expression()
            print(i,'>>',program.fitness, ":", simplify(exp))
            i=i+1
        print('--------------------------------')
        #==========================================================


        #==========================================================
        # evolve programs
        #==========================================================
        for gen in range(GENERATIONS):
            print('GEN:', gen+1)

            # generate a new population of same size
            nextgen_population = []

            for i in range(GEN_POP_SIZE):
                parent1 = self.selection()
                parent2 = self.selection()

                # mate and mutate
                offspring = parent1.crossover(parent2)
                offspring.mutation()
                nextgen_population.append(offspring)

            # replacement (replace ~75%)
            self.population[POP_SIZE-GEN_POP_SIZE:] = nextgen_population

            # population evaluation
            for ind in self.population:
                fitness(ind, executable, instances)

            self.population.sort(key=lambda x: x.fitness, reverse=True)

            # update best if improvement was found
            '''
            best_program_pop = max(self.population, key=lambda x: x.fitness)
            if best_program_pop.fitness > best_fitness:
                best_fitness = best_program_pop.fitness
                best_program = deepcopy(best_program_pop)
            '''

            # DEB: print population
            i = 1
            for program in self.population:
                exp = program.infix_expression()
                print(i,'>>',program.fitness, ':', simplify(exp), '|',program.regression_values,'#', hash(str(program.regression_values)))
                i = i+1
            print('--------------------------------')
        #==========================================================




# Evaluation function
def fitness(individual, executable, instances):

    global references

    # create array containing individual scores for each instances
    scores = []
    # regression values (=parameter values)
    individual.regression_values = []
    for inst in instances:
        # evaluate tree using feature values (inst[1:]) to obtain the numerical parameter value
        param_value = individual.compute_tree( [float(i) for i in inst[1:]] )
        individual.regression_values.append(param_value)

        # execute target algorithm (executable) using the numerical parameter value for each instance
        # TODO: if stochastic, repeat k times
        inst_score = float( subprocess.run(executable.split()+[inst[0], str( param_value )], stdout = subprocess.PIPE).stdout.decode('utf-8') )
        scores.append( inst_score/references[inst[0]] )
        
        # update references if a better one was found using GP
        if (inst_score > references[inst[0]]):
            references[inst[0]] = inst_score

    # calculate the final score by averaging the obtained scores for each instance
#    score_avg_instances = 
    individual.fitness = mean(scores)
    individual.regression_hash = hash(str(individual.regression_values))

    #print("OKAY-------->",individual.fitness,'vs',mean(scores),'||',)

    return individual.fitness









def fitness2(individual, executable, instances):
    #print(  str(individual.compute_tree(float(instances[0][1])))  )
    #for inst in instances: print('--->>',[float(i) for i in inst[1:]])

    scores = [subprocess.run(executable.split()+[inst[0], str( individual.compute_tree( [float(i) for i in inst[1:]] ) )], 
        stdout = subprocess.PIPE).stdout.decode('utf-8') for inst in instances]
    avg_score = mean( list(map(int, scores)) )
    return avg_score


def fitness3(individual, executable, instances):

    # create array containing individual scores for each instances
    scores = []
    for inst in instances:
        # evaluate tree using feature values (inst[1:]) to obtain the numerical parameter value
        param_value = individual.compute_tree( [float(i) for i in inst[1:]] )

        # execute target algorithm (executable) using the numerical parameter value for each instance
        # TODO: if stochastic, repeat k times
        scores.append( subprocess.run(executable.split()+[inst[0], str( param_value )], stdout = subprocess.PIPE).stdout.decode('utf-8') )

    # calculate the final score by averaging the obtained scores for each instance
    avg_score = mean( list(map(float, scores)) )

    return avg_score




