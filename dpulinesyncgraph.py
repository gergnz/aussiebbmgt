#!/usr/bin/env python

import dateutil.parser
import matplotlib.pyplot as plt 
import sqlite3
from datetime import datetime
conn = sqlite3.connect('aussiebbmgt.db')

c = conn.cursor()

results = c.execute("select * from dpuportstatusresults where completed_at > '2020-08-11T22:29:50Z' order by id")

up = []
down = []
x = []
  
for i in results.fetchall():  
    up.append(i[5])
    down.append(i[6])
    x.append(dateutil.parser.parse(i[7]))

# plotting the points  
plt.plot(x, up, label='up line speed')
plt.plot(x, down, label='down line speed')
  
# naming the x axis 
plt.xlabel('Date/Time')
# naming the y axis 
plt.ylabel('Mbps')
  
# giving a title to my graph 
plt.title('Line Sync Speed')

plt.legend()
plt.gcf().autofmt_xdate()
  
# function to show the plot 
plt.savefig('linesync.png', bbox_inches='tight')

conn.close()
