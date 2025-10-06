import sqlite3
import os
from datetime import datetime, time, date, timedelta
from config.database_config import DatabaseConfig

class DatabaseManager:
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.db_config.initialize_database()
    
    # Patient operations
    def add_patient(self, mrn, name, email, phone, date_of_birth):
        """Add a new patient to the database"""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO patients (mrn, name, email, phone, date_of_birth)
                VALUES (?, ?, ?, ?, ?)
            ''', (mrn, name, email, phone, date_of_birth))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Patient with MRN {mrn} already exists!")
            return None
        finally:
            conn.close()
    
    def get_patient(self, patient_id=None, mrn=None):
        """Get patient by ID or MRN"""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        if patient_id:
            cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
        elif mrn:
            cursor.execute('SELECT * FROM patients WHERE mrn = ?', (mrn,))
        else:
            return None
        
        patient = cursor.fetchone()
        conn.close()
        return patient
    
    # Doctor operations
    def add_doctor(self, name, specialization, email, phone):
        """Add a new doctor to the database"""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO doctors (name, specialization, email, phone)
            VALUES (?, ?, ?, ?)
        ''', (name, specialization, email, phone))
        
        conn.commit()
        doctor_id = cursor.lastrowid
        conn.close()
        return doctor_id
    
    def get_doctor(self, doctor_id):
        """Get doctor by ID"""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM doctors WHERE doctor_id = ?', (doctor_id,))
        doctor = cursor.fetchone()
        conn.close()
        return doctor
    
    def get_doctors_by_specialization(self, specialization):
        """Get all doctors by specialization"""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM doctors WHERE specialization = ?', (specialization,))
        doctors = cursor.fetchall()
        conn.close()
        return doctors
    
    # Appointment operations
    def add_appointment(self, patient_id, doctor_id, appointment_date, time_slot, duration_minutes=30):
        """Add a new appointment with conflict detection"""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        # Convert time_slot to string if it's a time object
        if hasattr(time_slot, 'isoformat'):
            time_slot_str = time_slot.isoformat(timespec='minutes')
        else:
            time_slot_str = str(time_slot)
        
        # Convert appointment_date to string if it's a date object
        if hasattr(appointment_date, 'isoformat'):
            appointment_date_str = appointment_date.isoformat()
        else:
            appointment_date_str = str(appointment_date)
        
        # Check for conflicts
        if self._has_appointment_conflict(doctor_id, appointment_date, time_slot, duration_minutes):
            conn.close()
            return None, "Time slot conflict detected"
        
        try:
            cursor.execute('''
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, time_slot, duration_minutes)
                VALUES (?, ?, ?, ?, ?)
            ''', (patient_id, doctor_id, appointment_date_str, time_slot_str, duration_minutes))
            
            conn.commit()
            appointment_id = cursor.lastrowid
            conn.close()
            return appointment_id, "Appointment scheduled successfully"
            
        except sqlite3.IntegrityError as e:
            conn.close()
            return None, f"Scheduling error: {str(e)}"
    
    def _has_appointment_conflict(self, doctor_id, appointment_date, time_slot, duration_minutes):
        """Check if appointment time conflicts with existing appointments"""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        # Convert to strings for comparison
        if hasattr(appointment_date, 'isoformat'):
            appointment_date_str = appointment_date.isoformat()
        else:
            appointment_date_str = str(appointment_date)
        
        cursor.execute('''
            SELECT time_slot, duration_minutes 
            FROM appointments 
            WHERE doctor_id = ? AND appointment_date = ? AND status != 'cancelled'
        ''', (doctor_id, appointment_date_str))
        
        existing_appointments = cursor.fetchall()
        conn.close()
        
        for existing_slot, existing_duration in existing_appointments:
            # Convert string time back to time object for comparison
            if isinstance(existing_slot, str):
                existing_time = time.fromisoformat(existing_slot)
            else:
                existing_time = existing_slot
                
            existing_start = datetime.combine(appointment_date, existing_time)
            existing_end = existing_start + timedelta(minutes=existing_duration)
            
            # Convert new time_slot if it's a string
            if isinstance(time_slot, str):
                new_time = time.fromisoformat(time_slot)
            else:
                new_time = time_slot
                
            new_start = datetime.combine(appointment_date, new_time)
            new_end = new_start + timedelta(minutes=duration_minutes)
            
            # Check for overlap
            if not (new_end <= existing_start or new_start >= existing_end):
                return True
        
        return False
    
    def get_doctor_appointments(self, doctor_id, appointment_date):
        """Get all appointments for a doctor on a specific date"""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        
        # Convert date to string for query
        if hasattr(appointment_date, 'isoformat'):
            appointment_date_str = appointment_date.isoformat()
        else:
            appointment_date_str = str(appointment_date)
        
        cursor.execute('''
            SELECT a.*, p.name as patient_name 
            FROM appointments a 
            JOIN patients p ON a.patient_id = p.patient_id 
            WHERE a.doctor_id = ? AND a.appointment_date = ? 
            ORDER BY a.time_slot
        ''', (doctor_id, appointment_date_str))
        
        appointments = cursor.fetchall()
        conn.close()
        return appointments