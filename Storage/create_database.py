import sqlite3

conn = sqlite3.connect('parking_events.sqlite')

c = conn.cursor()

c.execute('''
          CREATE TABLE IF NOT EXISTS parking_status
          (id INTEGER PRIMARY KEY ASC, 
           meter_id INTEGER NOT NULL,
           device_id VARCHAR(250) NOT NULL,
           status BOOLEAN NOT NULL,
           spot_number INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE IF NOT EXISTS payment_event
          (id INTEGER PRIMARY KEY ASC, 
           meter_id INTEGER NOT NULL,
           device_id VARCHAR(250) NOT NULL,
           amount REAL NOT NULL,
           duration INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
