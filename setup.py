import sqlite3

conn = sqlite3.connect('cache.db')
c = conn.cursor()

c.execute('''CREATE TABLE queries 
	(reviews integer, result float, business text, location text, param text)''')

conn.commit()
conn.close()	