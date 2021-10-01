#!/usr/bin/env python3
# coding: utf-8

# In[ ]:
import pandas as pd  
import numpy as np
import math
from datetime import datetime
from IPython.display import display, HTML
import sys
from funcoes import *
from IPython.core.interactiveshell import InteractiveShell  
InteractiveShell.ast_node_interactivity = "all"

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


if len(sys.argv) < 3:
    print('Use: idw threshold alpha')
    exit(0)

threshold = int(sys.argv[1]) 
alpha  = int(sys.argv[2])

# In[ ]:


#dict with coordinates
coord_gauges = '/home/mary/mc/IDW method/estacoes_planicie.xlsx'
df_coord = pd.read_excel(coord_gauges)
#df_coord = df_coord.drop(['Name'], axis=1)
# transform gauge names from int to strings
df_coord['Gauge'] = df_coord['Gauge'].astype(str)
coords = df_coord.set_index('Gauge').T.to_dict()


# In[ ]:


#rainfall timeseries
data = '/home/mary/mc/IDW method/consisted_rain_gauges_planicie.xlsx'
gauge_data = pd.read_excel(data)
gauge_data = gauge_data.set_index(['Date'])
# transform gauge names from int to strings
gauge_data.columns = [str(c) for c in gauge_data.columns]


# In[ ]:


filter_gauges = gauge_data.notna().dot(gauge_data.columns+',').str.rstrip(',')
filter_gauges = pd.DataFrame(filter_gauges)
filter_gauges.index = pd.to_datetime(filter_gauges.index)
df = pd.DataFrame(filter_gauges).reset_index()
groups = df.groupby(0)['Date'].apply(list).reset_index(name='dias')
groups.columns = ['gauges', 'dias']
#groups['dias']


# In[ ]:


meus_dias = ['2000-06-07', '2000-06-08']
gauge_data.loc[gauge_data.index.isin(meus_dias)]


# In[ ]:


dfs = []
for dias in groups['dias']:
    meus_dias = [dia.strftime("%Y-%m-%d") for dia in dias]
    df = gauge_data.loc[gauge_data.index.isin(meus_dias)]
    dfs.append(df)


# In[ ]:


# get the names of gauges w/ values at each line of gauge_data
filter_gauges = gauge_data.notna().dot(gauge_data.columns+',').str.rstrip(',')
dfs = pd.DataFrame(filter_gauges)


# In[ ]:


gauge_data


# In[ ]:


mylist = filter_gauges.values.tolist()
gauge_list = []
for l in mylist:
    gauge_list.append(l.split(','))
dfinho = pd.DataFrame(gauge_list)


# In[ ]:


lista2 = []
# percorrendo cada linha de instante de tempo de chuva
for i, list_gauges in enumerate(gauge_list):
    # pegando lista de chuvas nao nulas
    rainfall_values = gauge_data.iloc[i].dropna().tolist()
    # se tiver chuva em apenas uma estacao, nao precisa interpolar
    if len(rainfall_values)<2:
        continue
        
    final_idw = idw_all(list_gauges, rainfall_values, threshold, coords, alpha)
    lista2.append(final_idw)


# In[ ]:


lista2 = pd.DataFrame(lista2)
lista2 = lista2.rename(columns = {0: 'idw_values', 1: 'gauges', 2: 'unknow_id', 3: 'real_values'})


# In[ ]:


lista2['n_gauges'] = lista2['gauges'].apply(count_gauges)


# In[ ]:


def sMAE(sim, obs):
    lista_errors = []
    for s, o in zip(sim, obs):
        lista_errors.append(abs(o-s))
    return lista_errors

def calc_sMAE(x):
    return sMAE(x['idw_values'], x['real_values'])

def sMAPEabs(sim, obs):
    lista_errors = []
    for s, o in zip(sim, obs):
        lista_errors.append(abs(o-s))
    return lista_errors

def sMAPErel(sim, obs):
    lista_errors = []
    for s, o in zip(sim, obs):
        lista_errors.append(o+s)
    return lista_errors

def calc_sMAPEabs(x):
    return sMAPEabs(x['idw_values'], x['real_values'])

def calc_sMAPErel(x):
    return sMAPErel(x['idw_values'], x['real_values'])

lista2['erro_abs'] = lista2.apply(lambda x: calc_sMAPEabs(x), axis=1)
lista2['erro_rel'] = lista2.apply(lambda x: calc_sMAPErel(x), axis=1)


def convert2tuple(x):
    tuplinha = []
    for qtde, erro_abs, erro_rel, erro in zip(x['n_gauges'], x['erro_abs'], x['erro_rel'],  x['erro_rel']):
        tuplinha.append((qtde, erro_abs, erro_rel, erro))
    return tuplinha

lista2['dicio'] = lista2.apply(lambda x: convert2tuple(x), axis=1)



df = lista2[['dicio']].explode('dicio').reset_index().drop('index', axis=1)



df[['qtde','erro_abs','erro_rel','erro']] = pd.DataFrame(df['dicio'].tolist(), index=df.index)
df2 = df.drop('dicio', axis=1)
#erro = df2.to_excel('planalto_'+str(alpha)+'_'+str(threshold)+'_'+'erro.xlsx', index = False)

sMAPE = pd.DataFrame(df2.groupby('qtde').sum().reset_index())
sMAPE['erro'] = sMAPE['erro_abs']/sMAPE['erro_rel']
sMAPE
sMAPE = sMAPE.to_excel('planicie_'+str(alpha)+'_'+str(threshold)+'_'+'sMAPE.xlsx',index = False)


