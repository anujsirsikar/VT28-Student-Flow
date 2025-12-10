# take care of the "people" here

from collections import deque

class FlightStudent:
    # constructor
    def __init__(self, student_id, class_id, start_date, status, syllabus):
        self.student_id = student_id
        self.class_id = class_id
        self.medium_assigned = None
        self.start_date = start_date
        self.current_date = start_date         # last date they were active/completed an event
        self.days_in_process = 0
        self.days_since_last_event = None # lastCompletedEventDate - currentDate. If it's >= 15, they need a warmup flight
        self.total_wait_time = 0                   # total days waiting due to resource shortage (weekdays only)
        self.last_complete_event_date = None
        self.status = status   # active, completed, med down, leave, (pool?), waiting
        self.completion_date = None
        self.uncompleted_events = syllabus  # syllabus should be a deque of all the events in primary
        self.night_hours = 0  # need at least 5 hours of night flying
        # should we include a student failure rate?

    # toString function
    def __str__(self):
        return f"Student: {self.student_id}"

    # returns the student's next event
    def next_event(self):
        return self.uncompleted_events[0]
        

class Instructor:
    failure_rate = 0.30 # only 70% of the instructors are available to instruct (30% chance they can't)
    def __init__(self, name, section_lead, formation_q):
        self.name = name
        self.section_lead = section_lead  # boolean value  (12)
        self.formation_q = formation_q # boolean value (I'm guessing this means formation qualified) (13)
        # Add this later:
        # self.onwing = (studentID)  <- add this to the constructor's parameters
        # should instructors have a status too?