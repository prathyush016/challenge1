import mysql.connector
import logging
import mysql
import pandas as pd

logging.basicConfig(filename="my_sql.log", format='%(asctime)s %(message)s', filemode='w', level=logging.DEBUG)

mydb=mysql.connector.connect(
    host="localhost",
    user="abc",
    password="password"
)
print(mydb)
mycursor=mydb.cursor()


try:
 mycursor.execute('create database prathyush')
except:
  logging.error('not able to create a database. Please check the connection, or database already created with same name')
try:
 mycursor.execute('create table prathyush.scrapper(Main_Course TEXT(1000), Sub_Course TEXT(1000), Training TEXT(1000), Description TEXT(10000), Mentors TEXT(1000))')
except:
  logging.error("table already exists or please check the connection")

try:
 mycursor.execute('delete from prathyush.scrapper')
except:
  pass

try:
 data = pd.read_csv('course_details.txt', sep="|", header=0)
 df = pd.DataFrame(data)
except:
  pass
try:
 for row in df:
  mycursor.execute('''INSERT INTO prathyush.scrapper (Main_Course,Sub_Course,Training,Description,Mentors) VALUES(?,?,?,?,?)''',row)
  mydb.commit()
except:
  pass
mycursor.close()

