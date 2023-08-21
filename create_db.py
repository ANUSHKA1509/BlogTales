import mysql.connector

my = mysql.connector.connect(
	host="localhost",
	user="root",
	passwd="12A1339@a",
	)

my_cursor = my.cursor()
my_cursor.execute("CREATE DATABASE users")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
	print(db)