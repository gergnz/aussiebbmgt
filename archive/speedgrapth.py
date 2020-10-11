#!/usr/bin/env python

import dateutil.parser
import matplotlib.pyplot as plt 
import sqlite3
from datetime import datetime
conn = sqlite3.connect('aussiebbmgt.db')

c = conn.cursor()

#results = c.execute("select * from speedtestresults where date > '2020-08-11T22:29:50Z' order by id")
results = c.execute("select * from speedtestresults order by id")

up = []
down = []
x = []
  
for i in results.fetchall():  
    up.append(i[4])
    down.append(i[3])
    x.append(dateutil.parser.parse(i[5]))

# plotting the points  
plt.plot(x, up, label='up speed')
plt.plot(x, down, label='down speed')
  
# naming the x axis 
plt.xlabel('Date/Time')
# naming the y axis 
plt.ylabel('Kbps')
  
# giving a title to my graph 
plt.title('Speed Test')

plt.legend()
plt.gcf().autofmt_xdate()
  
# function to show the plot 
plt.savefig('speed.png', bbox_inches='tight')

conn.close()
