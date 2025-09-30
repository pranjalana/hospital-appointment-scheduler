
#!/usr/bin/env python3
"""
Hospital Patient Appointment Scheduler
Main Application Interface
"""

import sys
from datetime import datetime, date, time, timedelta
from src.services.appointment_service import AppointmentService
from src.services.schedule_service import ScheduleService
from src.services.notification_service import NotificationService
from src.services.analytics_service import AnalyticsService
from src.utils.database_manager import DatabaseManager
from database.sample_data import load_sample_data

class HospitalSchedulerApp:
    def __init__(self):
        self.appointment_service = AppointmentService()
        self.schedule_service = ScheduleService()
        self.notification_service = NotificationService()
        self.analytics_service = AnalyticsService()
        self.db_manager = DatabaseManager()
    
    def display_menu(self):
        """Display main menu"""
        print("\n🏥 HOSPITAL APPOINTMENT SCHEDULER")
        print("=" * 50)
        print("1.  Book New Appointment")
        print("2.  Book Emergency Appointment")
        print("3.  Cancel Appointment")
        print("4.  Complete Appointment")
        print("5.  View Patient Appointments")
        print("6.  Set Doctor Schedule")
        print("7.  Check Doctor Availability")
        print("8.  Send Appointment Reminders")
        print("9.  Generate Daily Report")
        print("10. View Analytics & Performance")
        print("11. Load Sample Data")
        print("12. Exit")
        print("=" * 50)
    
    def run(self):
        """Main application loop"""
        print("🚀 Hospital Appointment Scheduler Started!")
        print("💡 Tip: Run 'Load Sample Data' first to test the system")
        
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-12): ").strip()
            
            try:
                if choice == '1':
                    self.book_appointment()
                elif choice == '2':
                    self.book_emergency_appointment()
                elif choice == '3':
                    self.cancel_appointment()
                elif choice == '4':
                    self.complete_appointment()
                elif choice == '5':
                    self.view_patient_appointments()
                elif choice == '6':
                    self.set_doctor_schedule()
                elif choice == '7':
                    self.check_doctor_availability()
                elif choice == '8':
                    self.send_reminders()
                elif choice == '9':
                    self.generate_daily_report()
                elif choice == '10':
                    self.view_analytics()
                elif choice == '11':
                    self.load_sample_data()
                elif choice == '12':
                    print("👋 Thank you for using Hospital Appointment Scheduler!")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def book_appointment(self):
        """Book a new appointment"""
        print("\n📅 BOOK NEW APPOINTMENT")
        
        # Get patient ID
        patient_id = int(input("Enter Patient ID: "))
        patient = self.db_manager.get_patient(patient_id=patient_id)
        if not patient:
            print("❌ Patient not found!")
            return
        
        # Get doctor ID
        doctor_id = int(input("Enter Doctor ID: "))
        doctor = self.db_manager.get_doctor(doctor_id)
        if not doctor:
            print("❌ Doctor not found!")
            return
        
        # Get appointment date
        date_str = input("Enter appointment date (YYYY-MM-DD): ")
        appointment_date = date.fromisoformat(date_str)
        
        # Get preferred time
        time_str = input("Enter preferred time (HH:MM): ")
        preferred_time = time.fromisoformat(time_str)
        
        # Book appointment
        appointment_id, message = self.appointment_service.book_appointment(
            patient_id, doctor_id, appointment_date, preferred_time
        )
        
        if appointment_id:
            print(f"✅ {message}")
            print(f"📋 Appointment ID: {appointment_id}")
        else:
            print(f"❌ {message}")
    
    def book_emergency_appointment(self):
        """Book emergency appointment"""
        print("\n🚨 BOOK EMERGENCY APPOINTMENT")
        
        patient_id = int(input("Enter Patient ID: "))
        doctor_id = int(input("Enter Doctor ID: "))
        
        appointment_id, message = self.appointment_service.book_emergency_appointment(
            patient_id, doctor_id, date.today()
        )
        
        if appointment_id:
            print(f"✅ {message}")
            print(f"📋 Emergency Appointment ID: {appointment_id}")
        else:
            print(f"❌ {message}")
    
    def cancel_appointment(self):
        """Cancel an appointment"""
        print("\n❌ CANCEL APPOINTMENT")
        appointment_id = int(input("Enter Appointment ID to cancel: "))
        
        if self.appointment_service.cancel_appointment(appointment_id):
            print("✅ Appointment cancelled successfully!")
        else:
            print("❌ Appointment not found or already cancelled!")
    
    def complete_appointment(self):
        """Complete an appointment with medical details"""
        print("\n✅ COMPLETE APPOINTMENT")
        appointment_id = int(input("Enter Appointment ID: "))
        diagnosis = input("Enter diagnosis: ")
        prescription = input("Enter prescription: ")
        notes = input("Enter notes: ")
        
        if self.appointment_service.complete_appointment(
            appointment_id, diagnosis, prescription, notes
        ):
            print("✅ Appointment marked as completed!")
        else:
            print("❌ Appointment not found!")
    
    def view_patient_appointments(self):
        """View appointments for a patient"""
        print("\n👥 VIEW PATIENT APPOINTMENTS")
        patient_id = int(input("Enter Patient ID: "))
        
        appointments = self.appointment_service.get_patient_appointments(patient_id)
        
        if not appointments:
            print("📭 No appointments found for this patient.")
            return
        
        print(f"\n📋 Appointments for Patient {patient_id}:")
        print("-" * 80)
        for appt in appointments:
            print(f"ID: {appt[0]} | Dr. {appt[12]} ({appt[13]}) | Date: {appt[3]} | Time: {appt[4]} | Status: {appt[6]}")
    
    def set_doctor_schedule(self):
        """Set doctor schedule"""
        print("\n🕐 SET DOCTOR SCHEDULE")
        doctor_id = int(input("Enter Doctor ID: "))
        day_of_week = input("Enter day of week (e.g., Monday): ")
        start_time = time.fromisoformat(input("Enter start time (HH:MM): "))
        end_time = time.fromisoformat(input("Enter end time (HH:MM): "))
        
        if self.schedule_service.set_doctor_schedule(doctor_id, day_of_week, start_time, end_time):
            print("✅ Doctor schedule updated successfully!")
        else:
            print("❌ Failed to update schedule!")
    
    def check_doctor_availability(self):
        """Check doctor availability"""
        print("\n📅 CHECK DOCTOR AVAILABILITY")
        doctor_id = int(input("Enter Doctor ID: "))
        date_str = input("Enter date to check (YYYY-MM-DD): ")
        check_date = date.fromisoformat(date_str)
        
        available_slots = self.schedule_service.get_doctor_availability(doctor_id, check_date)
        
        if available_slots:
            print(f"✅ Available slots for {check_date}:")
            for slot in available_slots:
                print(f"   ⏰ {slot}")
        else:
            print("❌ No available slots or doctor not working on this date.")
    
    def send_reminders(self):
        """Send appointment reminders"""
        print("\n🔔 SENDING APPOINTMENT REMINDERS")
        days = int(input("Enter days before appointment to send reminder (default: 1): ") or 1)
        
        count = self.notification_service.send_appointment_reminders(days)
        print(f"✅ Sent {count} appointment reminders!")
    
    def generate_daily_report(self):
        """Generate daily report"""
        print("\n📊 GENERATING DAILY REPORT")
        date_str = input("Enter date for report (YYYY-MM-DD) or press Enter for today: ")
        
        if date_str:
            report_date = date.fromisoformat(date_str)
        else:
            report_date = date.today()
        
        self.notification_service.generate_daily_report(report_date)
    
    def view_analytics(self):
        """View analytics and performance reports"""
        print("\n📈 VIEW ANALYTICS & PERFORMANCE")
        print("1. Doctor Utilization Report")
        print("2. Patient Flow Metrics")
        print("3. Peak Hours Analysis")
        print("4. Comprehensive Performance Report")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        if choice == '1':
            doctor_id = int(input("Enter Doctor ID: "))
            report = self.analytics_service.get_doctor_utilization(doctor_id, start_date, end_date)
            print(f"\n👨‍⚕️ UTILIZATION REPORT - Dr. {doctor_id}")
            for key, value in report.items():
                print(f"  {key}: {value}")
                
        elif choice == '2':
            report = self.analytics_service.get_patient_flow_metrics(start_date, end_date)
            print(f"\n👥 PATIENT FLOW METRICS")
            for key, value in report.items():
                if key not in ['specialty_distribution', 'daily_trends']:
                    print(f"  {key}: {value}")
                    
        elif choice == '3':
            report = self.analytics_service.get_peak_hours_analysis(start_date, end_date)
            print(f"\n🕐 PEAK HOURS ANALYSIS")
            for peak in report['peak_hours']:
                print(f"  Hour {peak['hour']}: {peak['appointment_count']} appointments")
                
        elif choice == '4':
            self.analytics_service.generate_performance_report()
        else:
            print("❌ Invalid choice!")
    
    def load_sample_data(self):
        """Load sample data"""
        print("\n📦 LOADING SAMPLE DATA...")
        load_sample_data()
        print("✅ Sample data loaded successfully!")

def main():
    """Main entry point"""
    try:
        app = HospitalSchedulerApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
