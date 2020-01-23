#from random import random, randint, seed
from statistics import mean
from copy import deepcopy
from scipy import stats

from GPTree import *
import GPSetup

import subprocess
import random
import io

from sympy import simplify, symbols

#import platform
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
            evaluate(ind)
        # sort population
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        self.population = self.population[:POP_SIZE]


    # Tournament selection
    def selection(self): # select one tree using tournament selection
        #return deepcopy(population[randint(0, len(population)-1)]) 
        tournament = [randint(0, len(self.population)-1) for i in range(TOURNAMENT_SIZE)] # select tournament contenders
        tournament_fitnesses = [self.population[tournament[i]].fitness for i in range(TOURNAMENT_SIZE)]
        return deepcopy(self.population[tournament[tournament_fitnesses.index(max(tournament_fitnesses))]]) 


    # String representation of GP population
    def __str__(self):
        i = 1
        s = ''
        for program in self.population:
            exp = program.infix_expression()
            s = s + '#'+'%2d' %i
            s = s + ' : F=%2.2f' %program.fitness
            s = s + ' | C=%2d' %program.size()
            s = s + " | FH="+str(len(program.fitness_history))
            s = s + ' | EXP=' + str(simplify(exp))
            #s = s + ' | {R}=' + str(['%.2f' %val for val in program.regression_values])
            #s = s + ' | HASH=' + str(hash(frozenset(program.regression_values)))
            s = s + '\n'

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
        # DEB: print population
        print(self)
        print('--------------------------------')
        #==========================================================


        #==========================================================
        # log files
        #==========================================================
        log_bloat = open("./output/log_bloat-" + dt + ".csv","w+")
        log_ref   = open("./output/log_ref-" +   dt + ".csv","w+")
        # log header
        log_bloat.write('Generation Old_size New_size\n')
        log_bloat.flush()
        for inst in instances:
            log_ref.write(inst[0]+' ')
        log_ref.write('\n')
        #==========================================================


        #==========================================================
        # evolve programs
        #==========================================================
        for gen in range(GENERATIONS):

            for ref in references.values():
                log_ref.write(str(ref)+' ')
            log_ref.write('\n')
            log_ref.flush()

            print('GEN:', gen+1)

            # generate a new population of same size
            new_trees = []

            for i in range(GEN_POP_SIZE or self.selectio):
                parent1 = self.selection()
                parent2 = self.selection()
                # mate and mutate
                offspring = parent1.crossover(parent2)
                offspring.mutation()
                # evaluate
                #for i in range(5):
                evaluate(offspring)
                # add to the new stack of trees
                new_trees.append(offspring)

            new_trees.sort(key=lambda x: x.fitness, reverse=True)

            # new_pop = GP(new_trees)
            # print(new_pop)


            # replacement & bloat control
            k = -1
            for i in range(GEN_POP_SIZE):
                tree_size_new = new_trees[i].size()
                new_scores = normalise_scores(new_trees[i])

                dropped = False
                for j in range(POP_SIZE):
                    tree_size_current = self.population[j].size()

                    # if the tress represent the same expression
                    # if ( new_trees[i].regression_hash == self.population[j].regression_hash ):
                    current_scores = normalise_scores(self.population[j])
                    x, pval = stats.ranksums(new_scores, current_scores)
                    #print('>>',new_scores, current_scores, pval)
                    # if pval >= 0.0079:
                    #     print('GOOD!!!')
                    if (pval >= 0.01 or new_trees[i].regression_hash == self.population[j].regression_hash):
                        # if the new tree is less complex
                        if ( tree_size_new < tree_size_current ):
                            # debug
                            print('[REPLACE] >> ', tree_size_current,'|',self.population[j].fitness, ' ==> ', tree_size_new, '|', new_trees[i].fitness , ' ## ', end='')
                            print('  >>', new_scores, current_scores, pval)
                            # save log
                            log_bloat.write(str(gen+1)+' '+str(tree_size_current)+' '+str(tree_size_new)+' '+ new_trees[i].infix_expression() +'\n')
                            log_bloat.flush()
                            self.population[j] = new_trees[i]

                        print('[DROP] >> ', self.population[j].regression_hash)
                        dropped = True
                        break
                if (not dropped):
                    self.population[k] = new_trees[i]
                    k = k-1


            # population evaluation
            for ind in self.population:
                evaluate(ind)

            self.population.sort(key=lambda x: x.fitness, reverse=True)

            # DEB: print population
            print(self)
            print('--------------------------------')
        #==========================================================
        log_bloat.close()
        log_ref.close()



# Evaluation function
def evaluate(tree):
    if len(tree.fitness_history)>=5:
        # print('skip')
        return None
    # print('OKAY')

    global references

    # evaluate tree using feature values (inst[1:]) to obtain the numerical parameter value
    # empty list of regression values
    tree.regression_values = []
    for inst in instances:
        param_value = round(tree.compute_tree( [float(i) for i in inst[1:]] ), 4)
        # TODO: use dictionary to store
        tree.regression_values.append(param_value)

    # run target algorithm for each instance
    for k in range(5):
        scores = {}

        for inst in instances:
            # evaluate tree using feature values (inst[1:]) to obtain the numerical parameter value
            param_value = round(tree.compute_tree( [float(i) for i in inst[1:]] ), 4)

            # execute target algorithm (executable) using the numerical parameter value for each instance
            # QUESTION: if stochastic: repeat k times vs. update on the fly (current)?
            inst_score = float( subprocess.run(executable.split()+[inst[0], str( param_value )], stdout = subprocess.PIPE).stdout.decode('utf-8') )
            scores[inst[0]] = inst_score
            
            # update references if a better one was found using GP
            if (inst_score > references[inst[0]]):
                references[inst[0]] = inst_score

        # save obtained score in fitness history
        tree.fitness_history.append(scores)

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



def normalise_scores(tree):

    # average over all instances at each previous generation
    norm_fitness_history = []

    for f in tree.fitness_history:
        # "re-normalise", average & add to history list
        norm_fitness_history.append( round(mean( [f[inst[0]]/references[inst[0]] for inst in instances] ), 4) )

    # calculate final tree fitness by averaging fitness history list
    return norm_fitness_history
