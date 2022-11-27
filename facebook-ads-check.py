import requests
import json
import pandas as pd
import csv
from csv import DictReader
from datetime import datetime
import numpy as np

access_token="INSERT HERE YOUR FACEBOOK DEVELOPER TOKEN"

# Vamos a consultar las cuentas publicitarias que gestiono
request = 'https://graph.facebook.com/v15.0/me/?fields=adaccounts{account_id,name}&access_token=%s'%access_token
result = requests.get(request)
content_dict = json.loads(result.content)
cuentas_filtradas = content_dict['adaccounts']['data']
inversion_lista = []
for i in cuentas_filtradas:
    for key in i:
        if key =='id':
            inversion_lista.append(i[key])

# Recopilamos la inversión de cada cuenta y la añadimos a un diccionario
dicts = {}
lista_gasto = []
for i in inversion_lista:
    date_preset = 'this_month'
    url_base = 'https://graph.facebook.com/v15.0/'
    base2 = '/insights?level=account&date_preset='
    fields = '&fields=spend&access_token=%s'%access_token
    act_id= str(i)
    request = url_base + act_id + base2 + date_preset + fields
    result = requests.get(request)
    inversion_campana = json.loads(result.content)
    campana_filtradas = inversion_campana['data']
    if campana_filtradas==[]:
        campana_filtradas={'spend': float(0.00)}
    else:
        for e in campana_filtradas:
            for key in e:
                if key == 'spend':
                    gasto_inversion=(e[key])
        lista_gasto.append({"id": i, "spend": float(gasto_inversion)})

print ("Capturado con éxito")

#cambiamos el nombre de la columna para que sean iguales en todas las tablas, no es obligatorio, pero queda más limpio

inversiondf = pd.DataFrame.from_dict(lista_gasto)
inversiondf["id_facebook"]=inversiondf["id"]
inversiondf.drop("id", inplace=True, axis=1)

#creamos la variable currentDay para ver el día del mes que estamos para multiplicar más adelante el presupuesto diario por el día del mes.

currentDay = datetime.now().day

# importamos el csv de Numbers y le pasamos que el delimitador es el punto y coma, convertimos los valores en un diccionario.

#cargamos el csv de nuestros datos indicándole que el separador es un punto y coma
inversion_lista = pd.read_csv("testfb.csv", sep = ';', parse_dates=True)
inversiontabla = pd.DataFrame.from_dict(inversion_lista)

#le formateamos los decimales para que las comas sean puntos
inversiontabla["inversion_diaria_fb"]=inversiontabla["inversion_diaria_fb"].str.replace(',','.')

#redondeamos decimales a dos dígitos borramos datos varios y les damos valor cero, creamos la columna de inversion_hoy con la operación matemática

inversiontabla["inversion_diaria_fb"] = pd.to_numeric(inversiontabla["inversion_diaria_fb"]).round(2)
inversiontabla["inversion_facebook"] = pd.to_numeric(inversiontabla["inversion_facebook"]).round(2)
inversiontabla.fillna(0,inplace=True)
inversiontabla["inversion_hoy"] = (inversiontabla["inversion_diaria_fb"]* currentDay).round(2)

# unimos las dos tablas y creamos la tabla final, en este caso he borrado las columnas que de momento no uso: inversion_google, id_google

df_cd = pd.merge(inversiontabla, inversiondf, how='inner', left_on = 'id_facebook', right_on = 'id_facebook')
df_cd.fillna(0,inplace=True)
df_cd.drop("id_google", inplace=True, axis=1)
df_cd.drop("inversion_facebook", inplace=True, axis=1)
df_cd.drop("inversion_google", inplace=True, axis=1)
df_cd.drop("id_facebook", inplace=True, axis=1)
df_cd["gastado"]=df_cd["spend"]
df_cd.drop("spend", inplace=True, axis=1)
df_cd["Porcentaje gastado"]=(df_cd["gastado"]/df_cd["inversion_hoy"]).round(2) * 100
df_cd.fillna(0,inplace=True)
print(df_cd)