# take care of the "people" here


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
        self.daysSinceLastEvent = None # lastCompletedEventDate - currentDate. If it's >= 15, they need a warmup flight
        self.totalWaitTime = 0                   # total days waiting due to resource shortage (weekdays only)
        self.lastCompletedEventDate = None
        self.status = status   # active, completed, med down, leave, (pool?), waiting
        self.completionDate = None
        self.completed_blocks = set()
        self.nightHours = 0  # need at least 5 hours of night flying
        # should we include a student failure rate?

    # toString function
    def __str__(self):
        return f"Student: {self.studentID}"

class Instructor:
    def __init__(self, name, sectionLead, formationQ):
        self.name = name
        self.sectionLead = sectionLead  # boolean value  (12)
        self.formationQ = formationQ # boolean value (I'm guessing this means formation qualified) (13)
        self.failureRate = 0.30  # only 70% of the instructors are available to instruct (30% chance they can't)
        # Add this later:
        # self.onwing = (studentID)  <- add this to the constructor's parameters
        # should instructors have a status too?