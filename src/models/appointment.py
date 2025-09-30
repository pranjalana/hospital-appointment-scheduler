from datetime import datetime, timedelta
from enum import Enum

class AppointmentStatus(Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EMERGENCY = "emergency"

class Appointment:
    def __init__(self, appointment_id, patient_id, doctor_id, appointment_date, 
                 time_slot, duration_minutes=30):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date
        self.time_slot = time_slot
        self.duration_minutes = duration_minutes
        self.status = AppointmentStatus.SCHEDULED
        self.diagnosis = None
        self.prescription = None
        self.notes = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def calculate_end_time(self):
        """Calculate appointment end time"""
        return (datetime.combine(self.appointment_date, self.time_slot) + 
                timedelta(minutes=self.duration_minutes)).time()
    
    def mark_completed(self, diagnosis="", prescription="", notes=""):
        """Mark appointment as completed with medical details"""
        self.status = AppointmentStatus.COMPLETED
        self.diagnosis = diagnosis
        self.prescription = prescription
        self.notes = notes
        self.updated_at = datetime.now()
    
    def mark_cancelled(self):
        """Mark appointment as cancelled"""
        self.status = AppointmentStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def is_conflicting(self, other_appointment):
        """Check if this appointment conflicts with another appointment"""
        if self.doctor_id != other_appointment.doctor_id:
            return False
        
        if self.appointment_date != other_appointment.appointment_date:
            return False
        
        self_end = self.calculate_end_time()
        other_end = other_appointment.calculate_end_time()
        
        # Check for time overlap
        return not (self_end <= other_appointment.time_slot or 
                   other_end <= self.time_slot)
    
    def __str__(self):
        return (f"Appointment {self.appointment_id}: "
                f"Patient {self.patient_id} with Dr. {self.doctor_id} "
                f"on {self.appointment_date} at {self.time_slot}")
