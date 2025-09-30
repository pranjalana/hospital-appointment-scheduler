import unittest
import sys
import os
from datetime import datetime, date, time, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.appointment_service import AppointmentService
from src.services.schedule_service import ScheduleService
from src.services.analytics_service import AnalyticsService
from src.utils.database_manager import DatabaseManager

class TestHospitalScenarios(unittest.TestCase):
    """End-to-end test scenarios for hospital scheduling"""
    
    def setUp(self):
        self.db_manager = DatabaseManager()
        self.appointment_service = AppointmentService()
        self.schedule_service = ScheduleService()
        self.analytics_service = AnalyticsService()
        
        # Create test data
        self.setup_test_data()
    
    def setup_test_data(self):
        """Setup comprehensive test data"""
        # Add multiple patients
        self.patient_ids = []
        patients = [
            ("MRN_SCENARIO_1", "Scenario Patient 1", "scenario1@test.com", "555-1001", date(1980, 5, 15)),
            ("MRN_SCENARIO_2", "Scenario Patient 2", "scenario2@test.com", "555-1002", date(1990, 8, 22)),
            ("MRN_SCENARIO_3", "Scenario Patient 3", "scenario3@test.com", "555-1003", date(1975, 12, 5)),
        ]
        
        for patient in patients:
            patient_id = self.db_manager.add_patient(*patient)
            if patient_id:
                self.patient_ids.append(patient_id)
        
        # Add multiple doctors with different specialties
        self.doctor_ids = []
        doctors = [
            ("Dr. Scenario Cardiologist", "Cardiology", "cardio@test.com", "555-2001"),
            ("Dr. Scenario Neurologist", "Neurology", "neuro@test.com", "555-2002"),
            ("Dr. Scenario Pediatrician", "Pediatrics", "pedia@test.com", "555-2003"),
        ]
        
        for doctor in doctors:
            doctor_id = self.db_manager.add_doctor(*doctor)
            self.doctor_ids.append(doctor_id)
    
    def tearDown(self):
        """Clean up test data"""
        conn = self.db_manager.db_config.get_connection()
        cursor = conn.cursor()
        
        for patient_id in self.patient_ids:
            cursor.execute('DELETE FROM appointments WHERE patient_id = ?', (patient_id,))
            cursor.execute('DELETE FROM patients WHERE patient_id = ?', (patient_id,))
        
        for doctor_id in self.doctor_ids:
            cursor.execute('DELETE FROM appointments WHERE doctor_id = ?', (doctor_id,))
            cursor.execute('DELETE FROM doctors WHERE doctor_id = ?', (doctor_id,))
        
        conn.commit()
        conn.close()
    
    def test_scenario_high_volume_scheduling(self):
        """Test high volume appointment scheduling"""
        test_date = date.today() + timedelta(days=2)
        
        # Schedule multiple appointments
        successful_bookings = 0
        time_slots = [time(9, 0), time(10, 0), time(11, 0), time(14, 0), time(15, 0)]
        
        for i, time_slot in enumerate(time_slots):
            patient_idx = i % len(self.patient_ids)
            doctor_idx = i % len(self.doctor_ids)
            
            appointment_id, message = self.appointment_service.book_appointment(
                self.patient_ids[patient_idx],
                self.doctor_ids[doctor_idx],
                test_date,
                time_slot
            )
            
            if appointment_id:
                successful_bookings += 1
        
        # Verify all appointments were booked successfully
        self.assertEqual(successful_bookings, len(time_slots), 
                        "All appointments should be booked without conflicts")
        
        # Verify analytics can handle the data
        utilization_report = self.analytics_service.get_doctor_utilization(
            self.doctor_ids[0], test_date - timedelta(days=1), test_date
        )
        self.assertIn('utilization_rate', utilization_report)
    
    def test_scenario_emergency_workflow(self):
        """Test complete emergency appointment workflow"""
        # Book emergency appointment
        appointment_id, message = self.appointment_service.book_emergency_appointment(
            self.patient_ids[0], self.doctor_ids[0], date.today()
        )
        
        # If emergency slot available, complete the workflow
        if appointment_id:
            # Complete the emergency appointment
            success = self.appointment_service.complete_appointment(
                appointment_id, 
                "Emergency diagnosis", 
                "Emergency prescription", 
                "Patient stabilized"
            )
            self.assertTrue(success, "Emergency appointment should be completable")
            
            # Verify it appears in analytics
            appointments = self.appointment_service.get_patient_appointments(self.patient_ids[0])
            emergency_appts = [appt for appt in appointments if appt[0] == appointment_id]
            self.assertEqual(len(emergency_appts), 1, "Emergency appointment should be in patient history")
    
    def test_scenario_schedule_management(self):
        """Test complete schedule management workflow"""
        doctor_id = self.doctor_ids[0]
        
        # Set doctor schedule
        self.schedule_service.set_doctor_schedule(
            doctor_id, "Monday", time(9, 0), time(17, 0)
        )
        
        # Add break time
        self.schedule_service.add_doctor_break(
            doctor_id, "Monday", time(12, 0), time(13, 0)
        )
        
        # Mark leave
        leave_date = date.today() + timedelta(days=5)
        self.schedule_service.mark_doctor_leave(doctor_id, leave_date, "Conference")
        
        # Check availability
        available_slots = self.schedule_service.get_doctor_availability(doctor_id, leave_date)
        self.assertEqual(len(available_slots), 0, "No slots should be available on leave day")
    
    def test_scenario_analytics_reporting(self):
        """Test analytics and reporting with real data"""
        # Generate some appointment data
        test_date = date.today() + timedelta(days=3)
        
        for i in range(3):
            appointment_id, message = self.appointment_service.book_appointment(
                self.patient_ids[i],
                self.doctor_ids[i],
                test_date,
                time(9 + i, 0)  # 9:00, 10:00, 11:00
            )
            
            if appointment_id and i == 0:  # Complete first appointment
                self.appointment_service.complete_appointment(
                    appointment_id, "Checkup", "Vitamins", "Routine checkup"
                )
        
        # Test analytics services
        start_date = date.today()
        end_date = test_date + timedelta(days=1)
        
        # Patient flow metrics
        flow_metrics = self.analytics_service.get_patient_flow_metrics(start_date, end_date)
        self.assertGreaterEqual(flow_metrics['total_appointments'], 3)
        
        # Doctor utilization
        for doctor_id in self.doctor_ids[:2]:  # Test first two doctors
            utilization = self.analytics_service.get_doctor_utilization(
                doctor_id, start_date, end_date
            )
            self.assertIn('utilization_rate', utilization)
        
        # Peak hours analysis
        peak_hours = self.analytics_service.get_peak_hours_analysis(start_date, end_date)
        self.assertIn('peak_hours', peak_hours)

if __name__ == '__main__':
    unittest.main()
