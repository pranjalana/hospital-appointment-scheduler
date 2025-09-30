from datetime import datetime, time, date, timedelta
from src.utils.database_manager import DatabaseManager
from src.models.appointment import AppointmentStatus
import logging

class AppointmentService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
    
    def book_appointment(self, patient_id, doctor_id, appointment_date, preferred_time):
        """Book an appointment with automatic time slot finding"""
        # Check doctor availability
        if not self._is_doctor_available(doctor_id, appointment_date):
            return None, "Doctor is not available on this date"
        
        # Find available time slot
        available_slot = self._find_available_slot(doctor_id, appointment_date, preferred_time)
        if not available_slot:
            return None, "No available slots found for preferred time"
        
        # Book the appointment
        appointment_id, message = self.db_manager.add_appointment(
            patient_id, doctor_id, appointment_date, available_slot
        )
        
        if appointment_id:
            self.logger.info(f"Appointment booked: {appointment_id} for patient {patient_id}")
            # Simulate notification
            self._send_appointment_confirmation(patient_id, doctor_id, appointment_date, available_slot)
        
        return appointment_id, message
    
    def _is_doctor_available(self, doctor_id, appointment_date):
        """Check if doctor is available on given date"""
        # For now, we'll assume doctors are available on weekdays
        # In a real system, this would check doctor schedules and leave
        return appointment_date.weekday() < 5  # Monday-Friday
    
    def _find_available_slot(self, doctor_id, appointment_date, preferred_time, max_slots=10):
        """Find available time slot starting from preferred time"""
        current_time = preferred_time
        slots_checked = 0
        
        while slots_checked < max_slots:
            # Check if this slot is available
            if not self.db_manager._has_appointment_conflict(doctor_id, appointment_date, current_time, 30):
                return current_time
            
            # Move to next slot (30-minute intervals)
            current_time = (datetime.combine(date.today(), current_time) + timedelta(minutes=30)).time()
            slots_checked += 1
        
        return None
    
    def cancel_appointment(self, appointment_id):
        """Cancel an appointment"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE appointments 
            SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP 
            WHERE appointment_id = ?
        ''', (appointment_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        if success:
            self.logger.info(f"Appointment cancelled: {appointment_id}")
        
        return success
    
    def complete_appointment(self, appointment_id, diagnosis, prescription, notes):
        """Mark appointment as completed with medical details"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE appointments 
            SET status = 'completed', diagnosis = ?, prescription = ?, notes = ?, 
                updated_at = CURRENT_TIMESTAMP 
            WHERE appointment_id = ?
        ''', (diagnosis, prescription, notes, appointment_id))
        
        # Also add to consultation history
        cursor.execute('''
            INSERT INTO consultation_history (patient_id, appointment_id, diagnosis, prescription, notes)
            SELECT patient_id, appointment_id, diagnosis, prescription, notes
            FROM appointments 
            WHERE appointment_id = ?
        ''', (appointment_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        if success:
            self.logger.info(f"Appointment completed: {appointment_id}")
        
        return success
    
    def get_patient_appointments(self, patient_id, status=None):
        """Get all appointments for a patient"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT a.*, d.name as doctor_name, d.specialization 
                FROM appointments a 
                JOIN doctors d ON a.doctor_id = d.doctor_id 
                WHERE a.patient_id = ? AND a.status = ?
                ORDER BY a.appointment_date DESC, a.time_slot DESC
            ''', (patient_id, status))
        else:
            cursor.execute('''
                SELECT a.*, d.name as doctor_name, d.specialization 
                FROM appointments a 
                JOIN doctors d ON a.doctor_id = d.doctor_id 
                WHERE a.patient_id = ? 
                ORDER BY a.appointment_date DESC, a.time_slot DESC
            ''', (patient_id,))
        
        appointments = cursor.fetchall()
        conn.close()
        return appointments
    
    def _send_appointment_confirmation(self, patient_id, doctor_id, appointment_date, time_slot):
        """Simulate sending appointment confirmation (console output for demo)"""
        patient = self.db_manager.get_patient(patient_id=patient_id)
        doctor = self.db_manager.get_doctor(doctor_id)
        
        print(f"\n=== APPOINTMENT CONFIRMATION ===")
        print(f"Patient: {patient[2]}")  # name is at index 2
        print(f"Doctor: {doctor[1]}")    # name is at index 1
        print(f"Date: {appointment_date}")
        print(f"Time: {time_slot}")
        print(f"MRN: {patient[1]}")
        print(f"===============================\n")
    
    def book_emergency_appointment(self, patient_id, doctor_id, appointment_date):
        """Book emergency appointment - finds next available slot regardless of schedule"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        # Find next available slot today
        current_time = datetime.now().time()
        today = date.today()
        
        # Try to find slot within next 2 hours
        emergency_slot = self._find_emergency_slot(doctor_id, today, current_time)
        
        if emergency_slot:
            appointment_id, message = self.db_manager.add_appointment(
                patient_id, doctor_id, today, emergency_slot
            )
            
            if appointment_id:
                cursor.execute('''
                    UPDATE appointments SET status = 'emergency' 
                    WHERE appointment_id = ?
                ''', (appointment_id,))
                conn.commit()
                
                self.logger.info(f"Emergency appointment booked: {appointment_id}")
                print(f"🚨 EMERGENCY APPOINTMENT: {today} at {emergency_slot}")
            
            conn.close()
            return appointment_id, message
        
        conn.close()
        return None, "No emergency slots available today"
    
    def _find_emergency_slot(self, doctor_id, appointment_date, start_time, max_hours=4):
        """Find emergency slot within specified hours"""
        current_dt = datetime.combine(appointment_date, start_time)
        end_dt = current_dt + timedelta(hours=max_hours)
        
        while current_dt <= end_dt:
            if not self.db_manager._has_appointment_conflict(
                doctor_id, appointment_date, current_dt.time(), 30
            ):
                return current_dt.time()
            
            current_dt += timedelta(minutes=30)
        
        return None
