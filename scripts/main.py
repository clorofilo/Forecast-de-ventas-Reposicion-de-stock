# -*- coding: utf-8 -*-
"""GH - Propuesta pedidos 2.0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1pBXaWyAY4p9CWNCiYf5tCmSKxWr9D0RR
"""

# @title Librerías
import numpy as np
import pandas as pd
import re
import warnings
from datetime import datetime
from datetime import timedelta
import calendar

warnings.filterwarnings('ignore')

# @title Nombrar archivos
#Cargar Saldo
saldo = 'saldo.xlsx'

#Cargar stock UH y Pedidos UH
uh = 'uh.xlsx'

#Cargar datos MyStore
mystore = 'mystore.xlsx'

#@title Funcs
def ultimas_ventas(df, periodo):
  '''Retorna una lista con el nombre de las columnas que contienen las ventas de
  las últimas 4 semanas (periodo = 'Semana') o los últimos dos meses
  (periodo = 'Ventas')'''
  lista = []
  pattern = re.compile(f'^{periodo}.*')
  for columna in df.columns:
      if len(lista) < 4 and pattern.match(columna) and periodo == 'Semana':
          lista.append(columna)
      elif len(lista) < 2 and pattern.match(columna) and periodo == 'Ventas':
          lista.append(columna)
  return lista

def dias_mes_pasado():
  hoy = datetime.now()
  año_pasado = hoy.year if hoy.month > 1 else hoy.year - 1
  mes_pasado = hoy.month - 1 if hoy.month > 1 else 12
  return calendar.monthrange(año_pasado, mes_pasado)[1]

#Calcular la previsión de venta
def prevision_venta(df,  ajuste_estacional=1, dep=0):
  '''
  df = DataFrame
  dep = columna que especifica el departamento
  ajuste_estacional = ajustes según la época del año. 1 si las ventas se estiman equivalentes al mes anterior. Ajustar valor según época del año.
  '''
  df = df.fillna(0)
  df = df.replace(np.inf, 2)
  if dep == 6:
    ajuste_wharehouse = 0.4
    dias_de_prevision = 90
  elif dep == 7:
    ajuste_wharehouse = 0.45
    dias_de_prevision = 90

  else:
    ajuste_wharehouse = 0.55
    dias_de_prevision = 30

  prevision = df['WEB: Promedio ventas diarias']*ajuste_wharehouse + df['WEB: Promedio ventas diarias'] *(df['Ajuste_MyStore'])
  prevision = prevision * dias_de_prevision
  prevision = prevision*ajuste_estacional

  return round(prevision, 0).astype(int)

def asignar_kam(departamento):
    if departamento in [21]:
        return 'foto'
    elif departamento in [6, 7, 26]:
        return 'audio'
    elif departamento in [3, 17, 18, 30]:
        return 'tv'
    else:
        return 'Otro'

def kam_df(KAM, df):
    return df[df['KAM']== f'{KAM}']

# @title Load data
df = pd.read_excel(saldo)
df_uh = pd.read_excel(uh)
df_mystore = pd.read_excel(mystore)

# @title Transformar DF
FDPs_UH = [131, 133, 135, 136, 236, 237, 4276, 4277]

df_uh = df_uh.rename(columns={'Product code': 'Nº Artículo', 'Effective quantity': 'Unidades Transfer Online'})


#Limpiar datos SALDO
try:
  df.drop(columns=['Online', 'Disponibilidad ', 'IP-W', 'CR-S', 'última EM',
       'Última venta',], inplace=True)
except:
  pass
try:
  df  = df[~df['Mar. Central'].str.contains('REI')] #Eliminar productos REI
except:
  pass
df.dropna(subset=['Mar. Central'], inplace=True)
df = df[~df['Mar. Central'].str.contains('OUT')] #Eliminar productos OUT
for columna in df.columns:
    if df[columna].dtype == float:
        df[columna] = df[columna].fillna(0).astype(int) #Convertir a int
df = df[~df['Nº Dpto.'].isin([0, 53, 55])] #Eliminar Play Station
df["Mar. Central"] = df["Mar. Central"].str.split(", ") #Convertir Flag a lista

#Transformar datos UH
df_uh = df_uh.rename(columns={'Product code': 'Nº Artículo', 'Effective quantity': 'Unidades Transfer Online'})
df_uh = df_uh[['Nº Artículo','Stock UH', 'Pedidos UH', 'Unidades Transfer Online' ]]
if df_uh.iloc[0]['Nº Artículo']=='#':
    df_uh.drop(df_uh.index[0], inplace=True)
df_uh = df_uh.astype(int)
df_uh = df_uh.fillna(0)

#Transformar datos MyStore
df_mystore = df_mystore.fillna(0)
df_mystore = df_mystore.astype(int)

#Unir data
df = pd.merge(df, df_uh, on='Nº Artículo', how='left')
df['Stock UH'] = df['Stock UH'].fillna(0).astype(int)
df['Pedidos UH'] = df['Pedidos UH'].fillna(0).astype(int)
df['Unidades Transfer Online'] = df['Unidades Transfer Online'].fillna(0).astype(int)

#Añadir ajuste de Mystore (% de venta del total MM que es de MyStore)
df_mystore['Ajuste_MyStore'] = (df_mystore['MYSTORE']/(df_mystore['APP']+df_mystore['MOBILE']+df_mystore['DESKTOP'])).round(2)
df_mystore = df_mystore[['ID', 'Ajuste_MyStore']]
df = pd.merge(df, df_mystore, left_on='Nº Artículo', right_on='ID', how='left')

#@title Calcs

#Suma stock
df['Suma_stock'] =  df['Stock'] + df['Alm. 99'] + df['Almacén 19']

#Calcular el promedio diario del total
regex_ventas = re.compile(r'^Ventas\s')
columnas_ventas_mes_df = []
for columna in df.columns:
  if re.match(regex_ventas, columna):
    columnas_ventas_mes_df.append(columna)
df['Ventas_CM_y_LMT'] = df[columnas_ventas_mes_df].sum(axis=1)
dias_columna_venta_mes_df = dias_mes_pasado()+datetime.now().date().day
df['MM total: Promedio ventas diarias'] =df['Ventas_CM_y_LMT']/(dias_mes_pasado()+datetime.now().date().day)

#Calcular el promedio diario de venta web
regex_ventas = re.compile(r'^Semana\s')
columnas_ventas_semana_df = []
for columna in df.columns:
  if re.match(regex_ventas, columna):
    columnas_ventas_semana_df.append(columna)
df['Ventas_suma_semanas_df'] = df[columnas_ventas_semana_df].sum(axis=1)
dias_semana_curso = datetime.now().weekday()+1
dias_ventas_semanas = dias_semana_curso + (len(columnas_ventas_semana_df)-1)*7
df['WEB: Promedio ventas diarias'] = df['Ventas_suma_semanas_df']/dias_ventas_semanas

#Dividir departamentos
df_audio_p = df[df['Nº Dpto.'] == 6]
df_auriculares = df[df['Nº Dpto.'] == 7]
df_otros = df[~df['Nº Dpto.'].isin([6, 7])]

#Ajustar las unidades de MyStore
df['Ajuste_MyStore'] = df.apply(lambda row: 0.96 if (pd.isna(row['Ajuste_MyStore']) and (row['Nº Dpto.'] == 3)) else row['Ajuste_MyStore'], axis=1)
df['Ajuste_MyStore'] = df.apply(lambda row: 0.22 if (pd.isna(row['Ajuste_MyStore']) and (row['Nº Dpto.'] != 3)) else row['Ajuste_MyStore'], axis=1)
df['Ajuste_MyStore'].fillna(0, inplace =True)
df['Ajuste_MyStore'].replace(np.inf, 2, inplace =True)

#Previsión de la venta
#Ajuste estacional
df_audio_p['Prevision_venta'] = prevision_venta(df_audio_p, ajuste_estacional=0.3, dep=6)
df_auriculares['Prevision_venta'] = prevision_venta(df_auriculares, ajuste_estacional=0.4, dep=7)
df_otros['Prevision_venta'] = prevision_venta(df_otros, ajuste_estacional=0.76)

#Unir df
df = pd.concat([df_audio_p, df_auriculares, df_otros])


#Propuesta pedido
df['Propuesta_pedido_prev'] = df['Prevision_venta'] - df['Suma_stock']
df['Propuesta_pedido_prev'] = df['Propuesta_pedido_prev'].map(lambda x: 0 if x<0 else x)
df['Propuesta_pedido_prev'] = df['Propuesta_pedido_prev'].fillna(0).astype(int)
df['Propuesta_pedido_forced'] = df.apply(lambda row: 2 if (row['Propuesta_pedido_prev'] + row['Suma_stock'])<3 else 0, axis=1)
df['Propuesta_pedido'] = df['Propuesta_pedido_prev'] + df['Propuesta_pedido_forced']

#Seleccionar columnas a mostrar
df = df[['Nº Artículo',  'Descripción artículo', 'Mar. Central',
        'Propuesta_pedido',   'MM total: Promedio ventas diarias',
        'WEB: Promedio ventas diarias','Ajuste_MyStore', 'Stock', 'Alm. 99', 'Almacén 19',
        'Stock UH', 'Pedidos UH', 'Unidades Transfer Online','Nº Dpto.', 'Nº FDP', 'FDP']]

df[ 'WEB: Promedio ventas diarias'] = df[ 'WEB: Promedio ventas diarias'].round(2)
df[ 'MM total: Promedio ventas diarias'] = df[ 'MM total: Promedio ventas diarias'].round(2)

#Asignar KAM
df['KAM'] = df['Nº Dpto.'].apply(asignar_kam)

#Definir TV de UH
df['UH'] = False
df.loc[df['Nº FDP'].isin(FDPs_UH), 'UH'] = True

#Solicitar transfer UH
df['Solicitud transfer'] = df.apply(lambda row: True if (row['UH'] == True and row['Stock UH'] > 2 and row['Unidades Transfer Online'] < row['Propuesta_pedido']) else False, axis=1)

#Unidades de solicitud de Transfer a online
df['Unidades Solicitud Transfer a Online'] = df.apply(lambda row: (row['Propuesta_pedido']-row['Unidades Transfer Online']) if row['Propuesta_pedido']  <= (row['Unidades Transfer Online'] + row['Stock UH'] - 2) else row['Stock UH'] - 2 , axis=1)
df['Unidades Solicitud Transfer a Online'] = df.apply(lambda row: 0 if row['Unidades Solicitud Transfer a Online'] < 0 else row['Unidades Solicitud Transfer a Online'], axis=1)

# @title Exportar datos
#Dataframe para cada KAM
Lista_kams = ['foto', 'audio', 'tv']


df_filtered = df[df['Propuesta_pedido'] > 0]

#Columnas para imprimir
columns_to_print = ['Nº Artículo',  'Descripción artículo', 'Mar. Central',
                    'Propuesta_pedido', 'Stock', 'Alm. 99','Almacén 19',
                    'WEB: Promedio ventas diarias', 'Nº Dpto.', 'FDP' ]
columns_to_print_tv = ['Nº Artículo', 'Descripción artículo', 'Mar. Central',
                       'Propuesta_pedido', 'WEB: Promedio ventas diarias',
                       'Ajuste_MyStore', 'Stock', 'Alm. 99', 'Almacén 19',
                       'Unidades Transfer Online', 'Nº Dpto.', 'Nº FDP', 'FDP',
                       'UH', 'Stock UH', 'Pedidos UH', 'Solicitud transfer',
                       'Unidades Solicitud Transfer a Online' ]

#DF para foto
df_foto = kam_df('foto', df_filtered)
df_foto.sort_values(by=['Nº Dpto.', 'Nº FDP', 'Nº Artículo'], ascending=[True, True, True], inplace=True)
df_foto[columns_to_print].to_excel('df_foto.xlsx', index=False)

#DF para audio
df_audio = kam_df('audio', df_filtered)
df_audio.sort_values(by=['Nº Dpto.', 'Nº FDP', 'Nº Artículo'], ascending=[True, True, True], inplace=True)
df_audio[columns_to_print].to_excel('df_audio.xlsx', index=False)

#DF para tv
df_tv = kam_df('tv', df_filtered)
df_tv.sort_values(by=[ 'Nº Dpto.','UH', 'Nº FDP', 'Nº Artículo'], ascending=[False, True, True, True], inplace=True)
df_tv[columns_to_print_tv].to_excel('df_tv.xlsx', index=False)

#DF para planner_uh
df_planner_uh_transfers = df_tv.copy()
df_planner_uh_transfers = df_planner_uh_transfers[df_planner_uh_transfers['Solicitud transfer'] == True]
df_planner_uh_transfers = df_planner_uh_transfers[['Nº Artículo', 'Descripción artículo', 'Mar. Central', 'Unidades Solicitud Transfer a Online',
       'Stock', 'Alm. 99', 'Almacén 19', 'Stock UH', 'Pedidos UH', 'Unidades Transfer Online',
       'Nº Dpto.', 'Nº FDP', 'FDP']]
df_planner_uh_transfers.to_excel('df_planner_uh_transfers.xlsx', index=False)