from statistics import mean
from copy import deepcopy
from scipy import stats

from GPTree import *
import GPSetup

import subprocess
import random
import io
import timeit

from multiprocessing import Pool

from sympy import simplify, symbols
#import platform
#print(platform.system())

from CGP import *


# GP population
class GP:


    # reference fitnesses to be used as upper bounds
    # each instance has a reference
    # references are parameter-independent
    references = {}
    for inst in instances:
        references[inst[0]] = -inf

    # references values for parameters for each instance
    ref_param_values = {}


    ##########################################################################
    # Construct GP instance for one parameter
    ##########################################################################
    def __init__(self, population = None, param_id = 0):
        self.population  = population
        self.param_id = param_id


    ##########################################################################
    # String representation of GP population
    ##########################################################################
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


    ##########################################################################
    # Randomely initialise population
    # ramped half-and-half
    ##########################################################################
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
            self.evaluate(ind)

        # sort population
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        self.population = self.population[:POP_SIZE]


    ##########################################################################
    # Tournament selection
    ##########################################################################
    def selection(self): # select one tree using tournament selection
        #return deepcopy(population[randint(0, len(population)-1)]) 
        tournament = [randint(0, len(self.population)-1) for i in range(TOURNAMENT_SIZE)] # select tournament contenders
        tournament_fitnesses = [self.population[tournament[i]].fitness for i in range(TOURNAMENT_SIZE)]
        return deepcopy(self.population[tournament[tournament_fitnesses.index(max(tournament_fitnesses))]]) 


    ##########################################################################
    # Evolve population
    ##########################################################################
    def evolution(self):
        #==========================================================
        # initialisation
        #==========================================================
        # generate initial population
        print('Initial population:')
        if self.population==None:
            self.init_population()

        # Re-evaluate population:
        # because the other parameters might have changed
        for ind in self.population:
            ind.fitness_history = []
            ind.fitness = -inf
            ind.regression_values = {}
            ind.regression_hash = None


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

            for ref in GP.references.values():
                log_ref.write(str(ref)+' ')
            log_ref.write('\n')
            log_ref.flush()

            print('PARAM',self.param_id,'| GEN:', gen+1)
            print('REF PARAM >>', GP.ref_param_values)
            print('REF FITNE >>', GP.references)


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
                self.evaluate(offspring)
                # add to the new stack of trees
                new_trees.append(offspring)

            new_trees.sort(key=lambda x: x.fitness, reverse=True)

            # new_pop = GP(new_trees)
            # print(new_pop)


            # replacement & bloat control
            k = -1
            for i in range(GEN_POP_SIZE):
                tree_size_new = new_trees[i].size()
                new_scores = self.normalise_scores(new_trees[i])

                dropped = False
                for j in range(POP_SIZE):
                    tree_size_current = self.population[j].size()

                    # if the tress represent the same expression
                    current_scores = self.normalise_scores(self.population[j])
                    x, pval = stats.ranksums(new_scores, current_scores)
                    if (pval >= 0.01 or new_trees[i].regression_hash == self.population[j].regression_hash):
                        # if the new tree is less complex
                        if ( tree_size_new < tree_size_current ):
                            # debug
                            #print('[REPLACE] >> ', tree_size_current,'|',self.population[j].fitness, ' ==> ', tree_size_new, '|', new_trees[i].fitness , ' ## ', end='')
                            #print('  >>', new_scores, current_scores, pval)
                            # save log
                            log_bloat.write(str(gen+1)+' '+str(tree_size_current)+' '+str(tree_size_new)+' '+ new_trees[i].infix_expression() +'\n')
                            log_bloat.flush()
                            self.population[j] = new_trees[i]

                        #print('[DROP] >> ', self.population[j].regression_hash)
                        dropped = True
                        break
                if (not dropped):
                    self.population[k] = new_trees[i]
                    k = k-1


            # population evaluation
            for ind in self.population:
                self.evaluate(ind)

            # soft population based on fitness
            self.population.sort(key=lambda x: x.fitness, reverse=True)

            # update reference parameter values
            for inst in instances:
                GP.ref_param_values[inst[0]][self.param_id] = str(self.population[0].regression_values[inst[0]])

            # DEB: print population
            print(self)
            print('--------------------------------')
        #==========================================================
        log_bloat.close()
        log_ref.close()


    ##########################################################################
    # Evaluation function
    ##########################################################################
    def evaluate(self, tree):
        if len(tree.fitness_history)>=5:
            return None

        # evaluate tree using feature values (inst[1:]) to obtain the numerical parameter value
        # empty list of regression values
        #tree.regression_values = []
        tree.regression_values = {}
        for inst in instances:
            param_value = round(tree.compute_tree( [float(i) for i in inst[1:]] ), 4)
            # TODO: use dictionary to store
            #tree.regression_values.append(param_value)
            tree.regression_values[inst[0]] = param_value

        # run target algorithm for each instance
        #start = timeit.default_timer()
        with Pool(10) as p:
            tree.fitness_history = p.map(self.run_target, [tree]*10)

        # update references if a better one was found using GP
        for i in range(len(tree.fitness_history)):
            for inst in instances:
                if (tree.fitness_history[i][inst[0]] > GP.references[inst[0]]):
                    GP.references[inst[0]] = tree.fitness_history[i][inst[0]]
                    #GP.ref_param_values[inst[0]][self.param_id] = str(tree.regression_values[inst[0]])
                    #GP.ref_param_values[inst[0]][self.param_id] = str(param_value)
                    print('NEW REF (p_',self.param_id,'):',GP.references)
                    #print('yaaaaaaaaaay!!',self.param_id,' A:',GP.ref_param_values)

        #for k in range(5):
        #    tree.fitness_history.append(self.run_target(tree))

        # normalise fitness scores using references
        norm_fitness_history = self.normalise_scores(tree)

        # calculate final tree fitness by averaging fitness history list
        tree.fitness = mean(norm_fitness_history)

        # calculate hash for regression values as a "unique" ID
        tree.regression_hash = hash(frozenset(tree.regression_values.items()))

        return tree.fitness


    ##########################################################################
    # Normalise fitness scores using references
    ##########################################################################
    def normalise_scores(self, tree):

        # average over all instances at each previous generation
        norm_fitness_history = []

        for f in tree.fitness_history:
            # "re-normalise", average & add to history list
            norm_fitness_history.append( round(mean( [f[inst[0]]/GP.references[inst[0]] for inst in instances] ), 4) )

        # calculate final tree fitness by averaging fitness history list
        return norm_fitness_history


    ##########################################################################
    # Run target algorithm for each instance
    ##########################################################################
    def run_target(self, tree):

        scores = {}
        for inst in instances:
            # evaluate tree using feature values (inst[1:]) to obtain the numerical parameter value
            param_value = round(tree.compute_tree( [float(i) for i in inst[1:]] ), 4)

            # execute target algorithm (executable) using the numerical parameter value for each instance
            tmp = GP.ref_param_values[inst[0]][self.param_id]
            GP.ref_param_values[inst[0]][self.param_id] = str(param_value)
            scores[inst[0]] = run_target_static(inst[0], GP.ref_param_values[inst[0]])
            #scores[inst[0]] = float( subprocess.run(executable.split()+[inst[0], str( param_value )], stdout = subprocess.PIPE).stdout.decode('utf-8') )
            GP.ref_param_values[inst[0]][self.param_id] = tmp

        return scores



##########################################################################
# Run target algorithm for one instance with static parameter values
##########################################################################
def run_target_static(inst_name, param_values):
    return float( subprocess.run(executable.split() + [inst_name] + param_values, stdout = subprocess.PIPE).stdout.decode('utf-8') )
