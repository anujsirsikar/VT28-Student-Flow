# @author Anuj Sirsikar and Timothy Kedrowski
# simulates a student going through the primary syllabus in flight school

# have it read from an excel spreadsheet? -> yes, to make a list of students

import datetime
from datetime import date, timedelta
from collections import deque
import time
import sys
from collections import defaultdict

class Mediums:
    def __init__(self, mediumType):
        # note: each type of resource/medium will have its own status
        self.mediumType = mediumType
        amount = 0
        if self.mediumType == 'Aircraft':
            amount = 18
        elif self.mediumType == 'Sim':
            amount = 32  # will change this number based on the specific sim (but for now there are 32 total sims)
        elif self.mediumType == 'Classroom':
            amount = 6
        self.amount = amount
        self.available = amount  # this could be useful
        # error handling (simple)
        if self.amount == 0:
            print("Unsupported Medium") 

# Note: these things can't be used everyday (usually just mon-fri)

# Subclass of Mediums
class Classroom(Mediums):
    # ***is a classroom capacity a factor? -> no, but later on add a class size variable
    def __init__(self, name, capacity=8):
        super().__init__("Classroom")
        self.name = name
        self.status = 0 # 0 = available and 1 = occupied
        self.capacity = capacity
        self.currentLoad = 0
        self.start = 6  # represents 0600 (6 am)
        self.stop = 18 # represents 1800 (6 pm)
        self.breakTime = 0 # hours

# Subclass of Mediums
class Sim(Mediums):
    def __init__(self, capacity=1):
        super().__init__("Sim")
        self.start = 5.5  # represents 0530
        self.capacity = capacity
        self.currentLoad = 0
        self.stop = 23 # represents 2300
        self.breakTime = 0.5 #hours
class Oft(Sim):                           # subclass of Sim
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.status = 0 # 0 = available and 1 = occupied
        self.amount = 6 # changing this here because 6 of the sims are OFTs
class Vtd(Sim):                           # subclass of Sim
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.status = 0 # 0 = available and 1 = occupied
        self.amount = 18 # changing this here because 18 of the sims are VTDs
class Utd(Sim):                           # subclass of Sim
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.status = 0 # 0 = available and 1 = occupied
        self.amount = 6 # changing this here because 6 of the sims are UTDs
class Mr(Sim):                           # subclass of Sim
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.status = 0 # 0 = available and 1 = occupied
        self.amount = 2 # changing this here because 2 of the sims are MRs

# Subclass of Mediums
class Aircraft(Mediums):
    def __init__(self, name, capacity=1):
        super().__init__("Aircraft")
        self.name = name
        self.status = 0 # 0 = available and 1 = occupied
        self.capacity = capacity
        self.currentLoad = 0
        self.start = 7  # represents 0700
        self.stop = 23 # represents 2300 
        self.breakTime = 1 # hours


class FlightStudent:
    # constructor
    def __init__(self, studentID, classID, startDate, status):
        self.studentID = studentID
        self.classID = classID
        self.mediumAssigned = None
        self.startDate = startDate
        self.currentDate = startDate         # last date they were active/completed an event
        self.available_date = startDate      # earliest calendar date student can attempt next event
        self.next_event_index = 0            # index into flattened syllabus events
        self.daysInProcess = 0
        self.dwellTime = 0                   # total days waiting due to resource shortage (weekdays only)
        self.lastCompletedEventDate = None
        self.status = status
        self.completionDate = None
        self.completed_blocks = set()
    
    # toString function
    def __str__(self):
        return f"Student: {self.studentID}"

# This code will address the flight schedule and different events and the resources they need
class TrainingBlock:
    def __init__(self, name, numEvents, events, totalDays, totalActivityTime):
        self.name = name # name of the block (i.e. aero, contacts, etc...)
        self.numEvents = numEvents
        self.events = events  # a list of the actual event objects
        self.totalDays = totalDays
        self.totalActivityTime = totalActivityTime   # in hours
        self.numStudents = 0 

class Event:
    def __init__(self, name, trainingDay, resources, activityTime):
        self.name = name # i.e. FAM2101, etc...
        self.trainingDay = trainingDay
        self.resources = resources  # a list (of no defined size) that contains all the resources that could be used for this event
        self.activityTime = activityTime # in hours
    
    # Will need a function that iterates over the resource list to check if there are resources available to fulfill the event.
    # Each event should also have a variable that indicates whether or not an event has available resources. 

    # Note: You can have more than one event in a day (especially for sims and flights) [but for first iteration, do one per day]

# SIMULATION LOGIC (with help from ChatGPT)
def run_simulation(students, syllabus):

    # Flatten all blocks into one ordered list of events
    all_events = []
    for block in syllabus:
        for evt in block.events:
            all_events.append(evt)

    # Precompute mapping: trainingDay → list of event indices
    training_day_map = {}
    for idx, evt in enumerate(all_events):
        td = evt.trainingDay
        if td not in training_day_map:
            training_day_map[td] = []
        training_day_map[td].append(idx)

    # Current simulation date is the earliest student start date
    current_date = min(s.startDate for s in students)

    # Group students by classID for synchronized Monday starts
    class_groups = defaultdict(list)
    for s in students:
        class_groups[s.classID].append(s)

    # Track which students have begun training
    students_not_started = set(students)
    students_started = set()
    class_started = set()    # tracks which classes have already started
    last_class_start_monday = None  # enforces one class per week


    # Helper: is weekend?
    def is_weekend(d):
        return d.weekday() >= 5  # 5 = Saturday, 6 = Sunday

    # Helper: check if a resource list has an available item
    def get_available_resource(resource_list):
        for r in resource_list:
            if r.currentLoad < r.capacity:   # resource still has slots
                return r
        return None

    # Simulation loop runs until all students complete all events
    last_training_day = max(training_day_map.keys())

    print("==== BEGIN SIMULATION ====\n")

    # Map event index → block
    event_to_block = {}
    for block in syllabus:
        for evt in block.events:
            event_to_block[id(evt)] = block

    while True:

        # if all students are finished, break
        if all(s.next_event_index >= len(all_events) for s in students):
            break

        # Skip weekends
        if is_weekend(current_date):
            print(f"{current_date} → Weekend (no training).")
            current_date += timedelta(days=1)
            continue
        

        # Allow class groups to start only on Mondays
        if current_date.weekday() == 0:  # Monday
            # Determine if a class already started this week
            if last_class_start_monday is None or (current_date - last_class_start_monday).days >= 7:

                # Find classIDs whose students are eligible to start
                eligible_classes = []
                for classID, group in class_groups.items():
                    # If this class hasn't started
                    if classID not in class_started:
                        # And at least one student has startDate <= today
                        if any(s.startDate <= current_date and s in students_not_started for s in group):
                            eligible_classes.append(classID)

                if eligible_classes:
                    # sort so that lowest classID gets priority
                    eligible_classes.sort()
                    # Choose ONE classID to start this week
                    classID_to_start = eligible_classes[0]   # deterministic, but you can randomize if you want

                    # Start all students in that class
                    for s in class_groups[classID_to_start]:
                        if s in students_not_started and s.startDate <= current_date:
                            s.currentDate = current_date
                            students_not_started.remove(s)
                            students_started.add(s)
                            print(f"Class {classID_to_start}: Student {s.studentID} STARTS syllabus on {current_date}")

                    # Record that this class started
                    class_started.add(classID_to_start)
                    last_class_start_monday = current_date


        print(f"\n=== {current_date} ===")

        # Process students FIFO
        for student in list(students):
            # Skip students whose class hasn't started yet
            if student not in students_started:
                continue

            # if student is already done
            if student.next_event_index >= len(all_events):
                continue

            # determine trainingDay of student's next event
            next_event = all_events[student.next_event_index]
            td = next_event.trainingDay

            # retrieve all events due on that trainingDay
            todays_event_indices = training_day_map.get(td, [])

            # Check if all required resources across all today's events are AVAILABLE
            all_available = True
            chosen_resources = []  # resource instance chosen for each event

            for evt_index in todays_event_indices:
                evt = all_events[evt_index]
                r = get_available_resource(evt.resources)

                if r is None:
                    all_available = False
                    break

                chosen_resources.append(r)

            # If ANY event not available → student dwells
            if not all_available:
                student.dwellTime += 1
                print(f"Student {student.studentID}: No resources → dwell +1 (total {student.dwellTime})")
                continue

            # Otherwise: assign resources and complete the events
            for r in chosen_resources:
                r.currentLoad += 1
            
            print(f"Student {student.studentID} COMPLETES training day {td}: "
                  f"{[all_events[i].name for i in todays_event_indices]}")
        
            # Advance student to the event after this training day
            student.next_event_index = max(todays_event_indices) + 1
            student.lastCompletedEventDate = current_date
            student.currentDate = current_date

            # Update block counts
            for evt_index in todays_event_indices:
                evt = all_events[evt_index]
                block = event_to_block[id(evt)]
                
                # If student just started this block
                if block.name not in student.completed_blocks:
                    block.numStudents += 1
                    student.completed_blocks.add(block.name)

            # After advancing student's next_event_index
            # Check if student has completed all events in the block(s) of today's events
            for evt_index in todays_event_indices:
                evt = all_events[evt_index]
                block = event_to_block[id(evt)]
                # If student has completed all events in the block, decrement active count
                block_event_ids = {id(e) for e in block.events}
                student_event_ids_done = {id(all_events[i]) for i in range(student.next_event_index)}
                if block_event_ids.issubset(student_event_ids_done):
                    if block.numStudents > 0:
                        block.numStudents -= 1


            # If finished all events
            if student.next_event_index >= len(all_events):
                student.completionDate = current_date
                print(f"Student {student.studentID} COMPLETED FULL SYLLABUS on {current_date}")

        # Reset all resource status at end of day
        for evt in all_events:
            for r in evt.resources:
                r.currentLoad = 0

        # After processing students and resetting resource loads
        '''
        sys.stdout.write("\033[H\033[J")  # Clear console (works in most terminals)
        
        # this way you just see numbers
        print(f"Simulation date: {current_date}")
        print(f"Systems Ground School: {syllabus[0].numStudents}")
        print(f"Contacts: {syllabus[1].numStudents}")
        print(f"Aero: {syllabus[2].numStudents}")
        print(f"Instruments Ground School: {syllabus[3].numStudents}")
        print(f"Instruments: {syllabus[4].numStudents}")
        print(f"Forms: {syllabus[5].numStudents}")
        print(f"Capstone: {syllabus[6].numStudents}")
        
        # this way you see blocks so it's more visual
        def print_block_status(blocks):
            # blocks: list of tuples (block_name, block_obj)
            max_bar_length = 20  # max width of the bar
            for name, block in blocks:
                # scale bar to max length if needed
                bar_length = min(block.numStudents, max_bar_length)
                bar = "█" * bar_length
                print(f"{name:25}: {bar} ({block.numStudents})")
        blocks = [
            ("Systems Ground School", syllabus[0]),
            ("Contacts", syllabus[1]),
            ("Aero", syllabus[2]),
            ("Instruments Ground School", syllabus[3]),
            ("Instruments", syllabus[4]),
            ("Forms", syllabus[5]),
            ("Capstone", syllabus[6])
        ]
        print(f"\n--- {current_date} Status ---")
        print_block_status(blocks)

        time.sleep(0.25)  # pause for half a second so you can watch updates
        '''
        # Next day
        current_date += timedelta(days=1)

    print("\n==== END OF SIMULATION ====\n")

    # FINAL REPORT
    for s in students:
        print(f"Student {s.studentID}:")
        print(f"  Completion Date : {s.completionDate}")
        print(f"  Dwell Time (days): {s.dwellTime}")
        print("")




def main():
    students = deque() # this will be a deque of students (for the future: be able to read in an excel sheet and then initialize student objects to populate this)
    # Let's make some students
    for i in range(1):
        students.append(FlightStudent(i, i//8, date.today(), "waiting")) # **IMPORTANT: change what i is being divided by to control class size (i.e. how many people are starting each week)

    # Resources
    classrooms = [Classroom(f"CL{i+1}") for i in range(6)]
    utd_sims = [Utd(f"UTD{i+1}") for i in range(6)]
    oft_sims = [Oft(f"OFT{i+1}") for i in range(6)]
    vtd_sims = [Vtd(f"VTD{i+1}") for i in range(18)]
    mr_sims = [Mr(f"MR{i+1}") for i in range(2)]
    aircrafts = [Aircraft(f"AC{i+1}") for i in range(18)]

    # keep track of each event's activity time
    activityTimeList = [7.3,4.5,1.9,3.5,2.9,2.5,6.5,5.5,5.5,2.5,3.5,7,7,1.3,1.3,1.3,1.3,1,1.3,1.3,1.3,1.3,
                        1.3,1.3,1.3,1.3,1.3,1.3,1.3,1.3,1.3,3,1.5,1.5,1.5,1.5,1.3,1.3,1.3,1.3,1.3,1.6,1.6,
                        1,1.6,1.6,1.7,1.7,1.7,1.7,1.7,1.5,1.3,1.7,1.7,1.7,4,4,1,4,5,4.5,2,6.5,2,4,1,1.3,1.3,
                        1.3,1.3,1.3,1.3,1.3,1.3,1.3,1.3,1.3,1.3,1.3,1.6,1.6,1.6,2,1.3,1.3,1.3,1.3,1.3,1.3,
                        1.3,1.6,1.6,1.6,1.6,1.7,1.7,1.7,1.7,1.7,1.6,1.6,3.5,1,2,1.3,1.3,1.6,1.6,1.6,1.6,1.6,
                        2,1.3,1.3,1.3,1.3,1.7,1.7,1.7]


    # Initialize a list of event objects for each block
    sysGrndSchoolEvents = []
    sysGrndSchoolEvents.append(Event("G0101", 1, classrooms, activityTimeList[0]/2))
    sysGrndSchoolEvents.append(Event("G6001", 1, classrooms, activityTimeList[0]/2))
    sysGrndSchoolEvents.append(Event("G0107", 2, classrooms, activityTimeList[1]/3))
    sysGrndSchoolEvents.append(Event("SY0101", 2, classrooms, activityTimeList[1]/3))
    sysGrndSchoolEvents.append(Event("SY0102", 2, classrooms, activityTimeList[1]/3))
    sysGrndSchoolEvents.append(Event("SY0106", 3, classrooms, activityTimeList[2]))
    sysGrndSchoolEvents.append(Event("SY0112", 4, classrooms, activityTimeList[3]))
    sysGrndSchoolEvents.append(Event("SY0190", 5, classrooms, activityTimeList[4]/2))
    sysGrndSchoolEvents.append(Event("SY0203", 5, classrooms, activityTimeList[4]/2))
    sysGrndSchoolEvents.append(Event("SY0206", 6, classrooms, activityTimeList[5]/2))
    sysGrndSchoolEvents.append(Event("G0106", 6, classrooms, activityTimeList[5]/2))
    sysGrndSchoolEvents.append(Event("SY0290", 7, classrooms, activityTimeList[6]/3))
    sysGrndSchoolEvents.append(Event("G0104", 7, classrooms, activityTimeList[6]/3))
    sysGrndSchoolEvents.append(Event("G0105", 7, classrooms, activityTimeList[6]/3))
    sysGrndSchoolEvents.append(Event("SY0301", 8, classrooms, activityTimeList[7]/3))
    sysGrndSchoolEvents.append(Event("PR0101", 8, classrooms, activityTimeList[7]/3))
    sysGrndSchoolEvents.append(Event("PR0102B", 8, classrooms, activityTimeList[7]/3))
    sysGrndSchoolEvents.append(Event("PR0103", 9, classrooms, activityTimeList[8]/3))
    sysGrndSchoolEvents.append(Event("PR0104", 9, classrooms, activityTimeList[8]/3))
    sysGrndSchoolEvents.append(Event("PR0105", 9, classrooms, activityTimeList[8]/3))
    sysGrndSchoolEvents.append(Event("FAM1106", 10, classrooms, activityTimeList[9]))
    sysGrndSchoolEvents.append(Event("FAM1190", 11, classrooms, activityTimeList[10]/2))
    sysGrndSchoolEvents.append(Event("FAM1203", 11, classrooms, activityTimeList[10]/2))
    sysGrndSchoolEvents.append(Event("FAM1290", 12, classrooms, activityTimeList[11]/3))
    sysGrndSchoolEvents.append(Event("G0201", 12, classrooms, activityTimeList[11]/3))
    sysGrndSchoolEvents.append(Event("G0103", 12, classrooms, activityTimeList[11]/3))
    sysGrndSchoolEvents.append(Event("G0290", 13, classrooms, activityTimeList[12]/2))
    sysGrndSchoolEvents.append(Event("G0102", 13, classrooms, activityTimeList[12]/2))
    
    contactsEvents = []
    contactsEvents.append(Event("FAM2101", 14, utd_sims, activityTimeList[13]))
    contactsEvents.append(Event("FAM2102", 15, utd_sims, activityTimeList[14]))
    contactsEvents.append(Event("FAM2201", 16, utd_sims, activityTimeList[15]))
    contactsEvents.append(Event("FAM2202", 17, utd_sims, activityTimeList[16]))
    contactsEvents.append(Event("IN1104", 18, classrooms, activityTimeList[17]))
    contactsEvents.append(Event("I2101", 19, utd_sims, activityTimeList[18]))
    contactsEvents.append(Event("I2102", 20, utd_sims, activityTimeList[19]))
    contactsEvents.append(Event("I2103", 21, utd_sims, activityTimeList[20]))
    contactsEvents.append(Event("FAM3101", 22, oft_sims, activityTimeList[21]))
    contactsEvents.append(Event("FAM3102", 23, oft_sims, activityTimeList[22]))
    contactsEvents.append(Event("FAM3103", 24, oft_sims, activityTimeList[23]))
    contactsEvents.append(Event("FAM6101", 25, vtd_sims, activityTimeList[24]))
    contactsEvents.append(Event("FAM6102", 26, vtd_sims, activityTimeList[25]))
    contactsEvents.append(Event("FAM6201", 27, vtd_sims, activityTimeList[26]))
    contactsEvents.append(Event("FAM6202", 28, vtd_sims, activityTimeList[27]))
    contactsEvents.append(Event("FAM6203", 29, vtd_sims, activityTimeList[28]))
    contactsEvents.append(Event("FAM6301", 30, vtd_sims, activityTimeList[29]))
    contactsEvents.append(Event("FAM6302", 31, vtd_sims, activityTimeList[30]))
    contactsEvents.append(Event("FAM1301", 32, aircrafts, activityTimeList[31])) # onwing
    contactsEvents.append(Event("FAM4101", 33, aircrafts, activityTimeList[32])) # onwing
    contactsEvents.append(Event("FAM4102", 34, aircrafts, activityTimeList[33])) # onwing
    contactsEvents.append(Event("FAM4103", 35, aircrafts, activityTimeList[34])) # onwing
    contactsEvents.append(Event("FAM4104", 36, aircrafts, activityTimeList[35])) # onwing
    contactsEvents.append(Event("FAM3201", 37, oft_sims, activityTimeList[36]))
    contactsEvents.append(Event("FAM3202", 38, oft_sims, activityTimeList[37]))
    contactsEvents.append(Event("FAM3301", 39, oft_sims, activityTimeList[38]))
    contactsEvents.append(Event("FAM6401", 40, vtd_sims, activityTimeList[39]))
    contactsEvents.append(Event("FAM6402", 41, vtd_sims, activityTimeList[40]))
    contactsEvents.append(Event("FAM4201", 42, aircrafts, activityTimeList[41]))
    contactsEvents.append(Event("FAM4202", 43, aircrafts, activityTimeList[42]))
    contactsEvents.append(Event("FAM1206", 44, classrooms, activityTimeList[43]))
    contactsEvents.append(Event("FAM4203", 45, aircrafts, activityTimeList[44]))
    contactsEvents.append(Event("FAM4204", 46, aircrafts, activityTimeList[45]))
    contactsEvents.append(Event("FAM4301", 47, aircrafts, activityTimeList[46]))
    contactsEvents.append(Event("FAM4302", 48, aircrafts, activityTimeList[47]))
    contactsEvents.append(Event("FAM4303", 49, aircrafts, activityTimeList[48])) # onwing
    contactsEvents.append(Event("FAM4304", 50, aircrafts, activityTimeList[49])) # onwing
    contactsEvents.append(Event("FAM4490", 51, aircrafts, activityTimeList[50]))
    contactsEvents.append(Event("FAM4501", 52, aircrafts, activityTimeList[51]))
    
    aeroEvents = []
    aeroEvents.append(Event("FAM3401", 53, oft_sims, activityTimeList[52]))
    aeroEvents.append(Event("FAM4701", 54, aircrafts, activityTimeList[53]))
    aeroEvents.append(Event("FAM4702", 55, aircrafts, activityTimeList[54]))
    aeroEvents.append(Event("FAM4703", 56, aircrafts, activityTimeList[55]))

    instrGrndSchoolEvents = []
    instrGrndSchoolEvents.append(Event("IN1202", 57, classrooms, activityTimeList[56]/2))
    instrGrndSchoolEvents.append(Event("IN1203", 57, classrooms, activityTimeList[56]/2))
    instrGrndSchoolEvents.append(Event("IN1205", 58, classrooms, activityTimeList[57]/2))
    instrGrndSchoolEvents.append(Event("IN1206", 58, classrooms, activityTimeList[57]/2))
    instrGrndSchoolEvents.append(Event("IN1290", 59, classrooms, activityTimeList[58]))
    instrGrndSchoolEvents.append(Event("IN1305", 60, classrooms, activityTimeList[59]/2))
    instrGrndSchoolEvents.append(Event("IN1306", 60, classrooms, activityTimeList[59]/2))
    instrGrndSchoolEvents.append(Event("IN1307", 61, classrooms, activityTimeList[60]/2))
    instrGrndSchoolEvents.append(Event("IN1308", 61, classrooms, activityTimeList[60]/2))
    instrGrndSchoolEvents.append(Event("IN1390", 62, classrooms, activityTimeList[61]/2))
    instrGrndSchoolEvents.append(Event("IN1403", 62, classrooms, activityTimeList[61]/2))
    instrGrndSchoolEvents.append(Event("IN1406", 63, classrooms, activityTimeList[62]))
    instrGrndSchoolEvents.append(Event("IN1411", 64, classrooms, activityTimeList[63]/3))
    instrGrndSchoolEvents.append(Event("IN1412", 64, classrooms, activityTimeList[63]/3))
    instrGrndSchoolEvents.append(Event("IN1413A", 64, classrooms, activityTimeList[63]/3))
    instrGrndSchoolEvents.append(Event("IN1490", 65, classrooms, activityTimeList[64]/2))  
    instrGrndSchoolEvents.append(Event("IN1501", 65, classrooms, activityTimeList[64]/2))
    instrGrndSchoolEvents.append(Event("NA1105", 66, classrooms, activityTimeList[65]/2))
    instrGrndSchoolEvents.append(Event("NA1106", 66, classrooms, activityTimeList[65]/2))
    instrGrndSchoolEvents.append(Event("NA1190", 67, classrooms, activityTimeList[66]))

    instrumentsEvents = []
    instrumentsEvents.append(Event("I2201", 68, utd_sims, activityTimeList[67]))
    instrumentsEvents.append(Event("I2202", 69, utd_sims, activityTimeList[68]))
    instrumentsEvents.append(Event("I2203", 70, utd_sims, activityTimeList[69]))
    instrumentsEvents.append(Event("N3101", 71, oft_sims, activityTimeList[70]))
    instrumentsEvents.append(Event("N6101", 72, vtd_sims, activityTimeList[71]))
    instrumentsEvents.append(Event("I6101", 73, vtd_sims, activityTimeList[72]))
    instrumentsEvents.append(Event("I6102", 74, vtd_sims, activityTimeList[73]))
    instrumentsEvents.append(Event("I3101", 75, utd_sims, activityTimeList[74]))
    instrumentsEvents.append(Event("I3102", 76, utd_sims, activityTimeList[75]))
    instrumentsEvents.append(Event("I3103", 77, utd_sims, activityTimeList[76]))
    instrumentsEvents.append(Event("I3104", 78, oft_sims, activityTimeList[77]))
    instrumentsEvents.append(Event("I6201", 79, vtd_sims, activityTimeList[78]))
    instrumentsEvents.append(Event("I6202", 80, vtd_sims, activityTimeList[79]))
    instrumentsEvents.append(Event("I4101", 81, aircrafts, activityTimeList[80]))
    instrumentsEvents.append(Event("I4102", 82, aircrafts, activityTimeList[81]))
    instrumentsEvents.append(Event("I4103", 83, aircrafts, activityTimeList[82]))
    instrumentsEvents.append(Event("SY0302", 84, classrooms, activityTimeList[83]))
    instrumentsEvents.append(Event("I3201", 85, utd_sims, activityTimeList[84]))
    instrumentsEvents.append(Event("I3202", 86, utd_sims, activityTimeList[85]))
    instrumentsEvents.append(Event("I3203", 87, oft_sims, activityTimeList[86]))
    instrumentsEvents.append(Event("I3204", 88, oft_sims, activityTimeList[87]))
    instrumentsEvents.append(Event("I3205", 89, oft_sims, activityTimeList[88]))
    instrumentsEvents.append(Event("I3206", 90, oft_sims, activityTimeList[89]))
    instrumentsEvents.append(Event("I6301", 91, vtd_sims, activityTimeList[90]))
    instrumentsEvents.append(Event("I4201", 92, aircrafts, activityTimeList[91]))
    instrumentsEvents.append(Event("I4202", 93, aircrafts, activityTimeList[92]))
    instrumentsEvents.append(Event("I4203", 94, aircrafts, activityTimeList[93]))
    instrumentsEvents.append(Event("I4204", 95, aircrafts, activityTimeList[94]))
    instrumentsEvents.append(Event("I4301", 96, aircrafts, activityTimeList[95]))
    instrumentsEvents.append(Event("I4302", 97, aircrafts, activityTimeList[96]))
    instrumentsEvents.append(Event("I4303", 98, aircrafts, activityTimeList[97]))
    instrumentsEvents.append(Event("I4304", 99, aircrafts, activityTimeList[98]))
    instrumentsEvents.append(Event("I4490", 100, aircrafts, activityTimeList[99]))
    instrumentsEvents.append(Event("N4101", 101, aircrafts, activityTimeList[100]))
    instrumentsEvents.append(Event("FAM4601", 102, aircrafts, activityTimeList[101]))

    formsEvents = []
    formsEvents.append(Event("F1102", 103, classrooms, activityTimeList[102]))
    formsEvents.append(Event("FF190", 104, classrooms, activityTimeList[103]))
    formsEvents.append(Event("FF1201", 105, classrooms, activityTimeList[104]))
    formsEvents.append(Event("F3101", 106, oft_sims, activityTimeList[105]))
    formsEvents.append(Event("F2101", 107, mr_sims, activityTimeList[106]))
    formsEvents.append(Event("F4101", 108, aircrafts, activityTimeList[107]))
    formsEvents.append(Event("F4102", 109, aircrafts, activityTimeList[108]))
    formsEvents.append(Event("F4103", 110, aircrafts, activityTimeList[109]))
    formsEvents.append(Event("F4104", 111, aircrafts, activityTimeList[110]))
    formsEvents.append(Event("F4290", 112, aircrafts, activityTimeList[111]))

    capstoneEvents = []
    capstoneEvents.append(Event("CS1101", 113, classrooms, activityTimeList[112]))
    capstoneEvents.append(Event("CS2101", 114, mr_sims, activityTimeList[113]))
    capstoneEvents.append(Event("CS2102", 115, mr_sims, activityTimeList[114]))
    capstoneEvents.append(Event("CS3101", 116, oft_sims, activityTimeList[115]))
    capstoneEvents.append(Event("CS3102", 117, oft_sims, activityTimeList[116]))
    capstoneEvents.append(Event("CS4101", 118, aircrafts, activityTimeList[117]))
    capstoneEvents.append(Event("CS4102", 119, aircrafts, activityTimeList[118]))
    capstoneEvents.append(Event("CS4290", 120, aircrafts, activityTimeList[119]))

    # Initialize the training blocks
    block1 = TrainingBlock("Systems Ground School", 28, sysGrndSchoolEvents, 13, 60.1)  
    block2 = TrainingBlock("Contacts", 39, contactsEvents, 39, 56)
    block3 = TrainingBlock("Aero", 4, aeroEvents, 4, 6.4)
    block4 = TrainingBlock("Instruments Ground School", 20, instrGrndSchoolEvents, 11, 38)
    block5 = TrainingBlock("Instruments", 35, instrumentsEvents, 35, 50.9)
    block6 = TrainingBlock("Forms", 10, formsEvents, 10, 17.1)
    block7 = TrainingBlock("Capstone", 8, capstoneEvents, 8, 12.3)

    # Combine into syllabus
    syllabus = [block1, block2, block3, block4, block5, block6, block7]
   

    # Run the simulation
    run_simulation(students, syllabus)



if __name__ == "__main__":
    main()
