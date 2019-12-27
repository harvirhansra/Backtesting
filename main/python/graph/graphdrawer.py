import matplotlib.pyplot as plt
import pandas as pd
import termplotlib as tpl

def draw_terminal(x, y):
    fig = tpl.figure()
    fig.plot([x for x in range(0, len(x))], y, width=200, height=60)
    fig.show()

    
def draw_to_image(x, y, path):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    fig.savefig(path)
