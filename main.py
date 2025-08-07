
from flask import Flask, render_template, request, redirect, session, flash, jsonify
from schedule_parser import parse_schedule
from notifications import send_schedule_change_notification
from database import (
    init_database, get_user_by_credentials, get_user_role,
    get_schedules_by_faculty, get_all_faculty_names,
    get_schedule_by_id, add_schedule, update_schedule,
    delete_schedule, get_today_schedule
)
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/')
def index():
    # Direct to login page
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_credentials(email, password)

        if user:
            session['user'] = email
            session['user_name'] = user[1]  # Store user name
            # Redirect to main dashboard after login
            return redirect('/main_dashboard')
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/main_dashboard')
def main_dashboard():
    if 'user' not in session:
        return redirect('/login')

    # Get current day
    current_day = datetime.now().strftime('%A')
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get today's schedule for adikasireddy (default)
    schedules = get_today_schedule('adikasireddy', current_day)
    
    # Get all faculty names for dropdown
    faculty_names = get_all_faculty_names()
    if 'adikasireddy' not in faculty_names:
        faculty_names.append('adikasireddy')
    
    return render_template('main_dashboard.html', 
                         schedules=schedules, 
                         current_day=current_day,
                         current_date=current_date,
                         faculty_names=faculty_names,
                         selected_faculty='adikasireddy')

@app.route('/get_faculty_schedule/<faculty_name>')
def get_faculty_schedule(faculty_name):
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    current_day = datetime.now().strftime('%A')
    schedules = get_today_schedule(faculty_name, current_day)
    
    # Convert schedules to JSON format
    schedule_list = []
    for schedule in schedules:
        schedule_list.append({
            'time': schedule[3],
            'subject': schedule[4],
            'Branch': schedule[5],
            'room': schedule[6]
        })
    
    return jsonify({'schedules': schedule_list})

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')
    return render_template('admin_dashbord.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    # Only allow adikasireddy to access lecturer dashboard
    if session['user'] != 'adikasireddy7036@gmail.com':
        flash("Access denied. Only adikasireddy can access this system.")
        return redirect('/logout')

    return render_template('Lecturer Dashboard.html')

@app.route('/view_timetable')
def view_timetable():
    if 'user' not in session:
        return redirect('/login')

    user_role = get_user_role(session['user'])

    if user_role == 'admin':
        # Admin can see and edit all schedules
        faculty_filter = request.args.get('faculty_name', '').strip()
        if faculty_filter:
            schedules = get_schedules_by_faculty(faculty_filter)
        else:
            # Show all schedules for admin
            schedules = get_all_schedules()

        faculty_names = get_all_faculty_names()
        current_filter = faculty_filter if faculty_filter else 'All Faculty'
    else:
        # Only adikasireddy can access as lecturer
        if session['user'] == 'adikasireddy7036@gmail.com':
            schedules = get_schedules_by_faculty('adikasireddy')
            faculty_names = ['adikasireddy']
            current_filter = 'adikasireddy'
        else:
            flash("Access denied. Only adikasireddy can access this system.")
            return redirect('/logout')

    return render_template('view_timetable.html',
                         schedules=schedules,
                         faculty_names=faculty_names,
                         current_filter=current_filter,
                         user_role=user_role)

@app.route('/weekly_timetable')
def weekly_timetable():
    if 'user' not in session:
        return redirect('/login')

    user_role = get_user_role(session['user'])
    faculty_filter = request.args.get('faculty_name', '').strip()
    
    if user_role == 'admin':
        if faculty_filter:
            schedules = get_schedules_by_faculty(faculty_filter)
        else:
            schedules = get_all_schedules()
        faculty_names = get_all_faculty_names()
        current_filter = faculty_filter if faculty_filter else 'All Faculty'
    else:
        schedules = get_schedules_by_faculty('adikasireddy')
        faculty_names = ['adikasireddy']
        current_filter = 'adikasireddy'

    # Organize schedules by day and time for weekly view
    weekly_schedule = organize_weekly_schedule(schedules)
    
    return render_template('weekly_timetable.html',
                         weekly_schedule=weekly_schedule,
                         faculty_names=faculty_names,
                         current_filter=current_filter,
                         user_role=user_role)

@app.route('/edit_schedule/<int:schedule_id>', methods=['GET', 'POST'])
def edit_schedule(schedule_id):
    if 'user' not in session:
        return redirect('/login')

    user_role = get_user_role(session['user'])
    schedule = get_schedule_by_id(schedule_id)

    if not schedule:
        return jsonify({'success': False, 'message': 'Schedule not found!'})

    # Admin can edit any schedule, lecturer can only edit their own
    if user_role != 'admin':
        if schedule[1] != 'adikasireddy' or session['user'] != 'adikasireddy7036@gmail.com':
            return jsonify({'success': False, 'message': 'Access denied.'})

    if request.method == 'POST':
        faculty_name = request.form['faculty_name']
        day = request.form['day']
        time = request.form['time']
        subject = request.form['subject']
        room = request.form['room']

        update_schedule(schedule_id, faculty_name, day, time, subject, room)

        # Send notification
        schedule_details = {
            'faculty_name': faculty_name,
            'day': day,
            'time': time,
            'subject': subject,
            'room': room
        }
        send_schedule_change_notification("Updated", schedule_details)

        return jsonify({'success': True, 'message': 'Schedule updated successfully!'})

    return render_template('edit_schedule.html', schedule=schedule, user_role=user_role)

@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule_route():
    if 'user' not in session:
        return redirect('/login')

    user_role = get_user_role(session['user'])

    if user_role != 'admin' and session['user'] != 'adikasireddy7036@gmail.com':
        return jsonify({'success': False, 'message': 'Access denied. Only adikasireddy can add schedules.'})

    if request.method == 'POST':
        # Force faculty_name to be adikasireddy
        faculty_name = 'adikasireddy'
        day = request.form['day']
        time = request.form['time']
        subject = request.form['subject']
        room = request.form['room']

        add_schedule(faculty_name, day, time, subject, room)

        # Send notification
        schedule_details = {
            'faculty_name': faculty_name,
            'day': day,
            'time': time,
            'subject': subject,
            'room': room
        }
        send_schedule_change_notification("Added", schedule_details)

        return jsonify({'success': True, 'message': 'New schedule added successfully!'})

    return render_template('add_schedule.html')

@app.route('/delete_schedule/<int:schedule_id>')
def delete_schedule_route(schedule_id):
    if 'user' not in session:
        return redirect('/login')

    user_role = get_user_role(session['user'])
    schedule = get_schedule_by_id(schedule_id)

    if not schedule:
        return jsonify({'success': False, 'message': 'Schedule not found!'})

    # Admin can delete any schedule, lecturer can only delete their own
    if user_role != 'admin':
        if schedule[1] != 'adikasireddy' or session['user'] != 'adikasireddy7036@gmail.com':
            return jsonify({'success': False, 'message': 'Access denied.'})

    delete_schedule(schedule_id)

    # Send notification
    schedule_details = {
        'faculty_name': schedule[1],
        'day': schedule[2],
        'time': schedule[3]
    }
    send_schedule_change_notification("Deleted", schedule_details)

    return jsonify({'success': True, 'message': 'Schedule deleted successfully!'})

@app.route('/upload_schedule', methods=['GET', 'POST'])
def upload_schedule():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        try:
            # Use the uploaded document
            doc_path = 'attached_assets/DEPT FACULTY INDIVIDUAL_1753639629022.docx'
            if os.path.exists(doc_path):
                parse_schedule(doc_path)
                return jsonify({'success': True, 'message': 'Schedule uploaded and parsed successfully!'})
            else:
                return jsonify({'success': False, 'message': 'Document file not found!'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error parsing document: {str(e)}'})

    return render_template('upload_schedule.html')

@app.route('/today_schedule')
def today_schedule():
    if 'user' not in session:
        return redirect('/login')

    # Get current day
    current_day = datetime.now().strftime('%A')

    # Get today's schedule for adikasireddy
    schedules = get_today_schedule('adikasireddy', current_day)

    return render_template('today_schedule.html', schedules=schedules, current_day=current_day)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_name', None)
    return redirect('/')

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
