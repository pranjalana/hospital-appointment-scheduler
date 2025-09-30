from datetime import datetime, date, timedelta
from src.utils.database_manager import DatabaseManager
import logging

class NotificationService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
    
    def send_appointment_reminders(self, days_before=1):
        """Send reminders for upcoming appointments"""
        target_date = date.today() + timedelta(days=days_before)
        
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.appointment_id, p.name as patient_name, p.email, p.phone,
                   d.name as doctor_name, a.appointment_date, a.time_slot
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_date = ? AND a.status = 'scheduled'
        ''', (target_date,))
        
        upcoming_appointments = cursor.fetchall()
        conn.close()
        
        reminders_sent = 0
        for appointment in upcoming_appointments:
            self._send_reminder(appointment)
            reminders_sent += 1
        
        self.logger.info(f"Sent {reminders_sent} appointment reminders for {target_date}")
        return reminders_sent
    
    def _send_reminder(self, appointment):
        """Send individual reminder (simulated)"""
        appointment_id, patient_name, email, phone, doctor_name, appointment_date, time_slot = appointment
        
        print(f"\n=== APPOINTMENT REMINDER ===")
        print(f"To: {patient_name}")
        print(f"Contact: {email} | {phone}")
        print(f"Reminder: Your appointment with {doctor_name}")
        print(f"Date: {appointment_date}")
        print(f"Time: {time_slot}")
        print(f"Appointment ID: {appointment_id}")
        print(f"Please arrive 15 minutes early.")
        print(f"============================\n")
    
    def generate_daily_report(self, report_date=None):
        """Generate daily appointment report for all doctors"""
        if not report_date:
            report_date = date.today()
        
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.doctor_id, d.name as doctor_name, d.specialization,
                   COUNT(a.appointment_id) as total_appointments,
                   SUM(CASE WHEN a.status = 'completed' THEN 1 ELSE 0 END) as completed,
                   SUM(CASE WHEN a.status = 'scheduled' THEN 1 ELSE 0 END) as scheduled
            FROM doctors d
            LEFT JOIN appointments a ON d.doctor_id = a.doctor_id AND a.appointment_date = ?
            GROUP BY d.doctor_id, d.name, d.specialization
            ORDER BY d.name
        ''', (report_date,))
        
        doctor_reports = cursor.fetchall()
        
        print(f"\n📊 DAILY APPOINTMENT REPORT - {report_date}")
        print("=" * 60)
        
        for report in doctor_reports:
            doctor_id, doctor_name, specialization, total, completed, scheduled = report
            print(f"👨‍⚕️  {doctor_name} ({specialization})")
            print(f"   📅 Total: {total} | ✅ Completed: {completed} | ⏰ Scheduled: {scheduled}")
            print("-" * 40)
        
        conn.close()
        return doctor_reports
    
    def notify_emergency_booking(self, appointment_id):
        """Notify about emergency appointment booking"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.name, d.name, a.appointment_date, a.time_slot
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_id = ?
        ''', (appointment_id,))
        
        appointment = cursor.fetchone()
        conn.close()
        
        if appointment:
            patient_name, doctor_name, appointment_date, time_slot = appointment
            print(f"\n🚨 EMERGENCY APPOINTMENT NOTIFICATION")
            print(f"Patient: {patient_name}")
            print(f"Doctor: {doctor_name}")
            print(f"Time: {appointment_date} {time_slot}")
            print(f"Please prioritize this appointment!")
            print(f"========================================\n")
