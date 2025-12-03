# @author Anuj Sirsikar and Timothy Kedrowski and Lauren Leckelt
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
        self.failureRate = 0.02 # 98% chance that the given sim is working 
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
        #self.currentLoad = 0  # i think we can delete this
        self.start = 7  # represents 0700
        self.stop = 23 # represents 2300 
        self.breakTime = 1 # hours
        self.failureRate = 0.25  # 75% chance given aircraft is working
        self.usePerDay = 0  # no more than 4 times per day


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

# HELPER FUNCTIONS
def is_valid_day(day):
    # not a weekend, 96 (long weekend), or a holiday period
    '''
    Thanksgiving -> 27-30nov25
    Christmas -> 25-28dec25
    New Years -> 01-04jan26
    July 4th -> 03-06jul26
    Columbus day -> 11-13oct25
    MLK day -> 17-19jan26
    President's day -> 14-16Feb26
    Memorial day -> 23-25may26
    Juneteenth -> 19-21jun26
    Labor day -> 5-7sep26
    Veterans day -> 11nov25 

    Holiday leave periods:
    1) 15dec-28dec
    2) 29dec-11jan

    '''
    # IMPORTANT: maybe we only assign student the first holiday period of leave or we assign half the first period 
    #            and the other half the second period of leave. We can swap each time we class someone up or there 
    #            could be an even more effecient way. But then we would also have to note which leave period the 
    #            student falls into as a parameter for this function. 
    """
    Returns True if the given date (a datetime.date object) is a valid working day.
    Invalid days include:
      - Weekends (Saturday, Sunday)
      - Fixed holiday periods (same month/day every year)
      - Specific long-weekend patterns (same month/day every year)
      - Annual holiday leave periods (15–28 Dec, 29 Dec–11 Jan)
    """
    # --- Weekend check ---
    if day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        return False
    # Month/day helper
    m, d = day.month, day.day
    # --- Holiday ranges (month/day, month/day) ---
    holiday_ranges = [
        '''
        These change every fiscal year. Maybe this can also be info that gets read in from a file
        '''
        # Long weekends and federal holidays
        ((11, 27), (11, 30)),  # Thanksgiving
        ((12, 25), (12, 28)),  # Christmas
        ((1, 1),  (1, 4)),     # New Years
        ((7, 3),  (7, 6)),     # July 4th
        ((10, 11), (10, 13)),  # Columbus Day
        ((1, 17), (1, 19)),    # MLK Day
        ((2, 14),  (2, 16)),   # President's Day
        ((5, 23),  (5, 25)),   # Memorial Day
        ((6, 19),  (6, 21)),   # Juneteenth
        ((9, 5),  (9, 7)),     # Labor Day
        ((11, 11), (11, 11)),  # Veterans Day (single day)
        # Holiday leave periods (every year)
        ((12, 15), (12, 28)),  # Holiday leave 1
        # Holiday leave 2 spans across years → handle separately below
    ]
    # Check normal (same-year) ranges
    for (m1, d1), (m2, d2) in holiday_ranges:
        if (m > m1 or (m == m1 and d >= d1)) and (m < m2 or (m == m2 and d <= d2)):
            return False
    # --- Cross-year holiday leave period: 29 Dec → 11 Jan ---
    # Case 1: late December
    if m == 12 and d >= 29:
        return False
    # Case 2: early January
    if m == 1 and d <= 11:
        return False
    # If none of the invalid conditions triggered:
    return True


def isResourceAvailable(event, resourceList):
    # check everything including dwellTime and how many times used that day, etc ...
    '''
    1) given the event, identify which type of resource is needed
    2) look through a list of that type of resource and see if any of them are available
    3) if none are, return false
    4) if a resource is availble, then we have to do some work...
        a) check if there is enough time in the day given the length of the event 
        b) then block off the aircraft for the time of the event plus its required dwelltime
        c) if the resource is an aircraft, then we need to also check if an instructor is available too
        d) after we have checked everything, and everything is all good, return true
    '''
    pass

def isInstructorAvailble(event, instructors):  #needOnwing?
    # handle forms flight events seperatley bc need to check quals and need two instructors 
    '''
    1) if a forms event
        a) need a section lead and a forms qualled guy
    2) otherwise, if an instructor is available, assign them

    Not really taking onwings into account right now. Also I don't know if this is the best way, haven't thought about it. 

    We may have to do something completely different for forms, because we need two students who are on the same event. 
    But I do think that the two students fly all their forms flights together; not sure if the instructors have to be the same though...
    '''
    pass

def notToday(student):
    # when a student is unable to complete an event on a given day
    student.daysSinceLastEvent += 1
    student.totalWaitTime += 1 

def schedule(student, instrictor, event, resource):
    # if all good
    # take night hours into account
    pass

# IMPORTANT: how to keep track of how many students in each training block? Should we make them classes? Because we 
#            need to look at all the counts to decide where to place students after they complete contacts, and then 
#            also for scheduling for forms (need two students and two instructors)
# My opinion:
# 1) we need a function that keeps track of resources and their scheduling 

# SIMULATION LOGIC 
def run_simulation(students, instructors):
    '''
    This just came to my attention:
    but this loop is going to have to run more often than just once a "day". 
    I THINK IT WILL HAVE TO RUN EVERY 0.1 HOUR UNTIL THE END OF THE WORKING DAY (23) AND THEN START BACK UP AT 0530 THE NEXT DAY.
    '''
    while True:
        # go day by day
        # sort student list at the start of each day by daysSinceLastEvent
        if students is None:
            break # if all students finished 
        if is_valid_day(date) is False:
            continue 
        
        # if it's the 1st or 3rd Monday of the month, start a new class...

        # iterate over the student list:
        '''
        Check student's next event  (also for the events for which this applies, if you can double up, check on that as well)
        1) if next event starts a new training block, and multiple options exist, check the student spread and place student 
        in the block that makes most sense. So if just finished Contacts, either place in instrument ground school or contacts 
        (maybe later we can also place in forms) 
        2) Once next event is decided, check if resources available -> isResourceAvailable(event, resourceList)... something like that
        3) if resource is an aircraft & available, check if instructor availble -> isInstructorAvailble(event, instructors, needOnwing?)
        4) if student is unable to complete event, add a day to daysSinceLastEvent and totalWaitTime, otherwise schedule the student
        5) if all good -> schdule(student, instrictor, event, resource) [updates all variables that need to be updated]
        '''
        # Make sure to account for hours and resource rest time 
        # at the end, update student.currentdate and student.daysInProcess




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
    instrumentsEvents.append(Event("I4201", 92, aircrafts, activityTimeList[91]))  # can do two in one day
    instrumentsEvents.append(Event("I4202", 93, aircrafts, activityTimeList[92]))  # can do two in one day  
    instrumentsEvents.append(Event("I4203", 94, aircrafts, activityTimeList[93]))  # can do two in one day
    instrumentsEvents.append(Event("I4204", 95, aircrafts, activityTimeList[94]))  # can do two in one day
    instrumentsEvents.append(Event("I4301", 96, aircrafts, activityTimeList[95]))  # can do two in one day
    instrumentsEvents.append(Event("I4302", 97, aircrafts, activityTimeList[96]))  # can do two in one day
    instrumentsEvents.append(Event("I4303", 98, aircrafts, activityTimeList[97]))  # can do two in one day
    instrumentsEvents.append(Event("I4304", 99, aircrafts, activityTimeList[98]))  # can do two in one day
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
