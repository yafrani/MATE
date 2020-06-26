from statistics import mean
from copy import deepcopy
from scipy import stats

from GPTree import *
import GPSetup

import subprocess
import random
import io
import timeit
import math

from multiprocessing import Pool

from sympy import simplify, symbols
# import platform
# print(platform.system())

from MPGP import *


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

        self.lbound = float(parameters[param_id][1]) if len(parameters[param_id])>=3 else -999
        self.rbound = float(parameters[param_id][2]) if len(parameters[param_id])>=3 else +999


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
            s = s + ' | {R}=' + str(['%.2f' %float(val) for val in program.regression_values.values()])
            s = s + ' | HASH=' + str(hash(frozenset(program.regression_values.items())))
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
            i=0
            while i < POP_SIZE:
                t = GPTree()
                if i<int(POP_SIZE/2):
                    t.random_tree(grow = True, max_depth = md) # grow
                else:
                    t.random_tree(grow = False, max_depth = md) # full

                # get param values
                self.evaluation_reg(t)
                #print('ok3',t.regression_values, str(simplify(t.infix_expression())))

                # check if param is valid (inside [lbound,rbound])
                valid = True
                for x in t.regression_values.values():
                    if x<self.lbound or x>self.rbound or math.isnan(x):
                        valid = False
                        break

                if any(x.regression_hash == t.regression_hash for x in self.population) or not valid:
                    i = i-1 #review
                else:
                    self.population.append(t) 
                i = i+1
            print('i>>',i, self.lbound, self.rbound)

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
        else:
            # Re-evaluate population:
            # because the other parameters might have changed
            for ind in self.population:
                ind.fitness_history = []
                ind.fitness = -inf


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

            print('PARAM',parameters[self.param_id][0],'| GEN:', gen+1)
            print('REF PARAM >>', GP.ref_param_values)
            print('REF FITNE >>', GP.references)


            # generate a new population of same size
            new_trees = []

            for i in range(GEN_POP_SIZE):
                parent1 = self.selection()
                parent2 = self.selection()
                # mate and mutate
                offspring = parent1.crossover(parent2)
                offspring.mutation()
                # evaluate
                #for i in range(5):

                # TODO: print(offspring)
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
                    _, pval = stats.ranksums(new_scores, current_scores)

                    new_exp = str(simplify(new_trees[i].infix_expression()))
                    current_exp = str(simplify(self.population[j].infix_expression()))
                    
                    if (pval >= STATE_SIGNIFICANCE or new_trees[i].regression_hash == self.population[j].regression_hash or new_exp==current_exp):
                        print('>>', new_trees[i].regression_hash, new_exp, self.population[j].regression_hash, current_exp, pval)
                        # if the new tree is less complex
                        if ( tree_size_new < tree_size_current ):
                            # debug
                            #print('[REPLACE] >> ', tree_size_current,'|',self.population[j].fitness, ' ==> ', tree_size_new, '|', new_trees[i].fitness , ' ## ', end='')
                            # save log
                            log_bloat.write(str(gen+1)+' '+str(tree_size_current)+' '+str(tree_size_new)+' '+ new_trees[i].infix_expression() +'\n')
                            log_bloat.flush()
                            self.population[j] = new_trees[i]
                            #j = j-1

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
        if len(tree.fitness_history)>=SAMPLE_RUNS:
            return None

        # evaluate tree using feature values (inst[1:]) to obtain the numerical parameter value
        # empty list of regression values
        #tree.regression_values = []
        self.evaluation_reg(tree)

        # run target algorithm for each instance
        #start = timeit.default_timer()
        with Pool(SAMPLE_RUNS) as p:
            tree.fitness_history = p.map(self.run_target, [tree]*SAMPLE_RUNS)

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

        return tree.fitness


    def evaluation_reg(self, tree):
        # evaluate tree using feature values (inst[1:]) to obtain the numerical parameter value
        # empty list of regression values
        #tree.regression_values = []
        tree.regression_values = {}
        for inst in instances:
            param_value = tree.compute_tree( [float(i) for i in inst[1:]] )
            # TODO: use dictionary to store
            #tree.regression_values.append(param_value)
            tree.regression_values[inst[0]] = param_value

        # calculate hash for regression values as a "unique" ID
        tree.regression_hash = hash(frozenset(tree.regression_values.items()))


    ##########################################################################
    # Normalise fitness scores using references
    ##########################################################################
    def normalise_scores(self, tree):

        # average over all instances at each previous generation
        norm_fitness_history = []

        for f in tree.fitness_history:
            # "re-normalise", average & add to history list
            norm_fitness_history.append( mean( [f[inst[0]]/GP.references[inst[0]] for inst in instances] ) )

        # calculate final tree fitness by averaging fitness history list
        return norm_fitness_history


    ##########################################################################
    # Run target algorithm for each instance
    ##########################################################################
    def run_target(self, tree):

        scores = {}
        for inst in instances:
            # evaluate tree using feature values (inst[1:]) to obtain the numerical parameter value
            param_value = tree.compute_tree( [float(i) for i in inst[1:]] )

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
    # z=subprocess.run(executable.split() + [inst_name] + param_values, stdout = subprocess.PIPE).stdout.decode('utf-8')
    # print  (   '--->',z     )
    
    param_values = ['999999' if x=='inf' else '-999999' if x=='-inf' else x for x in param_values]
    return float( subprocess.run(executable.split() + [inst_name] + param_values, stdout = subprocess.PIPE).stdout.decode('utf-8') )
