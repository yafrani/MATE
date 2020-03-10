import subprocess
from math import floor, ceil

N_values = [10, 20, 50, 100, 200, 500]
for N in N_values:
	K_values = [2, ceil(N/4), ceil(N/2), ceil(3*N/4), N-1]
	for K in K_values:
		inst_name = 'T_8_N_'+str(N)+'_K_'+str(K)+'.npy'
		subprocess.run(['python3', 'LandscapeGeneration.py', str(N), str(K)], stdout = subprocess.PIPE).stdout.decode('utf-8')
