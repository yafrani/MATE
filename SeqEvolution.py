from GP import *
from GPSetup import *


# Sequential evolution GP
class SeqEvolution:
    
    def __init__(self, gp = None):
        self.gp = []
        for i in range(len(parameters)):
            self.gp.append( GP() )


    def evolution(self):

        nb_rep = MPGP_ITERATIONS
        for u in range(nb_rep):
            print('=======================================================')
            print('CGP GEN:', u)
            print('=======================================================')
            for i in range(len(parameters)):
                self.gp[i] = GP(population = self.gp[i].population, param_id = i)
                self.gp[i].evolution()
