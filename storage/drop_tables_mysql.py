import mysql.connector


db_conn = mysql.connector.connect(host="kafka-ijaz.eastus.cloudapp.azure.com", user="user", password="", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
                  DROP TABLE acceleration_reading, environmental_reading
                  ''')

db_conn.commit()
db_conn.close()