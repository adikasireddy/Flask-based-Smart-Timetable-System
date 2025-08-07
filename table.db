from docx import Document
import sqlite3

def parse_schedule(file_path):
    conn = sqlite3.connect('data/timetable_data.db')
    cursor = conn.cursor()
    document = Document(file_path)

    # Clear old data
    cursor.execute("DELETE FROM schedules")

    for table in document.tables:
        for i, row in enumerate(table.rows):
            cells = [cell.text.strip() for cell in row.cells]
            if len(cells) >= 5:
                faculty_name, day, time, subject, room = cells[:5]
                cursor.execute("INSERT INTO schedules (faculty_name, day, time, subject, room) VALUES (?, ?, ?, ?, ?)",
                               (faculty_name, day, time, subject, room))
    conn.commit()
    conn.close()