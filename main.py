import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import visualize as vz


teacher = pd.read_csv("data\Building0teacher.csv", ';', nrows = 671)
del teacher['\t']
teacher['Energy'] = teacher['Energy'].str.replace(',','.')
teacher['Energy'] = pd.to_numeric(teacher['Energy'], errors='coerce')
teacher['DateTime'] = pd.to_datetime(teacher['DateTime'],format='%d.%m.%Y %H:%M')

vz.visualize(teacher)
