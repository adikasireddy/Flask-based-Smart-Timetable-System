
import sqlite3

# Connect to the database
conn = sqlite3.connect('data/timetable_data.db')
cursor = conn.cursor()

# Insert admin user
admin_email = "adikasireddy7036@gmail.com"
admin_password = "adi@9538143"
admin_role = "admin"

try:
    cursor.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", 
                   (admin_email, admin_password, admin_role))
    conn.commit()
    print(f"Admin user '{admin_email}' added successfully!")
except sqlite3.IntegrityError:
    print(f"User '{admin_email}' already exists in the database.")
except Exception as e:
    print(f"Error adding admin user: {e}")
finally:
    conn.close()
