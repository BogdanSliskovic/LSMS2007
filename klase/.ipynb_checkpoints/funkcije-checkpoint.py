import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import locale
locale.setlocale(locale.LC_ALL, 'sr_RS.UTF-8')

def form(value):
    if isinstance(value, (int, float, np.number)):
        return locale.format_string('%.2f', value, grouping=True)
    return str(value)
pd.options.display.float_format = lambda x: form(x)
np.set_printoptions(formatter={'all': lambda x: form(x)})

def jb( var, alfa = 0.1):
    mi3, mi4 = [((var - var.mean())**momenat).mean() for momenat in [3,4]]
    sigma3, sigma4 = [var.std() ** momenat for momenat in [3,4]]
    S, K = mi3 / sigma3, mi4 / sigma4
    JB = len(var) * (np.square(S) + np.square(K - 3) / 4) / 6
    p = stats.chi2.sf(JB, df=2)
    if p < alfa:
        print(f'Uz rizik greške od {alfa * 100}%, odbacujem nultu hipotezu i zaključujem da se raspodela varijable {var.name} statistički značajno razlikuje od normalne')
    else:
        print(f'Uz rizik greške od {alfa * 100}%, ne odbacujem nultu hipotezu i zaključujem da se raspodela varijable {var.name} ne razlikuje značajno od normalne')
    return pd.Series([JB, p], index= ['JB', 'p'])
