import pandas as pd
import matplotlib.pyplot as plot
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (15, 8),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'medium',
         'ytick.labelsize':'x-large'}
plot.rcParams.update(params)

def visualize(df):
    """
    df[df['Anomaly'] == True].plot()
    df.plot(x='DateTime', y='Energy')
    plot.show()
    """
    df1 = df[df['Anomaly'] == True]
    plot.figure("Chart")
    plot.plot(df['DateTime'], df['Energy'], color='b', label="Normal")
    plot.plot(df1['DateTime'], df1['Energy'], color='r', label="Anomaly")
    plot.xlabel('DateTime')
    plot.ylabel('Energy')
    plot.grid(True)
    plot.legend()
    plot.show()
