from math import inf

# GP parameters
GENERATIONS     = 10    # maximal number of generations to evolve programs
POP_SIZE        = 10    # population size
MIN_DEPTH       = 2     # minimum initial tree depth
MAX_DEPTH       = 4     # maximum initial tree depth
TOURNAMENT_SIZE = 3     # size of tournament for tournament selection
XO_RATE         = 0.8   # crossover rate
PROB_MUTATION   = 0.2   # per-node mutation probability
BLOAT_CONTROL   = False # True adds bloat control to fitness function

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
with open('srt_instances.txt', 'r') as file:
    FEATURES = file.readline().split()[1:]

TERMINALS = FEATURES + [-2, -1, 1, 2]
