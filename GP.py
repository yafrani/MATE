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
    # ramped half-and-half
    def init_population(self):
        self.population = []
        for md in range(3, MAX_DEPTH + 1):
            for i in range(int(POP_SIZE/2)):
                t = GPTree()
                t.random_tree(grow = True, max_depth = md) # grow
                self.population.append(t) 
            for i in range(int(POP_SIZE/2)):
                t = GPTree()
                t.random_tree(grow = False, max_depth = md) # full
                self.population.append(t) 
        # evaluate population
        for ind in self.population:
            evaluate(ind, executable, instances)
        # sort population
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        self.population = self.population[:POP_SIZE]


    # Tournament selection
    def selection(self): # select one tree using tournament selection
        #return deepcopy(population[randint(0, len(population)-1)]) 
        tournament = [randint(0, len(self.population)-1) for i in range(TOURNAMENT_SIZE)] # select tournament contenders
        tournament_fitnesses = [self.population[tournament[i]].fitness for i in range(TOURNAMENT_SIZE)]
        return deepcopy(self.population[tournament[tournament_fitnesses.index(max(tournament_fitnesses))]]) 


    # string representation of GP population
    def __str__(self):
        i = 1
        s = ''
        for program in self.population:
            exp = program.infix_expression()
            s = s + '#'+'%2d' %i
            s = s + ' : F=%2.2f' %program.fitness
            s = s + ' | C=%2d' %program.size()
            s = s + ' | EXP=' + str(simplify(exp))
            s = s + ' | {R}=' + str(['%.2f' %val for val in program.regression_values])
            s = s + ' | HASH=' + str(hash(frozenset(program.regression_values))) + '\n'
            #print('              ->',program.fitness_history)
            i = i+1
        return s


    # Evolve population
    def evolution(self):

        #==========================================================
        # initialisation
        #==========================================================
        # generate initial population
        print('Initial population:')
        self.init_population()
        '''
        # evaluate population
        for ind in self.population:
            evaluate(ind, executable, instances)
        # sort population
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        '''
        # DEB: print population
        print(self)
        print('--------------------------------')
        #==========================================================


        #==========================================================
        # evolve programs
        #==========================================================
        for gen in range(GENERATIONS):
            print('GEN:', gen+1)

            # generate a new population of same size
            new_trees = []

            for i in range(GEN_POP_SIZE):
                parent1 = self.selection()
                parent2 = self.selection()
                # mate and mutate
                offspring = parent1.crossover(parent2)
                offspring.mutation()
                # evaluate
                evaluate(offspring, executable, instances)
                # add to the new stack of trees
                new_trees.append(offspring)

            # replacement & bloat control
            k = -1
            for i in range(GEN_POP_SIZE):
                dropped = False
                for j in range(POP_SIZE):
                    if ( new_trees[i].regression_hash == self.population[j].regression_hash ):
                        if ( new_trees[i].size() < self.population[j].size() ):
                            print('[REPLACE] >> ', new_trees[i].size(), ' => ', self.population[j].size(), end='')
                            self.population[j] = new_trees[i]
                            #print('[REPLACE] + ', simplify(new_trees[i].infix_expression()),' | ', simplify(self.population[j].infix_expression()), end='')

                        print('[DROP] >> ', self.population[j].regression_hash)
                        dropped = True
                        break
                if (not dropped):
                    self.population[k] = new_trees[i]
                    k = k-1

            #self.population[POP_SIZE-len(new_trees):] = new_trees



            # population evaluation
            for ind in self.population:
                evaluate(ind, executable, instances)

            self.population.sort(key=lambda x: x.fitness, reverse=True)

            # DEB: print population
            print(self)
            print('--------------------------------')
        #==========================================================




# Evaluation function
def evaluate(tree, executable, instances):

    global references

    # list of tree scores for each instances
    scores = {}

    # empty list of regression values
    tree.regression_values = []

    # run target algorithm for each instance
    for inst in instances:
        # evaluate tree using feature values (inst[1:]) to obtain the numerical parameter value
        param_value = round(tree.compute_tree( [float(i) for i in inst[1:]] ), 2)
        tree.regression_values.append(param_value)

        # execute target algorithm (executable) using the numerical parameter value for each instance
        # QUESTION: if stochastic: repeat k times vs. update on the fly (current)?
        inst_score = float( subprocess.run(executable.split()+[inst[0], str( param_value )], stdout = subprocess.PIPE).stdout.decode('utf-8') )
        scores[inst[0]] = inst_score
        
        # update references if a better one was found using GP
        if (inst_score > references[inst[0]]):
            references[inst[0]] = inst_score

    # save obtained score in fitness history
    tree.fitness_history.append(scores)

    # print(tree.fitness_history)
    # print([x for x in references.values()])
    
    # average over all instances at each previous generation
    norm_fitness_history = []
    for f in tree.fitness_history:
        # "re-normalise", average & add to history list
        norm_fitness_history.append( mean( [f[inst[0]]/references[inst[0]] for inst in instances] ) )

    # calculate final tree fitness by averaging fitness history list
    tree.fitness = mean(norm_fitness_history)

    # calculate hash for regression values as a "unique" ID
    tree.regression_hash = hash(frozenset(tree.regression_values))

    return tree.fitness









def fitness2(tree, executable, instances):
    #print(  str(tree.compute_tree(float(instances[0][1])))  )
    #for inst in instances: print('--->>',[float(i) for i in inst[1:]])

    scores = [subprocess.run(executable.split()+[inst[0], str( tree.compute_tree( [float(i) for i in inst[1:]] ) )], 
        stdout = subprocess.PIPE).stdout.decode('utf-8') for inst in instances]
    avg_score = mean( list(map(int, scores)) )
    return avg_score


def fitness3(tree, executable, instances):

    # create array containing tree scores for each instances
    scores = []
    for inst in instances:
        # evaluate tree using feature values (inst[1:]) to obtain the numerical parameter value
        param_value = tree.compute_tree( [float(i) for i in inst[1:]] )

        # execute target algorithm (executable) using the numerical parameter value for each instance
        # TODO: if stochastic, repeat k times
        scores.append( subprocess.run(executable.split()+[inst[0], str( param_value )], stdout = subprocess.PIPE).stdout.decode('utf-8') )

    # calculate the final score by averaging the obtained scores for each instance
    avg_score = mean( list(map(float, scores)) )

    return avg_score




