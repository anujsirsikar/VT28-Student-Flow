# take care of the "people" here

from collections import deque
from datetime import date


class FlightStudent:
    # constructor

    syllabus1 = []
    syllabus2 = []
    syllabus3 = []
    syllabus4 = []

    

    # can get rid of this late r
    s1 = ["Ground School", "Contacts", "Instrument Ground", "Instruments", "Aero", "Forms", "Capstone"]
    s2 = ["Ground School", "Contacts", "Aero", "Forms", "Instrument Ground", "Instruments", "Capstone"]     # second most common
    s3 = ["Ground School", "Contacts", "Instrument Ground", "Instruments", "Forms", "Aero", "Capstone"]
    s4 = ["Ground School", "Contacts", "Aero", "Instrument Ground", "Instruments", "Forms", "Capstone"]     # most common

    student_id = 0

    def __init__(self, student_id, class_id, start_date):
        self.student_id = student_id
        self.class_id = class_id
        self.start_date = start_date
        self.days_since_last_event = 0             # lastCompletedEventDate - currentDate. If it's >= 15, they need a warmup flight
        self.total_wait_time = 0                   # total days waiting due to resource shortage (weekdays only)
        self.last_completed_event_date = None
        # self.status = "active"   # active, completed, med down, leave, (pool?), waiting
        self.completion_date = None
        self.completed_blocks = [0,0,0,0,0,0,0]    # 0 = uncompleted, 1 = completed
        self.completed_dates = [None, None, None, None, None, None, None]  
        self.block_wait_times = {
            "Ground School": 0, 
            "Contacts": 0, 
            "Aero": 0, 
            "Instrument Ground": 0, 
            "Instruments": 0, 
            "Forms": 0, 
            "Capstone" : 0

        }
        self.unscheduled_per_resource = {
            "classroom": 0,
            "utd": 0,
            "oft": 0,
            "vtd":0,
            "mr":0,
            "aircraft": 0
        }
        self.current_block = 0                     # Block one starts at zero for indexing
        self.next_event_index = 0                  # index into flattened syllabus events
        self.Aero_first = True                     # do we need this????
        self.night_hours = 0                       # need at least 5 hours of night flying
        # should we include a student failu/setre rate?
        self.syllabus_type = 4 # 4 = normal, 2 = Aero and Forms and then instruments
        self.imported = True
        self.partner = None 
        self.schedule_failed = False 

    # toString function
    def __str__(self):
        return f"Student: {self.student_id}"
    
    def __repr__(self):
        return str(self)

    # returns the student's next event
    def next_event(self):
        return self.current_block, self.next_event_index

    # returns what block a student is in
    def get_block(self):
        if self.current_block > 6:
            return "complete"
        else:
            return [FlightStudent.s1, FlightStudent.s2, FlightStudent.s3, FlightStudent.s4][self.syllabus_type-1][self.current_block]


    def event_complete(self, day):
        syl = FlightStudent.syllabus1
        self.days_since_last_event = 0
        if self.syllabus_type == 2:
            syl = FlightStudent.syllabus2
        elif self.syllabus_type == 3:
            syl = FlightStudent.syllabus3
        elif self.syllabus_type == 4:
            syl = FlightStudent.syllabus4

        if self.current_block == 7:
            print("continueing to avoid error. need to fix this")
            print(self)
            print("syallbus type: ", self.syllabus_type)
            print("partner: ", self.partner)
            print("partner's syllabus type: ", self.partner.syllabus_type)
            print("current block: ", self.current_block, self.get_block())
            print("my next event", self.next_event())
            print("partner next event", self.get_partner().next_event())
            print("partner's current block: ", self.partner.current_block, self.partner.get_block())
            print("completed blocks: ", self.completed_blocks)
            print("partner's completed blocks", self.partner.completed_blocks)
            print("completion date: ", self.completion_date)
            print("partner completion date: ", self.partner.completion_date)
            print("all completion dates: ", self.completed_dates)
            print("partner's completion dates: ", self.partner.completed_dates)
            print(" ")
            # return

        if len(syl[self.current_block])-1 <= self.next_event_index:
            self.completed_blocks[self.current_block] = 1
            self.completed_dates[self.current_block] = day
            self.current_block += 1
            self.next_event_index = 0
        else:
            self.next_event_index += 1
        if sum(self.completed_blocks) == 7:
            self.completion_date = day
    
    
    def has_partner(self):
        if self.partner == None:
            return False
        else:
            return True
    
    def assign_partner(self, other_student):
        self.partner = other_student
        other_student.partner = self

    def get_partner(self):
        return self.partner
    
    def remove_partner(self):
        self.partner = None
  

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
        '''
        if self.section_lead and self.formation_q:
            return f"Instructor: {self.name}, qualled in both"
        elif self.section_lead:
            return f"Instructor: {self.name}, section lead"
        elif self.formation_q:
            return f"Instructor: {self.name}, formation q"
        else:
            return f"Instructor: {self.name}"
        '''
        return f"Instructor: {self.name}"
    
    def __repr__(self):
        return str(self)