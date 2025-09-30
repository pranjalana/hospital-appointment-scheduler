from src.utils.database_manager import DatabaseManager
from datetime import datetime, time, date, timedelta

def load_sample_data():
    """Load sample data for testing"""
    db_manager = DatabaseManager()
    
    # Add sample patients
    patients = [
        ("MRN001", "John Smith", "john.smith@email.com", "555-0101", date(1985, 5, 15)),
        ("MRN002", "Emma Johnson", "emma.johnson@email.com", "555-0102", date(1990, 8, 22)),
        ("MRN003", "Michael Brown", "michael.brown@email.com", "555-0103", date(1978, 12, 5)),
        ("MRN004", "Sarah Davis", "sarah.davis@email.com", "555-0104", date(1982, 3, 30)),
        ("MRN005", "Robert Wilson", "robert.wilson@email.com", "555-0105", date(1995, 7, 18)),
    ]
    
    patient_ids = []
    for patient in patients:
        patient_id = db_manager.add_patient(*patient)
        if patient_id:
            patient_ids.append(patient_id)
            print(f"Added patient: {patient[1]} (ID: {patient_id})")
    
    # Add sample doctors
    doctors = [
        ("Dr. Alice Cooper", "Cardiology", "alice.cooper@hospital.com", "555-0201"),
        ("Dr. Brian Miller", "Neurology", "brian.miller@hospital.com", "555-0202"),
        ("Dr. Carol White", "Pediatrics", "carol.white@hospital.com", "555-0203"),
        ("Dr. David Lee", "Orthopedics", "david.lee@hospital.com", "555-0204"),
    ]
    
    doctor_ids = []
    for doctor in doctors:
        doctor_id = db_manager.add_doctor(*doctor)
        doctor_ids.append(doctor_id)
        print(f"Added doctor: {doctor[0]} (ID: {doctor_id})")
    
    # Add sample appointments (tomorrow and day after)
    tomorrow = date.today() + timedelta(days=1)
    day_after = date.today() + timedelta(days=2)
    
    sample_appointments = [
        (patient_ids[0], doctor_ids[0], tomorrow, time(9, 0)),   # John Smith with Cardiologist
        (patient_ids[1], doctor_ids[1], tomorrow, time(10, 0)),  # Emma Johnson with Neurologist
        (patient_ids[2], doctor_ids[2], tomorrow, time(11, 0)),  # Michael Brown with Pediatrician
        (patient_ids[3], doctor_ids[0], day_after, time(14, 0)), # Sarah Davis with Cardiologist
        (patient_ids[4], doctor_ids[3], day_after, time(15, 0)), # Robert Wilson with Orthopedist
    ]
    
    for appointment in sample_appointments:
        appointment_id, message = db_manager.add_appointment(*appointment)
        if appointment_id:
            print(f"Added appointment: {message} (ID: {appointment_id})")
        else:
            print(f"Failed to add appointment: {message}")
    
    print("\nSample data loaded successfully!")
    print(f"Loaded {len(patient_ids)} patients and {len(doctor_ids)} doctors")

if __name__ == "__main__":
    load_sample_data()
