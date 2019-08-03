GENERATIONS     = 10    # maximal number of generations to run evolution
POP_SIZE        = 10    # population size
MIN_DEPTH       = 2     # minimal initial random tree depth
MAX_DEPTH       = 5     # maximal initial random tree depth
TOURNAMENT_SIZE = 5     # size of tournament for tournament selection
XO_RATE         = 0.8   # crossover rate 
PROB_MUTATION   = 0.2   # per-node mutation probability 
BLOAT_CONTROL   = False # True adds bloat control to fitness function

def add(x, y): return x + y
def sub(x, y): return x - y
def mul(x, y): return x * y

FUNCTIONS = [add, sub, mul]
TERMINALS = ['x', -2, -1, 1, 2] 
