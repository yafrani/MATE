# tiny genetic programming plus, by moshe sipper, www.moshesipper.com
# graphic output, dynamic progress display, bloat-control option 
# need to install https://pypi.org/project/graphviz/

from random import random, randint, seed
from statistics import mean
from copy import deepcopy
import matplotlib.pyplot as plt
from IPython.display import Image, display
from graphviz import Digraph, Source 

from genData import *
from GPTree import GPTree
from GPSetup import *


def init_population(): # ramped half-and-half
    pop = []
    for md in range(3, MAX_DEPTH + 1):
        for i in range(int(POP_SIZE/6)):
            t = GPTree()
            t.random_tree(grow = True, max_depth = md) # grow
            pop.append(t) 
        for i in range(int(POP_SIZE/6)):
            t = GPTree()
            t.random_tree(grow = False, max_depth = md) # full
            pop.append(t) 
    return pop

def error(individual, dataset):
    return mean([abs(individual.compute_tree(ds[0]) - ds[1]) for ds in dataset])

def fitness(individual, dataset): 
    if BLOAT_CONTROL:
        return 1 / (1 + error(individual, dataset) + 0.01*individual.size())
    else:
        return 1 / (1 + error(individual, dataset))

def selection(population, fitnesses): # select one individual using tournament selection
    tournament = [randint(0, len(population)-1) for i in range(TOURNAMENT_SIZE)] # select tournament contenders
    tournament_fitnesses = [fitnesses[tournament[i]] for i in range(TOURNAMENT_SIZE)]
    return deepcopy(population[tournament[tournament_fitnesses.index(max(tournament_fitnesses))]]) 

def prepare_plots():
    fig, axarr = plt.subplots(2, sharex=True)
    fig.canvas.set_window_title('EVOLUTIONARY PROGRESS')
    fig.subplots_adjust(hspace = 0.5)
    axarr[0].set_title('error', fontsize=14)
    axarr[1].set_title('mean size', fontsize=14)
    plt.xlabel('generation', fontsize=18)
    plt.ion() # interactive mode for plot
    axarr[0].set_xlim(0, GENERATIONS)
    axarr[0].set_ylim(0, 1) # fitness range
    xdata = []
    ydata = [ [], [] ]
    line = [None, None]
    line[0], = axarr[0].plot(xdata, ydata[0], 'b-') # 'b-' = blue line    
    line[1], = axarr[1].plot(xdata, ydata[1], 'r-') # 'r-' = red line
    return axarr, line, xdata, ydata

def plot(axarr, line, xdata, ydata, gen, pop, errors, max_mean_size):
    xdata.append(gen)
    ydata[0].append(min(errors))
    line[0].set_xdata(xdata)
    line[0].set_ydata(ydata[0])
    sizes = [ind.size() for ind in pop]
    if mean(sizes) > max_mean_size[0]:
        max_mean_size[0] = mean(sizes)
        axarr[1].set_ylim(0, max_mean_size[0])
    ydata[1].append(mean(sizes))
    line[1].set_xdata(xdata)
    line[1].set_ydata(ydata[1])
    plt.draw()  
    plt.pause(0.01)





def main():
    # init stuff
    seed() # init internal state of random number generator
    dataset = generate_dataset()
    population= init_population() 
    best_of_run = None
    best_of_run_error = 1e20 
    best_of_run_gen = 0
    fitnesses = [fitness(ind, dataset) for ind in population]
    max_mean_size = [0] # track maximal mean size for plotting
    axarr, line, xdata, ydata = prepare_plots()

    # go evolution!
    for gen in range(GENERATIONS):        
        nextgen_population=[]
        for i in range(POP_SIZE):
            parent1 = selection(population, fitnesses)
            parent2 = selection(population, fitnesses)
            parent1.crossover(parent2)
            parent1.mutation()
            nextgen_population.append(parent1)
        population=nextgen_population
        fitnesses = [fitness(ind, dataset) for ind in population]
        errors = [error(ind, dataset) for ind in population]
        if min(errors) < best_of_run_error:
            best_of_run_error = min(errors)
            best_of_run_gen = gen
            best_of_run = deepcopy(population[errors.index(min(errors))])
            print("________________________")
            best_of_run.draw_tree("best_of_run",\
                                  "gen: " + str(gen) + ", error: " + str(round(best_of_run_error,3)))
        plot(axarr, line, xdata, ydata, gen, population, errors, max_mean_size)
        if best_of_run_error <= 1e-5: break
    
    endrun = "_________________________________________________\nEND OF RUN (bloat control was "
    endrun += "ON)" if BLOAT_CONTROL else "OFF)"
    print(endrun)
    s = "\n\nbest_of_run attained at gen " + str(best_of_run_gen) + " and has error=" + str(round(best_of_run_error,3))
    best_of_run.draw_tree("best_of_run",s)
    
if __name__== "__main__":
    main()
