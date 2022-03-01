import sqlite3

conn = sqlite3.connect('stats.sqlite')

c = conn.cursor()
c.execute(''' 
          CREATE TABLE stats 
          (id INTEGER PRIMARY KEY ASC,  
           num_acceleration_readings INTEGER NOT NULL, 
           max_acceleration_speed_readings INTEGER, 
           max_acceleration_watt_hours_reading INTEGER, 
           num_environmental_readings INTEGER NOT NULL, 
           max_temp_reading INTEGER, 
           last_updated VARCHAR(100) NOT NULL) 
          ''')

conn.commit()
conn.close()