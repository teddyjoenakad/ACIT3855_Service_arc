import mysql.connector

db_conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="parking_events"
)

db_cursor = db_conn.cursor()

db_cursor.execute('DROP TABLE IF EXISTS parking_status')
db_cursor.execute('DROP TABLE IF EXISTS payment_event')

db_conn.commit()
db_conn.close()