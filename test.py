# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 00:10:34 2016

@author: evangelion
"""
import os
import hvac
import base64
import redis
import sys
import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='segreto', passwd='segreti', db='segreti')
cur = conn.cursor()



r=redis.StrictRedis()

client = hvac.Client(url='http://localhost:8200', token=os.environ['VAULT_TOKEN'])

assert client.is_authenticated() # => True

def codifica(stringa):
    code = base64.b64encode(stringa)
    enc = client.write('transit/encrypt/foo', plaintext=code)
    ct = enc['data']['ciphertext']
    print ct
    r.lpush('segreti',ct)
    print "writing to db"
    cur.execute("INSERT INTO segreti(segreto) VALUES ('%s')" % ct)
    conn.commit()
    print "wrote to db"
    return ct
    

def decodifica(stringa):
    dec = client.write('transit/decrypt/foo', ciphertext=ct )
    plain64dec = dec['data']['plaintext']
    #print plain64dec
    raw = base64.b64decode(plain64dec)
    #print raw
    return raw

ct = codifica(sys.argv[1])

#code = codifica(sys.argv[1]).split(":")[2]

decodifica(ct)
