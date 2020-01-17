from random import random, randint, seed
from statistics import mean
from copy import deepcopy
import matplotlib.pyplot as plt
from IPython.display import Image, display
from graphviz import Digraph, Source 

from GPSetup import *
import subprocess


class GPTree:
    def __init__(self, data = None, left = None, right = None):
        self.data  = data
        self.left  = left
        self.right = right

        # fitness data
        self.fitness_history = []
        self.fitness = -inf

        # regression values data (=parameter values)
        self.regression_values = []
        self.regression_hash = None


    # String label
    def node_label(self):
        if (self.data in FUNCTIONS):
            return self.data.__name__
        else: 
            return str(self.data)

    # Evaluate tree
    def compute_tree(self, features):
        if (self.data in FUNCTIONS):
            return self.data(self.left.compute_tree(features), self.right.compute_tree(features))
        elif self.data in FEATURES: return features[FEATURES.index(self.data)]
        else: return self.data

    # Create random tree using either grow or full method
    def random_tree(self, grow, max_depth, depth = 0):
        if depth < MIN_DEPTH or (depth < max_depth and not grow): 
            self.data = FUNCTIONS[randint(0, len(FUNCTIONS)-1)]
        elif depth >= max_depth:   
            self.data = TERMINALS[randint(0, len(TERMINALS)-1)]
        else: # intermediate depth, grow
            if random () > 0.5: 
                self.data = TERMINALS[randint(0, len(TERMINALS)-1)]
            else:
                self.data = FUNCTIONS[randint(0, len(FUNCTIONS)-1)]
        if self.data in FUNCTIONS:
            self.left = GPTree()          
            self.left.random_tree(grow, max_depth, depth = depth + 1)            
            self.right = GPTree()
            self.right.random_tree(grow, max_depth, depth = depth + 1)

    # Random mutation
    def mutation(self):
        if random() < PROB_MUTATION:
            self.random_tree(grow = True, max_depth = 2)
        elif self.left: self.left.mutation()
        elif self.right: self.right.mutation() 
    
    # Crossover 2 trees at random nodes
    def crossover(self, other):
        # deep copy first parent
        offsping = deepcopy(self)
        # reintialise tree data
        # fitness data
        offsping.fitness_history = []
        offsping.fitness = -inf

        # regression values data
        offsping.regression_values = []
        offsping.regression_hash = None

        if random() < XO_RATE:
            second = other.scan_tree([randint(1, other.size())], None) # 2nd random subtree
            offsping.scan_tree([randint(1, offsping.size())], second) # 2nd subtree "glued" inside 1st tree
        return offsping

    # tree size in nodes
    def size(self):
        if self.data in TERMINALS: return 1
        l = self.left.size()  if self.left  else 0
        r = self.right.size() if self.right else 0
        return 1 + l + r

    def build_subtree(self):
        t = GPTree()
        t.data = self.data
        if self.left:  t.left  = self.left.build_subtree()
        if self.right: t.right = self.right.build_subtree()
        return t

    def scan_tree(self, count, second): # note: count is list, so it's passed "by reference"
        count[0] -= 1
        if count[0] <= 1:
            if not second: # return subtree rooted here
                return self.build_subtree()
            else: # glue subtree here
                self.data  = second.data
                self.left  = second.left
                self.right = second.right
        else:
            ret = None      
            if self.left  and count[0] > 1: ret = self.left.scan_tree(count, second)  
            if self.right and count[0] > 1: ret = self.right.scan_tree(count, second)  
            return ret

    # Equivalent infix expression
    def infix_expression(self):
        exp = ''
        if self.data in FUNCTIONS:
            exp += '('

        if self.left:
            exp += self.left.infix_expression()
        exp += str(self.data if self.data in TERMINALS else FUNCTION_SYM[self.data.__name__])
        if self.right:
            exp += self.right.infix_expression()
        
        if self.data in FUNCTIONS:
            exp += ')'

        return exp


    def draw(self, dot, count): # dot & count are lists in order to pass "by reference" 
        node_name = str(count[0])
        dot[0].node(node_name, self.node_label())
        if self.left:
            count[0] += 1
            dot[0].edge(node_name, str(count[0]))
            self.left.draw(dot, count)
        if self.right:
            count[0] += 1
            dot[0].edge(node_name, str(count[0]))
            self.right.draw(dot, count)

    def draw_tree(self, fname, footer):
        dot = [Digraph()]
        dot[0].attr(kw='graph', label = footer)
        count = [0]
        self.draw(dot, count)
        Source(dot[0], filename = fname + ".gv", format="png").render()
        display(Image(filename = fname + ".gv.png"))
