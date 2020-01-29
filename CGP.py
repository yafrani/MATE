from GP import *
from GPSetup import *


# Coevolution GP
class CGP:
    
    def __init__(self, gp = None):
        self.gp = []
        for i in range(len(parameters)):
            self.gp.append( GP() )


    def coevolution(self):

        nb_rep = 100
        for u in range(nb_rep):
            print('=======================================================')
            print('CGP GEN:', nb_rep)
            print('=======================================================')
            for i in range(len(parameters)):
                self.gp[i] = GP(population = self.gp[i].population, param_id = i)
                self.gp[i].evolution()
