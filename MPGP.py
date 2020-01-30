from GP import *
from GPSetup import *


# Coevolution GP
class MPGP:
    
    def __init__(self, gp = None):
        self.gp = []
        for i in range(len(parameters)):
            self.gp.append( GP() )


    def coevolution(self):

        nb_rep = len(parameters)**2
        for u in range(nb_rep):
            print('=======================================================')
            print('CGP GEN:', u)
            print('=======================================================')
            for i in range(len(parameters)):
                self.gp[i] = GP(population = self.gp[i].population, param_id = i)
                self.gp[i].evolution()
