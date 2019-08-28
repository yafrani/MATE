import matplotlib.pyplot as plt
from IPython.display import Image, display
from graphviz import Digraph, Source 

# plotting functions
def prepare_plots():
    fig, axarr = plt.subplots(2, sharex=True)
    fig.canvas.set_window_title('EVOLUTIONARY PROGRESS')
    fig.subplots_just(hspace = 0.5)
    axarr[0].set_title('error', fontsize=14)
    axarr[1].set_title('mean size', fontsize=14)
    plt.xlabel('generation', fontsize=18)
    plt.ion() # interactive mode for plot
    axarr[0].set_xlim(0, GENERATIONS)
    axarr[0].set_ylim(0, 1) # fitness range
    xdata = []
    ydata = [ [], [] ]
    line = [None, None]
    line[0], = axarr[0].plot(xdata, ydata[0], 'b-') # 'b-' = blue line    
    line[1], = axarr[1].plot(xdata, ydata[1], 'r-') # 'r-' = red line
    return axarr, line, xdata, ydata

def plot(axarr, line, xdata, ydata, gen, pop, errors, max_mean_size):
    xdata.append(gen)
    ydata[0].append(min(errors))
    line[0].set_xdata(xdata)
    line[0].set_ydata(ydata[0])
    sizes = [ind.size() for ind in pop]
    if mean(sizes) > max_mean_size[0]:
        max_mean_size[0] = mean(sizes)
        axarr[1].set_ylim(0, max_mean_size[0])
    ydata[1].append(mean(sizes))
    line[1].set_xdata(xdata)
    line[1].set_ydata(ydata[1])
    plt.draw()  
    plt.pause(0.01)