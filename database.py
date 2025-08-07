
import sqlite3
import os
from datetime import datetime

DATABASE = 'data/timetable_data.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    return conn

def init_database():
    """Initialize database with tables and default data"""
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    conn = sqlite3.connect(DATABASE)
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

def get_user_by_credentials(email, password):
    """Get user by email and password"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_role(email):
    """Get user role by email"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE email=?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_schedules_by_faculty(faculty_name):
    """Get schedules for a specific faculty"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schedules WHERE faculty_name = ? ORDER BY day, time", (faculty_name,))
    schedules = cursor.fetchall()
    conn.close()
    return schedules

def get_all_faculty_names():
    """Get all unique faculty names"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT faculty_name FROM schedules ORDER BY faculty_name")
    faculty_names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return faculty_names

def get_schedule_by_id(schedule_id):
    """Get schedule by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schedules WHERE id=?", (schedule_id,))
    schedule = cursor.fetchone()
    conn.close()
    return schedule

def add_schedule(faculty_name, day, time, subject, room):
    """Add new schedule"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO schedules (faculty_name, day, time, subject, room) VALUES (?, ?, ?, ?, ?)",
        (faculty_name, day, time, subject, room)
    )
    conn.commit()
    conn.close()

def update_schedule(schedule_id, faculty_name, day, time, subject, room):
    """Update existing schedule"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE schedules SET faculty_name=?, day=?, time=?, subject=?, room=? WHERE id=?",
        (faculty_name, day, time, subject, room, schedule_id)
    )
    conn.commit()
    conn.close()

def delete_schedule(schedule_id):
    """Delete schedule by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedules WHERE id=?", (schedule_id,))
    conn.commit()
    conn.close()

def get_today_schedule(faculty_name, day):
    """Get today's schedule for a faculty"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schedules WHERE faculty_name = ? AND day = ? ORDER BY time", 
                   (faculty_name, day))
    schedules = cursor.fetchall()
    conn.close()
    return schedules

def get_all_schedules():
    """Get all schedules from database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schedules ORDER BY faculty_name, day, time")
    schedules = cursor.fetchall()
    conn.close()
    return schedules

def organize_weekly_schedule(schedules):
    """Organize schedules into weekly format"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    times = set()
    
    # Extract all unique times
    for schedule in schedules:
        times.add(schedule[3])  # time is at index 3
    
    times = sorted(list(times))
    
    # Create weekly schedule structure
    weekly_schedule = {}
    for day in days:
        weekly_schedule[day] = {}
        for time in times:
            weekly_schedule[day][time] = []
    
    # Fill in the schedules
    for schedule in schedules:
        day = schedule[2]
        time = schedule[3]
        if day in weekly_schedule and time in weekly_schedule[day]:
            weekly_schedule[day][time].append({
                'id': schedule[0],
                'faculty_name': schedule[1],
                'subject': schedule[4],
                'room': schedule[5]
            })
    
    return {'schedule': weekly_schedule, 'times': times, 'days': days}

def clear_all_schedules():
    """Clear all schedules from database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedules")
    conn.commit()
    conn.close()
