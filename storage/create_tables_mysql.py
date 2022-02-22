import mysql.connector


db_conn = mysql.connector.connect(host="kafka-ijaz.eastus.cloudapp.azure.com", user="user", password="", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
                  CREATE TABLE acceleration_reading
                  (id INT NOT NULL AUTO_INCREMENT,
                  vin_id VARCHAR(17) NOT NULL, 
                  speed INTEGER NOT NULL,
                  watt_hours_per_mile INTEGER NOT NULL,
                  estimated_range INTEGER NOT NULL,
                  timestamp VARCHAR(100) NOT NULL,
                  trace_id VARCHAR(100) NOT NULL,
                  date_created VARCHAR(100) NOT NULL,
                  CONSTRAINT acceleration_reading_pk PRIMARY KEY (id))
                  ''')

db_cursor.execute('''
                  CREATE TABLE environmental_reading
                  (id INT NOT NULL AUTO_INCREMENT,
                  vin_id VARCHAR(17) NOT NULL, 
                  elevation INTEGER NOT NULL,
                  gps_location VARCHAR(100) NOT NULL,
                  grade_incline INTEGER NOT NULL,
                  temperature INTEGER NOT NULL,
                  trace_id VARCHAR(100) NOT NULL,
                  date_created VARCHAR(100) NOT NULL,
                  CONSTRAINT environmental_reading_pk PRIMARY KEY (id))
                  ''')

db_conn.commit()
db_conn.close()