from datetime import datetime, date, timedelta
from src.utils.database_manager import DatabaseManager
import statistics
from collections import defaultdict

class AnalyticsService:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_doctor_utilization(self, doctor_id, start_date, end_date):
        """Calculate doctor utilization rate for a period"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        # Get total working hours in period
        cursor.execute('''
            SELECT day_of_week, start_time, end_time 
            FROM doctor_schedules 
            WHERE doctor_id = ?
        ''', (doctor_id,))
        
        schedules = cursor.fetchall()
        total_available_hours = self._calculate_available_hours(schedules, start_date, end_date)
        
        # Get booked appointment hours
        cursor.execute('''
            SELECT COUNT(*) as appointment_count,
                   SUM(duration_minutes) as total_minutes
            FROM appointments 
            WHERE doctor_id = ? 
            AND appointment_date BETWEEN ? AND ?
            AND status IN ('scheduled', 'completed')
        ''', (doctor_id, start_date, end_date))
        
        result = cursor.fetchone()
        conn.close()
        
        appointment_count = result[0] if result[0] else 0
        total_booked_minutes = result[1] if result[1] else 0
        total_booked_hours = total_booked_minutes / 60
        
        # Calculate utilization rate
        if total_available_hours > 0:
            utilization_rate = (total_booked_hours / total_available_hours) * 100
        else:
            utilization_rate = 0
        
        return {
            'doctor_id': doctor_id,
            'period': f"{start_date} to {end_date}",
            'total_available_hours': round(total_available_hours, 2),
            'total_booked_hours': round(total_booked_hours, 2),
            'appointment_count': appointment_count,
            'utilization_rate': round(utilization_rate, 2),
            'efficiency': 'High' if utilization_rate > 70 else 'Medium' if utilization_rate > 40 else 'Low'
        }
    
    def _calculate_available_hours(self, schedules, start_date, end_date):
        """Calculate total available hours based on schedule"""
        total_hours = 0
        current_date = start_date
        
        # Create day mapping
        day_mapping = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        
        schedule_dict = {}
        for day, start_time, end_time in schedules:
            schedule_dict[day_mapping[day]] = (start_time, end_time)
        
        # Calculate hours for each day in range
        while current_date <= end_date:
            day_of_week = current_date.weekday()
            if day_of_week in schedule_dict:
                start_time, end_time = schedule_dict[day_of_week]
                hours = (datetime.combine(date.today(), end_time) - 
                        datetime.combine(date.today(), start_time)).seconds / 3600
                total_hours += hours
            
            current_date += timedelta(days=1)
        
        return total_hours
    
    def get_patient_flow_metrics(self, start_date, end_date):
        """Analyze patient flow and appointment patterns"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        # Basic appointment statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_appointments,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
                SUM(CASE WHEN status = 'emergency' THEN 1 ELSE 0 END) as emergency,
                AVG(duration_minutes) as avg_duration
            FROM appointments 
            WHERE appointment_date BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        stats = cursor.fetchone()
        
        # Appointment distribution by specialty
        cursor.execute('''
            SELECT d.specialization, COUNT(*) as appointment_count
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_date BETWEEN ? AND ?
            GROUP BY d.specialization
            ORDER BY appointment_count DESC
        ''', (start_date, end_date))
        
        specialty_distribution = cursor.fetchall()
        
        # Daily appointment trends
        cursor.execute('''
            SELECT appointment_date, COUNT(*) as daily_count
            FROM appointments 
            WHERE appointment_date BETWEEN ? AND ?
            GROUP BY appointment_date
            ORDER BY appointment_date
        ''', (start_date, end_date))
        
        daily_trends = cursor.fetchall()
        
        conn.close()
        
        # Calculate additional metrics
        completion_rate = (stats[1] / stats[0] * 100) if stats[0] > 0 else 0
        cancellation_rate = (stats[3] / stats[0] * 100) if stats[0] > 0 else 0
        
        return {
            'period': f"{start_date} to {end_date}",
            'total_appointments': stats[0],
            'completed_appointments': stats[1],
            'scheduled_appointments': stats[2],
            'cancelled_appointments': stats[3],
            'emergency_appointments': stats[4],
            'average_duration_minutes': round(stats[5] if stats[5] else 0, 2),
            'completion_rate': round(completion_rate, 2),
            'cancellation_rate': round(cancellation_rate, 2),
            'specialty_distribution': specialty_distribution,
            'daily_trends': daily_trends
        }
    
    def get_peak_hours_analysis(self, start_date, end_date):
        """Analyze peak appointment hours"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                strftime('%H:00', time_slot) as hour_block,
                COUNT(*) as appointment_count
            FROM appointments 
            WHERE appointment_date BETWEEN ? AND ?
            AND status != 'cancelled'
            GROUP BY hour_block
            ORDER BY appointment_count DESC
        ''', (start_date, end_date))
        
        hourly_data = cursor.fetchall()
        conn.close()
        
        peak_hours = []
        for hour, count in hourly_data[:5]:  # Top 5 peak hours
            peak_hours.append({'hour': hour, 'appointment_count': count})
        
        return {
            'analysis_period': f"{start_date} to {end_date}",
            'peak_hours': peak_hours,
            'total_hours_analyzed': len(hourly_data)
        }
    
    def generate_performance_report(self, report_date=None):
        """Generate comprehensive performance report"""
        if not report_date:
            report_date = date.today()
        
        start_date = report_date - timedelta(days=30)  # Last 30 days
        
        doctor_utilization = []
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        # Get all doctors
        cursor.execute('SELECT doctor_id, name FROM doctors')
        doctors = cursor.fetchall()
        
        for doctor_id, doctor_name in doctors:
            utilization = self.get_doctor_utilization(doctor_id, start_date, report_date)
            doctor_utilization.append({
                'doctor_name': doctor_name,
                **utilization
            })
        
        patient_flow = self.get_patient_flow_metrics(start_date, report_date)
        peak_hours = self.get_peak_hours_analysis(start_date, report_date)
        
        conn.close()
        
        # Generate report
        self._print_performance_report(doctor_utilization, patient_flow, peak_hours, start_date, report_date)
        
        return {
            'doctor_utilization': doctor_utilization,
            'patient_flow': patient_flow,
            'peak_hours': peak_hours
        }
    
    def _print_performance_report(self, doctor_utilization, patient_flow, peak_hours, start_date, end_date):
        """Print formatted performance report"""
        print(f"\n📈 HOSPITAL PERFORMANCE REPORT")
        print(f"   Period: {start_date} to {end_date}")
        print("=" * 70)
        
        print(f"\n👨‍⚕️ DOCTOR UTILIZATION ANALYSIS")
        print("-" * 50)
        for doctor in doctor_utilization:
            print(f"Dr. {doctor['doctor_name']}:")
            print(f"  Utilization: {doctor['utilization_rate']}% ({doctor['efficiency']})")
            print(f"  Appointments: {doctor['appointment_count']}")
            print(f"  Booked Hours: {doctor['total_booked_hours']} / {doctor['total_available_hours']}")
            print()
        
        print(f"\n👥 PATIENT FLOW METRICS")
        print("-" * 30)
        print(f"Total Appointments: {patient_flow['total_appointments']}")
        print(f"Completion Rate: {patient_flow['completion_rate']}%")
        print(f"Cancellation Rate: {patient_flow['cancellation_rate']}%")
        print(f"Emergency Appointments: {patient_flow['emergency_appointments']}")
        print(f"Average Duration: {patient_flow['average_duration_minutes']} minutes")
        
        print(f"\n🕐 PEAK HOURS ANALYSIS")
        print("-" * 30)
        for peak in peak_hours['peak_hours']:
            print(f"Hour {peak['hour']}: {peak['appointment_count']} appointments")
        
        print(f"\n🎯 SPECIALTY DISTRIBUTION")
        print("-" * 30)
        for specialty, count in patient_flow['specialty_distribution'][:5]:  # Top 5
            print(f"{specialty}: {count} appointments")
        
        print("=" * 70)
