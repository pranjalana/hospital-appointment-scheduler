class Patient:
    def __init__(self, patient_id, mrn, name, email, phone, date_of_birth):
        self.patient_id = patient_id
        self.mrn = mrn  # Medical Record Number
        self.name = name
        self.email = email
        self.phone = phone
        self.date_of_birth = date_of_birth
        self.consultation_history = []
    
    def add_consultation(self, appointment_id, diagnosis, prescription, notes):
        """Add consultation record to patient history"""
        consultation = {
            'appointment_id': appointment_id,
            'diagnosis': diagnosis,
            'prescription': prescription,
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        }
        self.consultation_history.append(consultation)
    
    def get_consultation_history(self):
        """Get patient's complete consultation history"""
        return self.consultation_history
    
    def __str__(self):
        return f"Patient {self.patient_id}: {self.name} (MRN: {self.mrn})"
