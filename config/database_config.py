import sqlite3
import os
from datetime import datetime

class DatabaseConfig:
    def __init__(self, db_path="database/hospital_scheduler.db"):
        self.db_path = db_path
        self.ensure_database_directory()
    
    def ensure_database_directory(self):
        """Create database directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def initialize_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Patients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                mrn TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                date_of_birth DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Doctors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Appointments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date DATE NOT NULL,
                time_slot TIME NOT NULL,
                duration_minutes INTEGER DEFAULT 30,
                status TEXT DEFAULT 'scheduled',
                diagnosis TEXT,
                prescription TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id),
                UNIQUE(doctor_id, appointment_date, time_slot)
            )
        ''')
        
        # Doctor schedules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_schedules (
                schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER NOT NULL,
                day_of_week TEXT NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
            )
        ''')
        
        # Doctor breaks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_breaks (
                break_id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER NOT NULL,
                day_of_week TEXT NOT NULL,
                break_start TIME NOT NULL,
                break_end TIME NOT NULL,
                FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
            )
        ''')
        
        # Doctor leave table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_leave (
                leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER NOT NULL,
                leave_date DATE NOT NULL,
                reason TEXT,
                FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id),
                UNIQUE(doctor_id, leave_date)
            )
        ''')
        
        # Consultation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consultation_history (
                consultation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                appointment_id INTEGER NOT NULL,
                diagnosis TEXT,
                prescription TEXT,
                notes TEXT,
                consultation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
                FOREIGN KEY (appointment_id) REFERENCES appointments (appointment_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")
