import sys
import ipaddress


def ipvalido(ipclient):
   try:
      ip = ipaddress.ip_address(ipclient)
   except ValueError:
      print(str(ipclient)+' non è un ip valido')
      sys.exit()

#verifica se ip è valido
ipclient = sys.argv[1]
ipvalido(ipclient)

import pandas as pd
import ipaddress
import os
import redis
from datetime import datetime
#from openpyxl import load_workbook

#configuro connessione al beneamato redis
r = redis.StrictRedis(host='172.16.0.20')
#che giorno è?
oggi = str(datetime.today().strftime('%Y%m%d'))


def tracciamento(ipclient,giorno=oggi,httpstatus="504"):
   print(ipclient)
   print(giorno)
   print(httpstatus)
   key=str(giorno)+"_"+str(ipclient)
   filename = key+'.xlsx'
   #recupera tutti log di errore per ip e giorno in dataframe
   #salva dataframe in redis key
   #slice dataframe per httpstatus da redis key
   df = pd.read_pickle('pippo2.csv') #salva dataframe in file  
   r.set(key, df.to_msgpack(compress='zlib'))
   test = pd.read_msgpack(r.get(key))
   writer = pd.ExcelWriter(filename, engine='xlsxwriter')
   test.to_excel(writer,ipclient)
   writer.save()
   return test

try:
   giorno = sys.argv[2]
except:
   giorno = oggi
try:
   httpstatus = sys.argv[3]
except:
   httpstatus = "504"
   
tracciamento(ipclient,giorno,httpstatus)
