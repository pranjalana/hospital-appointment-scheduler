import unittest
import sys
import os
from datetime import datetime, date, time, timedelta

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.database_manager import DatabaseManager
from src.services.appointment_service import AppointmentService

class TestAppointmentConflicts(unittest.TestCase):
    def setUp(self):
        """Set up test database and services"""
        # Use test database
        self.db_manager = DatabaseManager()
        self.appointment_service = AppointmentService()
        
        # Add test doctor
        self.doctor_id = self.db_manager.add_doctor(
            "Dr. Test Specialist", "Cardiology", "test@hospital.com", "555-0000"
        )
        
        # Add test patient
        self.patient_id = self.db_manager.add_patient(
            "MRN_TEST", "Test Patient", "test@patient.com", "555-1111", date(1990, 1, 1)
        )
        
        # Test date (tomorrow)
        self.test_date = date.today() + timedelta(days=1)
    
    def tearDown(self):
        """Clean up test data"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        # Clean up test data
        cursor.execute('DELETE FROM appointments WHERE patient_id = ?', (self.patient_id,))
        cursor.execute('DELETE FROM patients WHERE patient_id = ?', (self.patient_id,))
        cursor.execute('DELETE FROM doctors WHERE doctor_id = ?', (self.doctor_id,))
        
        conn.commit()
        conn.close()
    
    def test_no_conflict_different_times(self):
        """Test that appointments at different times don't conflict"""
        # Book first appointment
        appointment_id1, message1 = self.db_manager.add_appointment(
            self.patient_id, self.doctor_id, self.test_date, time(9, 0)
        )
        self.assertIsNotNone(appointment_id1, "First appointment should be created")
        
        # Book second appointment at different time (should not conflict)
        appointment_id2, message2 = self.db_manager.add_appointment(
            self.patient_id, self.doctor_id, self.test_date, time(10, 0)
        )
        self.assertIsNotNone(appointment_id2, "Second appointment should be created without conflict")
    
    def test_conflict_same_time(self):
        """Test that appointments at same time conflict"""
        # Book first appointment
        appointment_id1, message1 = self.db_manager.add_appointment(
            self.patient_id, self.doctor_id, self.test_date, time(9, 0)
        )
        self.assertIsNotNone(appointment_id1, "First appointment should be created")
        
        # Try to book second appointment at same time (should conflict)
        appointment_id2, message2 = self.db_manager.add_appointment(
            self.patient_id, self.doctor_id, self.test_date, time(9, 0)
        )
        self.assertIsNone(appointment_id2, "Second appointment should conflict and not be created")
        self.assertIn("conflict", message2.lower(), "Error message should mention conflict")
    
    def test_conflict_overlapping_times(self):
        """Test that overlapping appointments conflict"""
        # Book first appointment at 9:00-9:30
        appointment_id1, message1 = self.db_manager.add_appointment(
            self.patient_id, self.doctor_id, self.test_date, time(9, 0)
        )
        self.assertIsNotNone(appointment_id1, "First appointment should be created")
        
        # Try to book overlapping appointment at 9:15-9:45 (should conflict)
        appointment_id2, message2 = self.db_manager.add_appointment(
            self.patient_id, self.doctor_id, self.test_date, time(9, 15)
        )
        self.assertIsNone(appointment_id2, "Overlapping appointment should conflict")
    
    def test_no_conflict_different_doctors(self):
        """Test that appointments with different doctors don't conflict"""
        # Add second test doctor
        doctor_id2 = self.db_manager.add_doctor(
            "Dr. Test Specialist 2", "Neurology", "test2@hospital.com", "555-0002"
        )
        
        try:
            # Book appointment with first doctor
            appointment_id1, message1 = self.db_manager.add_appointment(
                self.patient_id, self.doctor_id, self.test_date, time(9, 0)
            )
            self.assertIsNotNone(appointment_id1, "First appointment should be created")
            
            # Book appointment with second doctor at same time (should not conflict)
            appointment_id2, message2 = self.db_manager.add_appointment(
                self.patient_id, doctor_id2, self.test_date, time(9, 0)
            )
            self.assertIsNotNone(appointment_id2, "Appointment with different doctor should not conflict")
            
        finally:
            # Clean up second doctor
            conn = self.db_manager.db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM doctors WHERE doctor_id = ?', (doctor_id2,))
            conn.commit()
            conn.close()
    
    def test_no_conflict_different_dates(self):
        """Test that appointments on different dates don't conflict"""
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)
        
        # Book appointment for tomorrow
        appointment_id1, message1 = self.db_manager.add_appointment(
            self.patient_id, self.doctor_id, tomorrow, time(9, 0)
        )
        self.assertIsNotNone(appointment_id1, "First appointment should be created")
        
        # Book appointment for day after at same time (should not conflict)
        appointment_id2, message2 = self.db_manager.add_appointment(
            self.patient_id, self.doctor_id, day_after, time(9, 0)
        )
        self.assertIsNotNone(appointment_id2, "Appointment on different date should not conflict")

class TestAppointmentService(unittest.TestCase):
    def setUp(self):
        """Set up test data for service tests"""
        self.service = AppointmentService()
        self.db_manager = DatabaseManager()
        
        # Add test data
        self.patient_id = self.db_manager.add_patient(
            "MRN_SERVICE_TEST", "Service Test Patient", 
            "service_test@patient.com", "555-2222", date(1990, 1, 1)
        )
        self.doctor_id = self.db_manager.add_doctor(
            "Dr. Service Test", "Pediatrics", "service_test@hospital.com", "555-3333"
        )
        self.test_date = date.today() + timedelta(days=1)
    
    def tearDown(self):
        """Clean up test data"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM appointments WHERE patient_id = ?', (self.patient_id,))
        cursor.execute('DELETE FROM patients WHERE patient_id = ?', (self.patient_id,))
        cursor.execute('DELETE FROM doctors WHERE doctor_id = ?', (self.doctor_id,))
        conn.commit()
        conn.close()
    
    def test_emergency_appointment_booking(self):
        """Test emergency appointment booking"""
        appointment_id, message = self.service.book_emergency_appointment(
            self.patient_id, self.doctor_id, date.today()
        )
        
        # Emergency appointment should be created or return no slots
        self.assertTrue(
            appointment_id is not None or "no emergency slots" in message.lower(),
            "Emergency booking should either succeed or give appropriate message"
        )

if __name__ == '__main__':
    unittest.main()
