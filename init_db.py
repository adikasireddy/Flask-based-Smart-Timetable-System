
import sqlite3
import os

def init_database():
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    conn = sqlite3.connect('data/timetable_data.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'lecturer'
        )
    ''')
    
    # Create schedules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_name TEXT NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            subject TEXT NOT NULL,
            room TEXT NOT NULL
        )
    ''')
    
    # Insert default admin user
    cursor.execute('''
        INSERT OR REPLACE INTO users (name, email, password, role) 
        VALUES (?, ?, ?, ?)
    ''', ('Adikasireddy', 'adikasireddy7036@gmail.com', 'adi@9538143', 'admin'))
    
    # Insert sample schedule data
    sample_schedules = [
        ('adikasireddy', 'Monday', '9:00-10:00', 'Database Systems', 'Room 101'),
        ('adikasireddy', 'Monday', '11:00-12:00', 'Web Development', 'Room 102'),
        ('adikasireddy', 'Tuesday', '10:00-11:00', 'Data Structures', 'Room 103'),
        ('adikasireddy', 'Wednesday', '9:00-10:00', 'Software Engineering', 'Room 101'),
        ('adikasireddy', 'Thursday', '2:00-3:00', 'Computer Networks', 'Room 104'),
        ('adikasireddy', 'Friday', '10:00-11:00', 'Machine Learning', 'Room 105'),
    ]
    
    for schedule in sample_schedules:
        cursor.execute('''
            INSERT OR REPLACE INTO schedules (faculty_name, day, time, subject, room) 
            VALUES (?, ?, ?, ?, ?)
        ''', schedule)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()
