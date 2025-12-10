# take care of the "people" here

from collections import deque

class FlightStudent:
    # constructor
    def __init__(self, studentID, classID, startDate, status):
        self.studentID = studentID
        self.classID = classID
        self.mediumAssigned = None
        self.startDate = startDate
        self.currentDate = startDate         # last date they were active/completed an event
        self.next_event_index = 0            # index into flattened syllabus events
        self.daysInProcess = 0
        self.daily_events_done = 0
        self.daysSinceLastEvent = None # lastCompletedEventDate - currentDate. If it's >= 15, they need a warmup flight
        self.totalWaitTime = 0                   # total days waiting due to resource shortage (weekdays only)
        self.lastCompletedEventDate = None
        self.status = status   # active, completed, med down, leave, (pool?), waiting
        self.completionDate = None
        self.completed_blocks = [0,0,0,0,0,0,0]
        self.nightHours = 0  # need at least 5 hours of night flying
        # should we include a student failu/setre rate?

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