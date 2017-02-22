import pandas as pd
import matplotlib.pyplot as plt

def visualize(df):
    df.plot(x='DateTime', y='Energy')
    plt.show()
