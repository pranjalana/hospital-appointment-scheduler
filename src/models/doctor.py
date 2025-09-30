from datetime import time, datetime

class Doctor:
    def __init__(self, doctor_id, name, specialization, email, phone):
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization
        self.email = email
        self.phone = phone
        self.working_hours = {}  # {day: (start_time, end_time)}
        self.break_times = {}    # {day: [(break_start, break_end)]}
        self.leave_dates = []    # List of unavailable dates
        self.emergency_slots = []  # Emergency appointment slots
    
    def set_working_hours(self, day, start_time, end_time):
        """Set working hours for a specific day"""
        self.working_hours[day] = (start_time, end_time)
    
    def add_break_time(self, day, break_start, break_end):
        """Add break time for a specific day"""
        if day not in self.break_times:
            self.break_times[day] = []
        self.break_times[day].append((break_start, break_end))
    
    def add_leave_date(self, leave_date):
        """Add a leave date when doctor is unavailable"""
        if leave_date not in self.leave_dates:
            self.leave_dates.append(leave_date)
    
    def is_available(self, date, time_slot):
        """Check if doctor is available at given date and time"""
        day = date.strftime('%A')  # Get day name
        
        # Check if on leave
        if date in self.leave_dates:
            return False
        
        # Check working hours
        if day not in self.working_hours:
            return False
        
        start_time, end_time = self.working_hours[day]
        
        # Check if within working hours
        if not (start_time <= time_slot <= end_time):
            return False
        
        # Check break times
        if day in self.break_times:
            for break_start, break_end in self.break_times[day]:
                if break_start <= time_slot <= break_end:
                    return False
        
        return True
    
    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"
