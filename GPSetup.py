from math import inf
import datetime

# GP parameters
POP_SIZE        = 20                   # population size
GEN_POP_SIZE    = round(POP_SIZE*.75)  # size of offspring population
MIN_DEPTH       = 2                    # minimum initial tree depth
MAX_DEPTH       = 4                    # maximum initial tree depth
TOURNAMENT_SIZE = 5                    # size of tournament for tournament selection
XO_RATE         = 0.8                  # crossover rate
PROB_MUTATION   = 0.2                  # per-node mutation probability
BLOAT_CONTROL   = False                # True adds bloat control to fitness function

GENERATIONS     = 100 if len(parameters)==1 else 10  # maximal number of generations to evolve programs

# Multi-population GP parameters
MPGP_ITERATIONS = 1 if len(parameters)==1 else 10

# Statistical setting
SAMPLE_RUNS     = 10                   # number of samples per GP tree
STATE_SIGNIFICANCE = 0.02

# Functions
def add(x, y): return x + y
def sub(x, y): return x - y
def mul(x, y): return x * y
def div(x, y): return x / y if y!=0 else inf

FUNCTIONS = [add, sub, mul, div]

FUNCTION_SYM = {
'add':'+', 
'sub':'-', 
'mul':'*', 
'div':'/'
}

# Terminals (problem features + some values)
with open('cfg_instances.txt', 'r') as file:
    FEATURES = file.readline().split()[1:]

TERMINALS = FEATURES + [-2, -1, 1, 2]


#==========================================================
# tunner input
#==========================================================
# Algorithm executable
with open('cfg_executable.txt', 'r') as file:
    executable = file.read().replace('\n', '')

# List of instances
with open('cfg_instances.txt', 'r') as file:
    instances = [line.split() for line in file.readlines()[1:]]

# List of parameters
with open('cfg_parameters.txt', 'r') as file:
    parameters = [line.split() for line in file.readlines()[0:]]


# Date and time
dt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Debugging
debug = True
