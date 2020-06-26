import numpy as np
from os.path import expanduser  # new
import matplotlib.pyplot as plt
import sys
from math import log, ceil
import os # new
import re
from random import random, randint, seed

instance_name = sys.argv[1]
mut_rate = float(sys.argv[2])          # | probability of a long jump in a given round

NK_landscape = np.load('./input/NK_model/instances/'+instance_name)

[N,K,T] = list(map(int, re.findall(r'N(\d+)K(\d+)T(\d+)\.npy', instance_name)[0] ))

i = 1 # number of landscapes

# budget will be tricky...
t = ceil(N*log(N)) # time periods set to 50 initially

power_key = np.power(2, np.arange(N - 1, -1, -1))


# *** 2. LOCAL SEARCH EA***************************************

Output2 = np.zeros((i, t))

for i1 in np.arange(i):
    combination = np.random.binomial(1, 0.5, N)  # gen initial combination
    row = np.sum(combination*power_key)  # finding the address in the array
    fitness = NK_landscape[i1, row, 2*N]  # piggyback on work done previously
    max_fit = np.max(NK_landscape[i1, :, 2*N])
    min_fit = np.min(NK_landscape[i1, :, 2*N])
    fitness_norm = (fitness - min_fit)/(max_fit - min_fit)  # normalize 0 to 1
    for t1 in np.arange(t):  # time for local search
        Output2[i1, t1] = fitness_norm
        new_combination = combination.copy()
        for j in range(0, N):
        	if (random()<=mut_rate): 
        		new_combination[j] = 0 if new_combination[j] == 1 else 1

        row = np.sum(new_combination*power_key)
        new_fitness = NK_landscape[i1, row, 2*N]
        if new_fitness > fitness:  # if we have found a better combination
            combination = new_combination.copy()
            fitness = new_fitness.copy()
            fitness_norm = (fitness - min_fit)/(max_fit - min_fit)
        # otherwise all stays the same as in the previous round
Fitness2 = np.mean(Output2, axis=0)

print(str(Fitness2[t-1]),end='')
