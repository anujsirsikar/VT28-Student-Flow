# @author Anuj Sirsikar and Timothy Kedrowski and Lauren Leckelt
# simulates a student going through the primary syllabus in flight school

# have it read from an excel spreadsheet? -> yes, to make a list of students

import datetime
from datetime import date, timedelta
from collections import deque
import time
import sys
from collections import defaultdict
from eventList import getActivityTime, Event, TrainingBlock
from stuAndInsrtr import FlightStudent
from resources import Classroom, Utd, Oft, Vtd, Mr, Aircraft

import pandas as pd
import random
import matplotlib.pyplot as plt
    
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
    if day.today().weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        return False
    # Month/day helper
    m, d = day.month, day.day
    # --- Holiday ranges (month/day, month/day) ---
    holiday_ranges = [
        # """
        # These change every fiscal year. Maybe this can also be info that gets read in from a file
        # """
        # Long weekends and federal holidays
        (date(2025,11, 27), date(2025,11, 30)),  # Thanksgiving
        (date(2025,12, 25), date(2025,12, 28)),  # Christmas
        (date(2025,1, 1),  date(2025,1, 4)),     # New Years
        (date(2025,7, 3),  date(2025,7, 6)),     # July 4th
        (date(2025,10, 11), date(2025,10, 13)),  # Columbus Day
        (date(2025,1, 17), date(2025,1, 19)),    # MLK Day
        (date(2025,2, 14),  date(2025,2, 16)),   # President's Day
        (date(2025,5, 23),  date(2025,5, 25)),   # Memorial Day
        (date(2025,6, 19),  date(2025,6, 21)),   # Juneteenth
        (date(2025,9, 5),  date(2025,9, 7)),     # Labor Day
        (date(2025,11, 11), date(2025,11, 11)),  # Veterans Day (single day)
        # Holiday leave periods (every year)
        (date(2025,12, 15), date(2025,12, 28)),  # Holiday leave 1
        # Holiday leave 2 spans across years → handle separately below
        (date(2025,12,29), date(2026,1,11)), # holiday leave 2
    ]

    for start_date, end_date in holiday_ranges:
        if (start_date<= day.today() <= end_date):
            return False
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

def class_in_progress(event, classrooms):
    for c in classrooms:
        if event == c.event:
            # check to see if room is full
            if c.current_num < c.capacity:
                return classrooms.index(c)
    return 99

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
    counter = 0 # turning off infinite loop until simulation works
    while True:  
        # go day by day
        # sort student list at the start of each day by daysSinceLastEvent
        if students is None:
            break # if all students finished 
        if not is_valid_day(date):
            continue 
        
        if counter < 20:
            counter +=1
        else: 
            print("counter exceeded")
            break
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


daytime_hours = 11 ## 7 to 6
nighttime_hours = 5
instructors = 40
instructor_rate = 0.9
instructor_daily_hours = 12
'''
def schedule_one_day(students, instructors, utd, oft, vtd, mr, aircraft, classroom, grndSchool, contacts, aero, inst, forms, capstone):
    # events that will be attempted to schedule for each student
    events_to_attempt = []

    # sort the student by longest time since last event
    students.sort(key=lambda s: s.days_since_last_event, reverse=True)

    # can (for 97% of the time) only do one event a day -> unless multiple events taking place on the same training day
    for s in students:
        s.daily_events_done = 0  # unsure if I need this
        nxt = s.next_event()
        # NEED TO SOMEHOW ACCOUNT FOR EVENTS THAT TAKE PLACE ON THE SAME TRAINING DAY (make a function that combines all the events for a single training day into one big event)
        if nxt and s.completion_date is None: # if they have an event and are not finished add it to the attempted events
            events_to_attempt.append((s,nxt))

    # Filter out failed devices
    working_utds = [sim for sim in utd if random.random() > Sim.failure_rate]
    working_ofts = [sim for sim in oft if random.random() > Sim.failure_rate]
    working_vtds = [sim for sim in vtd if random.random() > Sim.failure_rate]
    working_mrs  = [sim for sim in mr  if random.random() > Sim.failure_rate]
    working_aircraft = [ac for ac in aircraft if random.random() > Aircraft.failure_rate]

    utd_hours = {sim: Sim.daily_hours for sim in working_utds}
    oft_hours = {sim: Sim.daily_hours for sim in working_ofts}
    vtd_hours = {sim: Sim.daily_hours for sim in working_vtds}
    mr_hours  = {sim: Sim.daily_hours for sim in working_mrs}
    aircraft_day_hours = {ac: (Aircraft.daily_hours - daytime_hours) for ac in working_aircraft}
    #classroom_hours = {c: Classroom.daily_hours for c in classroom}

    # instructors now
    # want to leave these as objects because we will need to check their quals later on and check onwings 
    instructors_available = [instructor for instructor in instructors if random.random() > Instructor.failure_rate]
    instructor_hours = {instructor: Instructor.daily_hours for instructor in instructors_available}

    # looking at student and the event they are scheduled for
    for s, ev in events_to_attempt:
        #getting how long the event it. 
        needed_time = ev.activity_time
        needed_resource = ev.resource

        if needed_resource == "classroom":
            # Just thinking, and we need to account for whether the classroom is at capacity. And then if down the event
            # list, this event pops up again, we need to use the same classroom...
            helper = 0
            # going to have to keep classrooms as objects
            for c in classroom: # classroom is a list of classroom objects 
                # 1) check if the event is already assigned to a classroom
                #   If it is...
                #   a) and there is space in the class, schedule the student and dont need to play around with the classroom's hours, just its current_num
                #   b) if there is no space, go check if another classroom is available
                # 2) if it isn't, then just assign it to a classroom if possible, and update hours and the classroom's current_num
                fate = class_in_progress(ev, classroom)
                if fate != 99:
                    assigned_classroom = classroom[fate]
                    s.event_complete()
                    assigned_classroom.current_num += 1
                    helper = 1
                    break
                else:
                    if needed_time <= c.daily_hours:
                        c.daily_hours = c.daily_hours - needed_time
                        c.event = ev
                        c.current_num += 1
                        s.event_complete()
                        helper = 1
                        break
            if helper == 0:
                s.days_since_last_event += 1
                s.total_wait_time += 1
            s.total_wait_time += 1  #delete this

#### ADD BLOCK SPECIFIC WAIT TINME

        elif needed_resource == "utd":
            helper = 0   # if stays zero, then not scheduled
            for hours in utd_hours.values():
                if need_time <= hours:
                    hours = hours - need_time #ADD BREAK TIOKE
                    # schedule the student
                    s.event_complete()
                    helper = 1
                    break
            if helper == 0:
                # not scheduled
                s.days_since_last_event += 1
                s.total_wait_time += 1
            s.total_wait_time += 1 # DELETE
        elif needed_resource == "oft":
            helper = 0   # if stays zero, then not scheduled
            for hours in oft_hours.values():
                if need_time <= hours:
                    hours = hours - need_time
                    # schedule the student
                    s.event_complete()
                    helper = 1
                    break
            if helper == 0:
                # not scheduled
                s.days_since_last_event += 1
                s.total_wait_time += 1
            s.total_wait_time += 1
        elif needed_resource == "vtd":
            helper = 0   # if stays zero, then not scheduled
            for hours in vtd_hours.values():
                if need_time <= hours:
                    hours = hours - need_time
                    # schedule the student
                    s.event_complete()
                    helper = 1
                    break
            if helper == 0:
                # not scheduled
                s.days_since_last_event += 1
                s.total_wait_time += 1
            s.total_wait_time += 1
        elif needed_resource == "mr":
            helper = 0   # if stays zero, then not scheduled
            for hours in mr_hours.values():
                if need_time <= hours:
                    hours = hours - need_time
                    # schedule the student
                    s.event_complete()
                    helper = 1
                    break
            if helper == 0:
                # not scheduled
                s.days_since_last_event += 1
                s.total_wait_time += 1
            s.total_wait_time += 1
        else:
            # gonna need an aircraft and an instructor
            # Later: add in stuff about day or night...
            helper = 0
            ## make sure actuallly values not copies
            for hours in aircraft_day_hours.values():
                done = 0
                if need_time <= hours:
                    for time in instructor_hours.values():
                        if need_time <= time:
                            hours = hours - need_time
                            time = time - need_time
                            s.event_complete()
                            helper = 1
                            done = 1
                            break
                    if done == 1:
                        break
            if helper == 0:
                # not scheduled
                s.days_since_last_event += 1
                s.total_wait_time += 1
            s.total_wait_time += 1
    
    # need to reset the classroom variables after each day
    for c in classroom:
        c.current_num = 0
        c.event = None
        c.daily_hours = 12

'''
def main():
    students = [] # this will be a deque of students (for the future: be able to read in an excel sheet and then initialize student objects to populate this)
    # Let's make some students
    print(date.today())
    for i in range(5):
        new_student = FlightStudent(i, i, "waiting")
        new_student.totalWaitTime = i
        students.append(new_student) # **IMPORTANT: change what i is being divided by to control class size (i.e. how many people are starting each week)

    print(students)

    students.sort(key=lambda s: s.days_since_last_event, reverse=True)

    print(i for i in students)


    # Resources
    classrooms = [Classroom(f"CL{i+1}") for i in range(6)]
    utd_sims = [Utd(f"UTD{i+1}") for i in range(6)]
    oft_sims = [Oft(f"OFT{i+1}") for i in range(6)]
    vtd_sims = [Vtd(f"VTD{i+1}") for i in range(18)]
    mr_sims = [Mr(f"MR{i+1}") for i in range(2)]
    aircrafts = [Aircraft(f"AC{i+1}") for i in range(18)]

    # keep track of each event's activity time
    activity_time_dict = getActivityTime()


    # Initialize a list of event objects for each block
    sysGrndSchoolEvents = []
    # MAKE THE RESOURCES A STRING!!!
    sysGrndSchoolEvents.append(Event("G0101", 1, classrooms, activity_time_dict["G0101"]/2))
    sysGrndSchoolEvents.append(Event("G6001", 1, classrooms, activity_time_dict["G6001"]/2))
    sysGrndSchoolEvents.append(Event("G0107", 2, classrooms, activity_time_dict["G0107"]/3))
    sysGrndSchoolEvents.append(Event("SY0101", 2, classrooms, activity_time_dict["SY0101"]/3))
    sysGrndSchoolEvents.append(Event("SY0102", 2, classrooms, activity_time_dict["SY0102"]/3))
    sysGrndSchoolEvents.append(Event("SY0106", 3, classrooms, activity_time_dict["SY0106"]))
    sysGrndSchoolEvents.append(Event("SY0112", 4, classrooms, activity_time_dict["SY0112"]))
    sysGrndSchoolEvents.append(Event("SY0190", 5, classrooms, activity_time_dict["SY0190"]/2))
    sysGrndSchoolEvents.append(Event("SY0203", 5, classrooms, activity_time_dict["SY0203"]/2))
    sysGrndSchoolEvents.append(Event("SY0206", 6, classrooms, activity_time_dict["SY0206"]/2))
    sysGrndSchoolEvents.append(Event("G0106", 6, classrooms, activity_time_dict["G0106"]/2))
    sysGrndSchoolEvents.append(Event("SY0290", 7, classrooms, activity_time_dict["SY0290"]/3))
    sysGrndSchoolEvents.append(Event("G0104", 7, classrooms, activity_time_dict["G0104"]/3))
    sysGrndSchoolEvents.append(Event("G0105", 7, classrooms, activity_time_dict["G0105"]/3))
    sysGrndSchoolEvents.append(Event("SY0301", 8, classrooms, activity_time_dict["SY0301"]/3))
    sysGrndSchoolEvents.append(Event("PR0101", 8, classrooms, activity_time_dict["PR0101"]/3))
    sysGrndSchoolEvents.append(Event("PR0102B", 8, classrooms, activity_time_dict["PR0102B"]/3))
    sysGrndSchoolEvents.append(Event("PR0103", 9, classrooms, activity_time_dict["PR0103"]/3))
    sysGrndSchoolEvents.append(Event("PR0104", 9, classrooms, activity_time_dict["PR0104"]/3))
    sysGrndSchoolEvents.append(Event("PR0105", 9, classrooms, activity_time_dict["PR0105"]/3))
    sysGrndSchoolEvents.append(Event("FAM1106", 10, classrooms, activity_time_dict["FAM1106"]))
    sysGrndSchoolEvents.append(Event("FAM1190", 11, classrooms, activity_time_dict["FAM1190"]/2))
    sysGrndSchoolEvents.append(Event("FAM1203", 11, classrooms, activity_time_dict["FAM1203"]/2))
    sysGrndSchoolEvents.append(Event("FAM1290", 12, classrooms, activity_time_dict["FAM1290"]/3))
    sysGrndSchoolEvents.append(Event("G0201", 12, classrooms, activity_time_dict["G0201"]/3))
    sysGrndSchoolEvents.append(Event("G0103", 12, classrooms, activity_time_dict["G0103"]/3))
    sysGrndSchoolEvents.append(Event("G0290", 13, classrooms, activity_time_dict["G0290"]/2))
    sysGrndSchoolEvents.append(Event("G0102", 13, classrooms, activity_time_dict["G0102"]/2))

    
    contactsEvents = []

    contactsEvents.append(Event("FAM2101", 14, utd_sims, activity_time_dict["FAM2101"]))
    contactsEvents.append(Event("FAM2102", 15, utd_sims, activity_time_dict["FAM2102"]))
    contactsEvents.append(Event("FAM2201", 16, utd_sims, activity_time_dict["FAM2201"]))
    contactsEvents.append(Event("FAM2202", 17, utd_sims, activity_time_dict["FAM2202"]))
    contactsEvents.append(Event("IN1104", 18, classrooms, activity_time_dict["IN1104"]))
    contactsEvents.append(Event("I2101", 19, utd_sims, activity_time_dict["I2101"]))
    contactsEvents.append(Event("I2102", 20, utd_sims, activity_time_dict["I2102"]))
    contactsEvents.append(Event("I2103", 21, utd_sims, activity_time_dict["I2103"]))
    contactsEvents.append(Event("FAM3101", 22, oft_sims, activity_time_dict["FAM3101"]))
    contactsEvents.append(Event("FAM3102", 23, oft_sims, activity_time_dict["FAM3102"]))
    contactsEvents.append(Event("FAM3103", 24, oft_sims, activity_time_dict["FAM3103"]))
    contactsEvents.append(Event("FAM6101", 25, vtd_sims, activity_time_dict["FAM6101"]))
    contactsEvents.append(Event("FAM6102", 26, vtd_sims, activity_time_dict["FAM6102"]))
    contactsEvents.append(Event("FAM6201", 27, vtd_sims, activity_time_dict["FAM6201"]))
    contactsEvents.append(Event("FAM6202", 28, vtd_sims, activity_time_dict["FAM6202"]))
    contactsEvents.append(Event("FAM6203", 29, vtd_sims, activity_time_dict["FAM6203"]))
    contactsEvents.append(Event("FAM6301", 30, vtd_sims, activity_time_dict["FAM6301"]))
    contactsEvents.append(Event("FAM6302", 31, vtd_sims, activity_time_dict["FAM6302"]))
    contactsEvents.append(Event("FAM1301", 32, aircrafts, activity_time_dict["FAM1301"])) # onwing
    contactsEvents.append(Event("FAM4101", 33, aircrafts, activity_time_dict["FAM4101"])) # onwing
    contactsEvents.append(Event("FAM4102", 34, aircrafts, activity_time_dict["FAM4102"])) # onwing
    contactsEvents.append(Event("FAM4103", 35, aircrafts, activity_time_dict["FAM4103"])) # onwing
    contactsEvents.append(Event("FAM4104", 36, aircrafts, activity_time_dict["FAM4104"])) # onwing
    contactsEvents.append(Event("FAM3201", 37, oft_sims, activity_time_dict["FAM3201"]))
    contactsEvents.append(Event("FAM3202", 38, oft_sims, activity_time_dict["FAM3202"]))
    contactsEvents.append(Event("FAM3301", 39, oft_sims, activity_time_dict["FAM3301"]))
    contactsEvents.append(Event("FAM6401", 40, vtd_sims, activity_time_dict["FAM6401"]))
    contactsEvents.append(Event("FAM6402", 41, vtd_sims, activity_time_dict["FAM6402"]))
    contactsEvents.append(Event("FAM4201", 42, aircrafts, activity_time_dict["FAM4201"]))
    contactsEvents.append(Event("FAM4202", 43, aircrafts, activity_time_dict["FAM4202"]))
    contactsEvents.append(Event("FAM1206", 44, classrooms, activity_time_dict["FAM1206"]))
    contactsEvents.append(Event("FAM4203", 45, aircrafts, activity_time_dict["FAM4203"]))
    contactsEvents.append(Event("FAM4204", 46, aircrafts, activity_time_dict["FAM4204"]))
    contactsEvents.append(Event("FAM4301", 47, aircrafts, activity_time_dict["FAM4301"]))
    contactsEvents.append(Event("FAM4302", 48, aircrafts, activity_time_dict["FAM4302"]))
    contactsEvents.append(Event("FAM4303", 49, aircrafts, activity_time_dict["FAM4303"])) # onwing
    contactsEvents.append(Event("FAM4304", 50, aircrafts, activity_time_dict["FAM4304"])) # onwing
    contactsEvents.append(Event("FAM4490", 51, aircrafts, activity_time_dict["FAM4490"]))
    contactsEvents.append(Event("FAM4501", 52, aircrafts, activity_time_dict["FAM4501"]))

    aeroEvents = []
    aeroEvents.append(Event("FAM3401", 53, oft_sims, activity_time_dict["FAM3401"]))
    aeroEvents.append(Event("FAM4701", 54, aircrafts, activity_time_dict["FAM4701"]))
    aeroEvents.append(Event("FAM4702", 55, aircrafts, activity_time_dict["FAM4702"]))
    aeroEvents.append(Event("FAM4703", 56, aircrafts, activity_time_dict["FAM4703"]))


    instrGrndSchoolEvents = []
    instrGrndSchoolEvents.append(Event("IN1202", 57, classrooms, activity_time_dict["IN1202"]/2))
    instrGrndSchoolEvents.append(Event("IN1203", 57, classrooms, activity_time_dict["IN1203"]/2))
    instrGrndSchoolEvents.append(Event("IN1205", 58, classrooms, activity_time_dict["IN1205"]/2))
    instrGrndSchoolEvents.append(Event("IN1206", 58, classrooms, activity_time_dict["IN1206"]/2))
    instrGrndSchoolEvents.append(Event("IN1290", 59, classrooms, activity_time_dict["IN1290"]))
    instrGrndSchoolEvents.append(Event("IN1305", 60, classrooms, activity_time_dict["IN1305"]/2))
    instrGrndSchoolEvents.append(Event("IN1306", 60, classrooms, activity_time_dict["IN1306"]/2))
    instrGrndSchoolEvents.append(Event("IN1307", 61, classrooms, activity_time_dict["IN1307"]/2))
    instrGrndSchoolEvents.append(Event("IN1308", 61, classrooms, activity_time_dict["IN1308"]/2))
    instrGrndSchoolEvents.append(Event("IN1390", 62, classrooms, activity_time_dict["IN1390"]/2))
    instrGrndSchoolEvents.append(Event("IN1403", 62, classrooms, activity_time_dict["IN1403"]/2))
    instrGrndSchoolEvents.append(Event("IN1406", 63, classrooms, activity_time_dict["IN1406"]))
    instrGrndSchoolEvents.append(Event("IN1411", 64, classrooms, activity_time_dict["IN1411"]/3))
    instrGrndSchoolEvents.append(Event("IN1412", 64, classrooms, activity_time_dict["IN1412"]/3))
    instrGrndSchoolEvents.append(Event("IN1413A", 64, classrooms, activity_time_dict["IN1413A"]/3))
    instrGrndSchoolEvents.append(Event("IN1490", 65, classrooms, activity_time_dict["IN1490"]/2))
    instrGrndSchoolEvents.append(Event("IN1501", 65, classrooms, activity_time_dict["IN1501"]/2))
    instrGrndSchoolEvents.append(Event("NA1105", 66, classrooms, activity_time_dict["NA1105"]/2))
    instrGrndSchoolEvents.append(Event("NA1106", 66, classrooms, activity_time_dict["NA1106"]/2))
    instrGrndSchoolEvents.append(Event("NA1190", 67, classrooms, activity_time_dict["NA1190"]))


    instrumentsEvents = []
    instrumentsEvents.append(Event("I2201", 68, utd_sims, activity_time_dict["I2201"]))
    instrumentsEvents.append(Event("I2202", 69, utd_sims, activity_time_dict["I2202"]))
    instrumentsEvents.append(Event("I2203", 70, utd_sims, activity_time_dict["I2203"]))
    instrumentsEvents.append(Event("N3101", 71, oft_sims, activity_time_dict["N3101"]))
    instrumentsEvents.append(Event("N6101", 72, vtd_sims, activity_time_dict["N6101"]))
    instrumentsEvents.append(Event("I6101", 73, vtd_sims, activity_time_dict["I6101"]))
    instrumentsEvents.append(Event("I6102", 74, vtd_sims, activity_time_dict["I6102"]))
    instrumentsEvents.append(Event("I3101", 75, utd_sims, activity_time_dict["I3101"]))
    instrumentsEvents.append(Event("I3102", 76, utd_sims, activity_time_dict["I3102"]))
    instrumentsEvents.append(Event("I3103", 77, utd_sims, activity_time_dict["I3103"]))
    instrumentsEvents.append(Event("I3104", 78, oft_sims, activity_time_dict["I3104"]))
    instrumentsEvents.append(Event("I6201", 79, vtd_sims, activity_time_dict["I6201"]))
    instrumentsEvents.append(Event("I6202", 80, vtd_sims, activity_time_dict["I6202"]))
    instrumentsEvents.append(Event("I4101", 81, aircrafts, activity_time_dict["I4101"]))
    instrumentsEvents.append(Event("I4102", 82, aircrafts, activity_time_dict["I4102"]))
    instrumentsEvents.append(Event("I4103", 83, aircrafts, activity_time_dict["I4103"]))
    instrumentsEvents.append(Event("SY0302", 84, classrooms, activity_time_dict["SY0302"]))
    instrumentsEvents.append(Event("I3201", 85, utd_sims, activity_time_dict["I3201"]))
    instrumentsEvents.append(Event("I3202", 86, utd_sims, activity_time_dict["I3202"]))
    instrumentsEvents.append(Event("I3203", 87, oft_sims, activity_time_dict["I3203"]))
    instrumentsEvents.append(Event("I3204", 88, oft_sims, activity_time_dict["I3204"]))
    instrumentsEvents.append(Event("I3205", 89, oft_sims, activity_time_dict["I3205"]))
    instrumentsEvents.append(Event("I3206", 90, oft_sims, activity_time_dict["I3206"]))
    instrumentsEvents.append(Event("I6301", 91, vtd_sims, activity_time_dict["I6301"]))
    instrumentsEvents.append(Event("I4201", 92, aircrafts, activity_time_dict["I4201"]))
    instrumentsEvents.append(Event("I4202", 93, aircrafts, activity_time_dict["I4202"]))
    instrumentsEvents.append(Event("I4203", 94, aircrafts, activity_time_dict["I4203"]))
    instrumentsEvents.append(Event("I4204", 95, aircrafts, activity_time_dict["I4204"]))
    instrumentsEvents.append(Event("I4301", 96, aircrafts, activity_time_dict["I4301"]))
    instrumentsEvents.append(Event("I4302", 97, aircrafts, activity_time_dict["I4302"]))
    instrumentsEvents.append(Event("I4303", 98, aircrafts, activity_time_dict["I4303"]))
    instrumentsEvents.append(Event("I4304", 99, aircrafts, activity_time_dict["I4304"]))
    instrumentsEvents.append(Event("I4490", 100, aircrafts, activity_time_dict["I4490"]))
    instrumentsEvents.append(Event("N4101", 101, aircrafts, activity_time_dict["N4101"]))
    instrumentsEvents.append(Event("FAM4601", 102, aircrafts, activity_time_dict["FAM4601"]))

    formsEvents = []
    formsEvents.append(Event("F1102", 103, classrooms, activity_time_dict["F1102"]))
    formsEvents.append(Event("FF190", 104, classrooms, activity_time_dict["FF190"]))
    formsEvents.append(Event("FF1201", 105, classrooms, activity_time_dict["FF1201"]))
    formsEvents.append(Event("F3101", 106, oft_sims, activity_time_dict["F3101"]))
    formsEvents.append(Event("F2101", 107, mr_sims, activity_time_dict["F2101"]))
    formsEvents.append(Event("F4101", 108, aircrafts, activity_time_dict["F4101"]))
    formsEvents.append(Event("F4102", 109, aircrafts, activity_time_dict["F4102"]))
    formsEvents.append(Event("F4103", 110, aircrafts, activity_time_dict["F4103"]))
    formsEvents.append(Event("F4104", 111, aircrafts, activity_time_dict["F4104"]))
    formsEvents.append(Event("F4290", 112, aircrafts, activity_time_dict["F4290"]))

    capstoneEvents = []
    capstoneEvents.append(Event("CS1101", 113, classrooms, activity_time_dict["CS1101"]))
    capstoneEvents.append(Event("CS2101", 114, mr_sims, activity_time_dict["CS2101"]))
    capstoneEvents.append(Event("CS2102", 115, mr_sims, activity_time_dict["CS2102"]))
    capstoneEvents.append(Event("CS3101", 116, oft_sims, activity_time_dict["CS3101"]))
    capstoneEvents.append(Event("CS3102", 117, oft_sims, activity_time_dict["CS3102"]))
    capstoneEvents.append(Event("CS4101", 118, aircrafts, activity_time_dict["CS4101"]))
    capstoneEvents.append(Event("CS4102", 119, aircrafts, activity_time_dict["CS4102"]))
    capstoneEvents.append(Event("CS4290", 120, aircrafts, activity_time_dict["CS4290"]))

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
    # run_simulation(students, syllabus)



if __name__ == "__main__":
    main()
