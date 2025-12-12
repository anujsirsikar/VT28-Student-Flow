# take care of the "people" here

from collections import deque
from datetime import date


class FlightStudent:
    # constructor

    syllabus1 = []
    syllabus2 = []

    def __init__(self, student_id, class_id, start_date):
        self.student_id = student_id
        self.class_id = class_id
        self.start_date = start_date
        self.current_date = start_date             # last date they were active/completed an event
        self.days_since_last_event = 0             # lastCompletedEventDate - currentDate. If it's >= 15, they need a warmup flight
        self.total_wait_time = 0                   # total days waiting due to resource shortage (weekdays only)
        self.last_completed_event_date = None
        # self.status = "active"   # active, completed, med down, leave, (pool?), waiting
        self.completion_date = None
        self.completed_blocks = [0,0,0,0,0,0,0]    # 0 = uncompleted, 1 = completed
        self.completed_dates = [None, None, None, None, None, None]
        self.current_block = 0                     # Block one starts at zero for indexing
        self.next_event_index = 0                  # index into flattened syllabus events
        self.aero_first = False
        self.night_hours = 0                       # need at least 5 hours of night flying
        # should we include a student failu/setre rate?
        self.syllabus_type = 1 # 1 = normal, 2 = aero and then instruments


    # toString function
    def __str__(self):
        return f"Student: {self.student_id}"
    
    def __repr__(self):
        return str(self)

    # returns the student's next event
    def next_event(self):
        return self.current_block, self.next_event_index
    
    
    def event_complete(self, day):
        if len(self.syllabus1[self.current_block])-1 <= self.next_event_index:
            self.completed_blocks[self.current_block] = 1
            self.completed_dates[self.current_block] = day
            self.current_block += 1
            self.next_event_index = 0
        else:
            self.next_event_index += 1
        if sum(self.completed_blocks) == 6:
            self.completion_date = date.today()
  

class Instructor:
    failure_rate = 0.30                                    # only 70% of the instructors are available to instruct (30% chance they can't)
    daily_hours = 12
    break_time = 0.5                                       # made this up bc it seems like it should be factored in.
    def __init__(self, name, section_lead, formation_q):
        self.name = name
        self.section_lead = section_lead                   # boolean value  (12)
        self.formation_q = formation_q                     # boolean value (I'm guessing this means formation qualified) (13)
        # Add this later:
        # self.onwing = (studentID)  <- add this to the constructor's parameters
        # should instructors have a status too?

    def __str__(self):
        return f"Instructor: {self.name}"
    
    def __repr__(self):
        return str(self)