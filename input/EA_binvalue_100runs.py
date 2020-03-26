#!/usr/bin/python3

################################################################################
# DESC:
# RLS for binary value
# 
# USAGE:
# ./randsearch.py <instance-name> <param>
# - instance-name: leading one size
# - param: mutation rate
#
# EXAMPLE:
# - python3 EA_binvalue.py 10 0.5 1
#
# number of iterations is set to size*log(size) # try with n^2
################################################################################

import sys
from random import random, randint, seed
from math import log, ceil, exp
import copy

n=[10,20,50,100,200,500]
nb_run=100

def fitness(sol):   
    result = 0 
    for i in range(0, size): 
        result=result+(2**(size-(i+1))*sol[i])
    return result


for instance in n:
    size = int(instance)
    vec_rate=[1/size, 1.5/size, 2/size, 2.5/size, 3/size, 4/size, 5/size]
    for mut_rate in vec_rate:
        vec_iter = [ceil(exp(1)*size*log(size)), ceil(2*exp(1)*size*log(size))] 
        for nb_iter in vec_iter:
            for run in range(0, nb_run):
                nb_hit=nb_iter+1
                print("Instance: bin-value", str(instance), str(mut_rate), str(nb_iter), str(run))

                sol1 = [randint(0, 1) for i in range(size)] # select tournament contenders
                fsol1 = fitness(sol1)
                for i in range(1, nb_iter+1):

                    # clone current solution
                    solx = sol1.copy()

                    # flip each bit according to the mutation rate
                    for j in range(0, size):
                        if (random()<=mut_rate): 
                            solx[j] = 0 if solx[j] == 1 else 1

                    # check if the new solution is better than the current one
                    fsolx = fitness(solx)
                    
                    if (fsolx>fsol1):
                        sol1 = solx
                        fsol1 = fsolx

                    if (nb_hit==nb_iter+1 and fsol1==size):
                        nb_hit=i

                #print('Score: ', end='')

                result_line = 'BinValue' + ';' + str(instance)+ ';' + str(nb_iter)+ ';' + 'EA'+ ';' + str(mut_rate)+';' + str(run) + ';' + str(fsol1)+ ';' + str(nb_hit)
                #print (result_line)
                # save result
                fmet = open('output-BinValue-EA.csv', 'a')
                fmet.write(result_line+'\n')
                fmet.flush()
                fmet.close()
