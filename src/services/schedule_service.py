from datetime import datetime, time, date, timedelta
from src.utils.database_manager import DatabaseManager
import logging

class ScheduleService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
    
    def set_doctor_schedule(self, doctor_id, day_of_week, start_time, end_time):
        """Set doctor's weekly schedule"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        # Remove existing schedule for this day
        cursor.execute('''
            DELETE FROM doctor_schedules 
            WHERE doctor_id = ? AND day_of_week = ?
        ''', (doctor_id, day_of_week))
        
        # Add new schedule
        cursor.execute('''
            INSERT INTO doctor_schedules (doctor_id, day_of_week, start_time, end_time)
            VALUES (?, ?, ?, ?)
        ''', (doctor_id, day_of_week, start_time, end_time))
        
        conn.commit()
        conn.close()
        self.logger.info(f"Schedule set for doctor {doctor_id} on {day_of_week}")
        return True
    
    def add_doctor_break(self, doctor_id, day_of_week, break_start, break_end):
        """Add break time to doctor's schedule"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO doctor_breaks (doctor_id, day_of_week, break_start, break_end)
            VALUES (?, ?, ?, ?)
        ''', (doctor_id, day_of_week, break_start, break_end))
        
        conn.commit()
        conn.close()
        self.logger.info(f"Break added for doctor {doctor_id} on {day_of_week}")
        return True
    
    def mark_doctor_leave(self, doctor_id, leave_date, reason=""):
        """Mark doctor as on leave"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO doctor_leave (doctor_id, leave_date, reason)
                VALUES (?, ?, ?)
            ''', (doctor_id, leave_date, reason))
            
            conn.commit()
            self.logger.info(f"Leave marked for doctor {doctor_id} on {leave_date}")
            return True
            
        except sqlite3.IntegrityError:
            self.logger.warning(f"Leave already exists for doctor {doctor_id} on {leave_date}")
            return False
        finally:
            conn.close()
    
    def get_doctor_availability(self, doctor_id, target_date):
        """Get available time slots for a doctor on specific date"""
        day_of_week = target_date.strftime('%A')
        
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        # Get working hours
        cursor.execute('''
            SELECT start_time, end_time FROM doctor_schedules 
            WHERE doctor_id = ? AND day_of_week = ?
        ''', (doctor_id, day_of_week))
        
        schedule = cursor.fetchone()
        if not schedule:
            return []  # No schedule for this day
        
        start_time, end_time = schedule
        
        # Get breaks
        cursor.execute('''
            SELECT break_start, break_end FROM doctor_breaks 
            WHERE doctor_id = ? AND day_of_week = ?
        ''', (doctor_id, day_of_week))
        
        breaks = cursor.fetchall()
        
        # Get existing appointments
        cursor.execute('''
            SELECT time_slot, duration_minutes FROM appointments 
            WHERE doctor_id = ? AND appointment_date = ? AND status != 'cancelled'
            ORDER BY time_slot
        ''', (doctor_id, target_date))
        
        appointments = cursor.fetchall()
        conn.close()
        
        # Generate available slots
        return self._generate_available_slots(
            start_time, end_time, breaks, appointments, target_date
        )
    
    def _generate_available_slots(self, start_time, end_time, breaks, appointments, target_date):
        """Generate available time slots considering breaks and existing appointments"""
        slot_duration = 30  # minutes
        current_time = start_time
        available_slots = []
        
        while current_time < end_time:
            slot_end = (datetime.combine(target_date, current_time) + 
                       timedelta(minutes=slot_duration)).time()
            
            # Check if slot overlaps with any break
            break_conflict = False
            for break_start, break_end in breaks:
                if not (slot_end <= break_start or current_time >= break_end):
                    break_conflict = True
                    break
            
            # Check if slot overlaps with any appointment
            appointment_conflict = False
            for app_time, app_duration in appointments:
                app_end = (datetime.combine(target_date, app_time) + 
                          timedelta(minutes=app_duration)).time()
                if not (slot_end <= app_time or current_time >= app_end):
                    appointment_conflict = True
                    break
            
            # If no conflicts, add to available slots
            if not break_conflict and not appointment_conflict and slot_end <= end_time:
                available_slots.append(current_time)
            
            # Move to next slot
            current_time = (datetime.combine(target_date, current_time) + 
                          timedelta(minutes=slot_duration)).time()
        
        return available_slots
    
    def get_daily_schedule(self, doctor_id, schedule_date):
        """Get daily schedule for a doctor"""
        return self.db_manager.get_doctor_appointments(doctor_id, schedule_date)
