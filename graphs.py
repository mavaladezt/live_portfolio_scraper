from time import sleep
import wget
import numpy as np
import pandas as pd
from random import sample
import sqlite3
from bs4 import BeautifulSoup
import requests
import re
import matplotlib.pyplot as plt

#plt.ion()
#for i in range(50):
#    y = np.random.random([10,1])
#    plt.plot(y)
#    plt.draw()
#    plt.pause(0.001)
#    plt.clf()
db = 'stock.db'

def get_query(db,query):
    try:
        conn = sqlite3.connect(db)
#        print("Connected to SQLITE Database stocks.db")
    except:
        print("Error connecting to stocks.db database.")
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result



def graph():
    plt.ion()
    for i in range(20):
        df = get_query(db,"Select * from live;")
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        y = df.loc[df.symbol=='AAPL']['open']
        plt.clf()
        plt.plot(y)
        plt.draw()
        plt.pause(1)

