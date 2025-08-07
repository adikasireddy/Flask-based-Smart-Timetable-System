def send_notification(subject, body, to_email=None):
    """
    Send notification - placeholder implementation
    In a real application, this would send actual emails or notifications
    """
    print(f"Notification: {subject}")
    print(f"To: {to_email or 'admin'}")
    print(f"Message: {body}")
    return True

def send_schedule_change_notification(action, schedule_details):
    """
    Send notification when schedule changes occur
    """
    print(f"📅 Schedule {action}:")
    print(f"   Faculty: {schedule_details.get('faculty_name', 'N/A')}")
    print(f"   Day: {schedule_details.get('day', 'N/A')}")
    print(f"   Time: {schedule_details.get('time', 'N/A')}")
    if 'subject' in schedule_details:
        print(f"   Subject: {schedule_details['subject']}")
    if 'room' in schedule_details:
        print(f"   Room: {schedule_details['room']}")
    print("   Notification sent successfully! ✅")

def send_mail(to_email, subject, body):
    """Legacy function for backward compatibility"""
    return send_notification(subject, body, to_email)