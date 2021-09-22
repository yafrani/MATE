from GP import *
from GPSetup import *
from multiprocessing import Process


# Co-Evolution GP
class CoEvolution:
    
    def __init__(self, gp = None):
        self.gp = []
        #self.dt = dt
        for i in range(len(parameters)):
            self.gp.append( GP() )


    def evolution(self):

        print('=======================================================')
        print('Co-Evolution:')
        print('=======================================================')
        nb_params = len(parameters)

        '''
        for i in range(len(parameters)):
            self.evolve_param(i)
        '''
        proc_list = []
        for i in range(len(parameters)):
            p = Process(target=self.evolve_param, args=(i,))
            p.daemon = False
            p.start()
            proc_list.append(p)

        for p in proc_list:
            p.join()
        
        #print('NEW PARAM REFERENCES:')
        #print(GP.ref_param_values)


    def evolve_param(self, i):
        print('PARAMETER p_'+str(i))
        self.gp[i] = GP(population = self.gp[i].population, param_id = i)
        self.gp[i].evolution()
        print('END CE - PARAMETER p_'+str(i))
        
        # store final populations
        result_pop = open("./output/result_pop-" + DT + ".txt", "a+")
        result_pop.write('Parameter: ' + parameters[i][0] + '\n' + self.gp[i].output_csv() + '###############################' + '\n')
        result_pop.flush()
        result_pop.close()
        #==========================================================
