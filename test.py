#vault
import os
import hvac
import base64
import redis
import sys
import pymysql


def codifica(stringa):
    conn = pymysql.connect(host='localhost', port=3306, user='segreto', passwd='segreti', db='segreti')
    cur = conn.cursor()
    client = hvac.Client(url='http://localhost:8200', token=os.environ['VAULT_TOKEN'])
    code = base64.b64encode(stringa)
    enc = client.write('transit/encrypt/foo', plaintext=code)
    ct = enc['data']['ciphertext']
    print ct
    r = redis.StrictRedis()
    r.lpush('segreti',ct)
    print "writing to db"
    cur.execute("INSERT INTO segreti(segreto) VALUES ('%s')" % ct)
    conn.commit()
    print "wrote to db"
    return ct
    

def decodifica(segreto):
    client = hvac.Client(url='http://localhost:8200', token=os.environ['VAULT_TOKEN'])
    dec = client.write('transit/decrypt/foo', ciphertext=segreto )
    plain64dec = dec['data']['plaintext']
    #print plain64dec
    raw = base64.b64decode(plain64dec)
    #print raw
    return raw

