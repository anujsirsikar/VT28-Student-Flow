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
from stuAndInsrtr import FlightStudent, Instructor
from resources import Classroom, Utd, Oft, Vtd, Mr, Aircraft, Sim
import csv
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

def schedule(student, instrictor, event, resource):
    # if all good
    # take night hours into account
    pass

def class_in_progress(event, classrooms):
    for c in classrooms:
        if event == classrooms[c][1]:
            capacity_index = classrooms[c][2]
            capacity = classrooms[c][3][capacity_index]
            if capacity < c.capacity:
                return c
    return 99

# IMPORTANT: how to keep track of how many students in each training block? Should we make them classes? Because we 
#            need to look at all the counts to decide where to place students after they complete contacts, and then 
#            also for scheduling for forms (need two students and two instructors)
# My opinion:
# 1) we need a function that keeps track of resources and their scheduling 

# SIMULATION LOGIC 
def run_simulation(students, instructors):
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

        # run the schedule_one_day() function for every valid day


daytime_hours = 11 ## 7 to 6
nighttime_hours = 5
instructors = 40
instructor_rate = 0.9
instructor_daily_hours = 12

def schedule_one_day(students, day, instructors, utd, oft, vtd, mr, aircraft, classroom, syllabus):# grndSchool, contacts, aero, inst, forms, capstone):
    # events that will be attempted to schedule for each student
    events_to_attempt = []
    successfull_events = []

    # sort the student by longest time since last event
    if day != date.today():
        students.sort(key=lambda s: s.days_since_last_event, reverse=True)

    for s in students:
        # s.daily_events_done = 0  # unsure if I need this
        block, event = s.next_event()
        nxt = syllabus[block][event]
        # NEED TO SOMEHOW ACCOUNT FOR EVENTS THAT TAKE PLACE ON THE SAME TRAINING DAY (make a function that combines all the events for a single training day into one big event)
        if nxt and s.completion_date is None: # if they have an event and are not finished add it to the attempted events
            events_to_attempt.append((s,nxt))

    # Filter out failed devices. Note this changes every day
    working_utds = [sim for sim in utd if random.random() > Sim.failure_rate]
    working_ofts = [sim for sim in oft if random.random() > Sim.failure_rate]
    working_vtds = [sim for sim in vtd if random.random() > Sim.failure_rate]
    working_mrs  = [sim for sim in mr  if random.random() > Sim.failure_rate]
    working_aircraft = [ac for ac in aircraft if random.random() > Aircraft.failure_rate]


    ## these are objects where the mapping is Object: hours ex. UTD object: 17.5
    utd_hours = {sim: Sim.daily_hours for sim in working_utds}
    oft_hours = {sim: Sim.daily_hours for sim in working_ofts}
    vtd_hours = {sim: Sim.daily_hours for sim in working_vtds}
    mr_hours  = {sim: Sim.daily_hours for sim in working_mrs}
    aircraft_day_hours = {ac: (Aircraft.daily_hours - daytime_hours) for ac in working_aircraft}

    # format object: [hours, event, current capacity check, [capacity_event_one, capacity_event_two, etc...]]
    classroom_hours_events = {c: [Classroom.daily_hours, None, -1, [0, 0, 0, 0]] for c in classroom}

    # instructors now
    # want to leave these as objects because we will need to check their quals later on and check onwings 
    ## these are objects where the mapping is Object: hours ex. UTD object: 17.5
    instructors_available = [instructor for instructor in instructors if random.random() > Instructor.failure_rate]
    instructor_hours = {instructor: Instructor.daily_hours for instructor in instructors_available}

    # looking at student and the event they are scheduled for
    for s, ev in events_to_attempt:
        #getting how long the event it. 
        needed_time = ev.activity_time
        needed_resource = ev.resource

        if needed_resource == "classroom":
            helper = 0
            fate = class_in_progress(ev, classroom_hours_events)
            if fate != 99:
                successfull_events.append([s,ev, day, str(fate) + " Class: " + str(classroom_hours_events[fate][2]) + " Student: " + str(classroom_hours_events[fate][3][classroom_hours_events[fate][2]])])
                s.event_complete()
                classroom_hours_events[fate][3][classroom_hours_events[fate][2]] += 1
                helper = 1
            else:
                for c in classroom_hours_events: # classroom is a list of classroom objects 
                # 1) check if the event is already assigned to a classroom
                #   If it is...
                #   a) and there is space in the class, schedule the student and dont need to play around with the classroom's hours, just its current_num
                #   b) if there is no space, go check if another classroom is available
                # 2) if it isn't, then just assign it to a classroom if possible, and update hours and the classroom's current_num
                # fate = class_in_progress(ev, classroom)
                # if fate != 99:
                #     assigned_classroom = classroom[fate]
                #     s.event_complete()
                #     assigned_classroom.current_num += 1
                #     helper = 1
                #     break
                # else:
                    if needed_time <= classroom_hours_events[c][0]:
                        classroom_hours_events[c][0] -= needed_time
                        classroom_hours_events[c][1] = ev
                        capacity_index = classroom_hours_events[c][2]
                        classroom_hours_events[c][3][capacity_index] = 1
                        classroom_hours_events[c][2] += 1
                        successfull_events.append([s,ev, day, str(c) + " Class: " + str(classroom_hours_events[c][2]) + " Student: " + str(classroom_hours_events[c][3][classroom_hours_events[c][2]])])
                        classroom_hours_events[c][3][classroom_hours_events[c][2]] += 1
                        s.event_complete()
                        helper = 1
                        sorted_classroom = sorted(classroom_hours_events.items(), key=lambda item: item[1][0], reverse=True)
                        classroom_hours_events = dict(sorted_classroom)
                        break
            if helper == 0:
                s.days_since_last_event += 1
                s.total_wait_time += 1
            
#### ADD BLOCK SPECIFIC WAIT TINME

        elif needed_resource == "utd":
            helper = 0   # if stays zero, then not scheduled
            for u in utd_hours:
                if needed_time <= utd_hours[u]:
                    utd_hours[u] -=  (needed_time + Sim.break_time) #ADD BREAK Time
                    # schedule the student
                    successfull_events.append([s,ev, day, u])
                    s.event_complete()
                    helper = 1
                    break
            if helper == 0:
                # not scheduled
                s.days_since_last_event += 1
                s.total_wait_time += 1
                
        elif needed_resource == "oft":
            helper = 0   # if stays zero, then not scheduled
            for o in oft_hours:
                if needed_time <= oft_hours[o]:
                    oft_hours[o] -= (needed_time + Sim.break_time)
                    # schedule the student
                    successfull_events.append([s,ev, day, o])
                    s.event_complete()
                    helper = 1
                    break
            if helper == 0:
                # not scheduled
                s.days_since_last_event += 1
                s.total_wait_time += 1
                
        elif needed_resource == "vtd":
            helper = 0   # if stays zero, then not scheduled
            for v in vtd_hours:
                if needed_time <= vtd_hours[v]:
                    vtd_hours[v] -= (needed_time + Sim.break_time)
                    # schedule the student
                    successfull_events.append([s,ev, day, v])
                    s.event_complete()
                    helper = 1
                    break
            if helper == 0:
                # not scheduled
                s.days_since_last_event += 1
                s.total_wait_time += 1
                
        elif needed_resource == "mr":
            helper = 0   # if stays zero, then not scheduled
            for m in mr_hours:
                if needed_time <= mr_hours[m]:
                    mr_hours -= (needed_time + Sim.break_time)
                    # schedule the student
                    successfull_events.append([s,ev, day, m])
                    s.event_complete()
                    helper = 1
                    break
            if helper == 0:
                # not scheduled
                s.days_since_last_event += 1
                s.total_wait_time += 1
            
        else: ##aircraft
            # gonna need an aircraft and an instructor
            # Later: add in stuff about day or night...
            aircraft_found = 0
            ## make sure actuallly values not copies
            for ac in aircraft_day_hours:
                print(type(ac))
                instructor_found = 0
                if needed_time <= aircraft_day_hours[ac] and ac.use_per_day < 4:
                    for inst in instructor_hours:
                        if needed_time <= instructor_hours[inst]:
                            aircraft_day_hours[ac] -= (needed_time + Aircraft.break_time)
                            instructor_hours[inst] -= (needed_time + Instructor.break_time)
                            successfull_events.append([s,ev, day, ac,inst])
                            s.event_complete()
                            aircraft_found = 1
                            instructor_found = 1
                            break
                    if instructor_found == 1:
                        break
            if aircraft_found == 0:
                # not scheduled
                s.days_since_last_event += 1
                s.total_wait_time += 1

    return successfull_events
            
    
    # # need to reset the classroom variables after each day
    # for c in classroom:
    #     c.current_num = 0
    #     c.event = None
    #     c.daily_hours = 12

# reads in events from a csv file and makes event objects per block and puts that in a list
def make_events(file_path, block):
    # keep track of each event's activity time
    activity_time_dict = getActivityTime()
    events = []
    csv_data = file_path
    # Read CSV into rows
    rows = []
    with open(file_path, "r") as f:
        next(f)  # skip header
        for line in f:
            event_id, training_day, resource = [x.strip() for x in line.split(",")]
            rows.append((event_id, int(training_day), resource))
    # ---------- GROUP EVENTS BY TRAINING DAY ----------
    grouped = defaultdict(lambda: {"names": [], "resource": None, "time": 0.0})
    for event_id, day, resource in rows:
        grouped[day]["names"].append(event_id)
        grouped[day]["resource"] = resource
        grouped[day]["time"] += activity_time_dict[event_id]
    # ---------- CREATE FINAL COMBINED EVENT OBJECTS ----------
    for day, data in sorted(grouped.items()):
        merged_name = "/".join(data["names"])
        total_time = data["time"]
        resource = data["resource"]
        events.append(Event(merged_name, day, resource, total_time, block))
    return events


def main():
    # Resources
    classrooms = "classroom"
    utd_sims = "utd"
    oft_sims = "oft"
    vtd_sims = "vtd"
    mr_sims = "mr"
    aircrafts = "aircraft"

    # Initialize a list of event objects for each block
    sysGrndSchoolEvents = make_events(r"data\sysGrnd.csv", "system ground")
    print("sys grnd: ", sysGrndSchoolEvents)
    # FAM1301, FAM4101, FAM4102, FAM4103, FAM4104, FAM4303, FAM4304 are the required onwing events
    contactsEvents = make_events(r"data\contacts.csv", "contacts")
    aeroEvents = make_events(r"data\aero.csv", "contacts")
    instrGrndSchoolEvents = make_events(r"data\instrGrnd.csv", "instrument ground")
    instrumentsEvents = make_events(r"data\instr.csv", "instruments")
    formsEvents = make_events(r"data\forms.csv", "forms")
    capstoneEvents = make_events(r"data\capstone.csv", "capstone")
    

    # Initialize the training blocks
    block1 = TrainingBlock("Systems Ground School", 28, sysGrndSchoolEvents, 13, 60.1)  
    block2 = TrainingBlock("Contacts", 39, contactsEvents, 39, 56)
    block3 = TrainingBlock("Aero", 4, aeroEvents, 4, 6.4)
    block4 = TrainingBlock("Instruments Ground School", 20, instrGrndSchoolEvents, 11, 38)
    block5 = TrainingBlock("Instruments", 35, instrumentsEvents, 35, 50.9)
    block6 = TrainingBlock("Forms", 10, formsEvents, 10, 17.1)
    block7 = TrainingBlock("Capstone", 8, capstoneEvents, 8, 12.3)

    # Combine into syllabus
    syllabus_old = [block1, block2, block3, block4, block5, block6, block7]
 
    syllabus = [sysGrndSchoolEvents, contactsEvents, aeroEvents, instrGrndSchoolEvents, instrumentsEvents, formsEvents, capstoneEvents]
    # Resources
    classrooms_list = [Classroom(f"CL{i+1}") for i in range(6)]
    utd_sims_list = [Utd(f"UTD{i+1}") for i in range(6)]
    oft_sims_list = [Oft(f"OFT{i+1}") for i in range(6)]
    vtd_sims_list = [Vtd(f"VTD{i+1}") for i in range(18)]
    mr_sims_list = [Mr(f"MR{i+1}") for i in range(2)]
    aircraft_list = [Aircraft(f"AC{i+1}") for i in range(18)]
    # Run the simulation
    # run_simulation(students, syllabus)/


    default_value=10

    students = [] # this will be a deque of students (for the future: be able to read in an excel sheet and then initialize student objects to populate this)
    # Let's make some students

    user_input = input("Enter a number of initial students (default 10): ")
    
    try:
        value = int(user_input)
    except ValueError:
        value = default_value

    if value > 100:
        value = 100


    for i in range(value):
        new_student = FlightStudent(i, i//8, date.today())
        new_student.days_since_last_event = i
        students.append(new_student) # **IMPORTANT: change what i is being divided by to control class size (i.e. how many people are starting each week)


    instructors = []

    for i in range(20):
        new_instructor = Instructor(i, True, True)
        instructors.append(new_instructor)

    result = []

    user_input = input("Enter a number of days (default 10): ")

    try: 
        value = int(user_input)
    except ValueError:
        value = default_value

    if value > 365:
        value = 365

    for i in range(value):
        current = date.today() + timedelta(days=i)
        result.append(schedule_one_day(students, current, instructors, utd_sims_list, oft_sims_list, vtd_sims_list, mr_sims_list, aircraft_list, classrooms_list, syllabus))

    for i in result:
        for j in i:
            print(j)

if __name__ == "__main__":
    main()
