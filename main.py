import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import visualize as vz


df1 = pd.read_csv("Building0teacher.csv", ';', nrows = 671)
del df1['\t']
df1['Energy'] = df1['Energy'].str.replace(',','.')
df1['Energy'] = pd.to_numeric(df1['Energy'], errors='coerce')
df1['DateTime'] = pd.to_datetime(df1['DateTime'],format='%d.%m.%Y %H:%M')

vz.visualize(df1)
