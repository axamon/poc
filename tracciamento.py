import sys
from datetime import datetime
timestamp = str(datetime.now().strftime('%Y%m%d-%H%M'))
oggi = str(datetime.today().strftime('%Y%m%d'))

#print(len(sys.argv))
if len(sys.argv) == 1:
   print("Sintassi: <clientip> <YYYYMMGG default oggi> <httpstatus default 504>")
   sys.exit()

def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

def controllodata(s):
   if len(s) != 8 or not s.isdigit():
      print('Ma che razza di data hai inserito?')
      return False
   else:
      return True

def controllohttpstatus(s):
   if len(s) != 3 or not s.isdigit():
      print('E quello sarebbe un codice di errore http?')
      return False
   else:
      return True

#verifica se ip valido

if len(sys.argv) == 2:
   ipclient = sys.argv[1]
   giorno = oggi
   httpstatus = "504"
   if validate_ip(ipclient) is False:
      print('Non fare il cretino! Ip non valido')
      sys.exit()


if len(sys.argv) == 3:
   ipclient = sys.argv[1]
   if validate_ip(ipclient) is False:
      print('Non fare il cretino! Ip non valido')
      sys.exit()
   giorno = sys.argv[2]
   if controllodata(giorno) is False:
      sys.exit()
   httpstatus = "504"

if len(sys.argv) == 4:
   ipclient = sys.argv[1]
   if validate_ip(ipclient) is False:
      print('Non fare il cretino! Ip non valido')
      sys.exit()
   giorno = sys.argv[2]
   if controllodata(giorno) is False:
      sys.exit()
   httpstatus = sys.argv[3]
   if controllohttpstatus(httpstatus) is False:
      sys.exit()

if len(sys.argv) > 4:
   print("Non ti sembra di esagerare? Troppi parametri!")
   sys.exit()

import pandas as pd
import os
import os.path
import mysql.connector as sql
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


#from openpyxl import load_workbook

#configuro connessione al beneamato redis
#r = redis.StrictRedis(host='172.16.0.20')
#che giorno?



def tracciamento(ipclient,giorno=oggi,httpstatus="504",sample="1T"):
   print(ipclient)
   print(giorno)
   print(httpstatus)
   key=str(giorno)+"_"+str(ipclient)
   #recupera tutti log di errore per ip e giorno in dataframe e lo salva su disco con come key
   if os.path.exists(key) is False:
      #query = "SELECT datereq, respcode from cdnerr."+giorno+" where clientip = inet_aton('"+ipclient+"')"
      query = "SELECT * from cdnerr."+giorno+" where clientip = inet_aton('"+ipclient+"')"
      db_connection = sql.connect(host='10.78.140.105', database='cdnerr', user='cdnmp', password='casper.2355')
      df = pd.read_sql(query, con=db_connection)
      #df.columns=['datereq','respcode']
      df.columns=['id','datereq','edgeip','tts','clientip','resp','respcode','bs','req','url','mt','ua','refer']
      df.to_pickle(key)
      filename = key+'.csv'
      df.to_csv(filename,sep=";")
   df = pd.read_pickle(key) #legge il dataframe da disco
   print("Si riscontrano i seguenti errori:") 
   print(df.respcode.unique())
   erroritrovati = df['respcode'].unique()
   pp = PdfPages(key+timestamp+'.pdf')
   x = 0
   for httpstatus in erroritrovati:
      print(httpstatus)
      if str(httpstatus) == "504":
         colorelinea = "r"
      elif str(httpstatus) == "404":
         colorelinea = "b"
      else:
         colorelinea = "y"
      x = x+1
      erroridf = df.loc[(df.respcode == int(httpstatus))]
      errori = erroridf['respcode']
      errori.index = erroridf['datereq']
      errori = errori.resample(str(sample), how='count')
      plt.figure(x)
      plt.clf()
      grafico = plt.title('Errori '+str(httpstatus)+' per ip '+ipclient+' in data '+giorno)
      plt.ylabel('Errori')
      plt.plot(errori.index, errori, label=str(httpstatus), color=colorelinea)
      plt.legend(bbox_to_anchor=(0., 1), loc=2, borderaxespad=0.)
      plt.figure(x).autofmt_xdate()
      pp.savefig(x)
   pp.close()
   plt.show()

   
tracciamento(ipclient,giorno,httpstatus)
