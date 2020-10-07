import numpy as np
import sys
from random import random, randint, seed
from math import ceil

instance = sys.argv[1]
size = int(instance)
rate_mu = float(sys.argv[2])
prob_x = float(sys.argv[3])
size_pop = 10
size_offspring = 1

nb_iter = ceil(0.5*size*size)

# Leading ones fitness
def fitness(sol):   
    count = 0 
    for i in range(0, size):
        if (sol[i] == 1): 
            count+= 1  
        else:
            break
    return count

# Uniform crossover
def crossover_uniform(sol1, sol2):
    mask1 = np.random.randint(0, 2, size = np.array(sol1).shape)
    mask2 = np.logical_not(mask1)
    #child
    child = np.add(np.multiply(sol1, mask1), np.multiply(sol2, mask2))
    return child

# Random mutation
def mutation(sol):
    for j in range(0, size):
        if (random()<=rate_mu):            
            sol[j] = 0 if sol[j] == 1 else 1
    return sol



# initialise
pop = np.empty([size_pop, size+1], dtype=int)
for j in range(size_pop):
    pop[j] = [randint(0, 1) for i in range(size+1)]
    pop[j,-1] = fitness(pop[j])

# sort based on fitness
pop = np.array(sorted(pop,key=lambda x: x[-1], reverse=True))

for t in range(nb_iter):
    '''
    print('----------------------------------------------')
    print(pop)
    print('----------------------------------------------')
    '''
    offspring = []
    for i in range(size_offspring):
        r = random()
        if (r<=prob_x):
            #print('OX: ',end='')
            sol1 = pop[randint(0, size_pop-1)]
            sol2 = pop[randint(0, size_pop-1)]
            offspring = crossover_uniform(sol1, sol2)
            offspring[-1] = fitness(offspring)
            #print( str(sol1)+'+'+str(sol2)+'->'+str(offspring) )
        else:
            #print('MU: ',end='')
            sol = pop[randint(0, size_pop-1)]
            #print(str(sol)+'->', end='')
            offspring = mutation(sol)
            offspring[-1] = fitness(offspring)
            #print(offspring)
            
        pop = np.concatenate((pop, [offspring]))

    # soft and reshape population
    pop = np.array(sorted(pop,key=lambda x: x[-1], reverse=True))[0:size_pop]

print(pop)
