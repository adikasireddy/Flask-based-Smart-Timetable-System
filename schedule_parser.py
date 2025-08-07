
try:
    from docx import Document
except ImportError:
    import sys
    print("Error importing docx. Please ensure python-docx is properly installed.")
    sys.exit(1)

from database import clear_all_schedules, add_schedule

def parse_schedule(file_path):
    try:
        document = Document(file_path)
        
        # Clear old data
        clear_all_schedules()

        for table in document.tables:
            for i, row in enumerate(table.rows):
                cells = [cell.text.strip() for cell in row.cells]
                if len(cells) >= 5 and i > 0:  # Skip header row
                    faculty_name, day, time, subject, room = cells[:5]
                    if faculty_name and day and time:  # Only insert if essential fields are not empty
                        add_schedule(faculty_name, day, time, subject, room)
        
        print(f"Successfully parsed schedule from {file_path}")
    except Exception as e:
        print(f"Error parsing schedule: {str(e)}")
        raise e
