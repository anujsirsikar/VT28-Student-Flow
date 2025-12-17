# @author Anuj Sirsikar and Timothy Kedrowski and Lauren Leckelt
# simulates a student going through the primary syllabus in flight school

# RANDOM ONE OFF CASES:
# randomly did SY0302 while in instr grnd:
# 102,2511,Active,12/16/2024,12/16/2024,12/17/2024,12/17/2024,12/17/2024,12/18/2024,12/19/2024,12/20/2024,12/20/2024,1/7/2025,1/7/2025,1/8/2025,1/8/2025,1/8/2025,1/10/2025,1/10/2025,1/10/2025,1/13/2025,1/13/2025,1/13/2025,1/14/2025,1/15/2025,1/15/2025,1/16/2025,1/16/2025,1/16/2025,1/17/2025,1/17/2025,1/22/2025,1/23/2025,1/24/2025,1/27/2025,1/28/2025,1/30/2025,2/3/2025,2/7/2025,2/13/2025,2/18/2025,2/19/2025,2/20/2025,2/24/2025,2/25/2025,2/26/2025,2/27/2025,2/28/2025,3/3/2025,3/24/2025,3/25/2025,3/28/2025,3/31/2025,4/9/2025,3/7/2025,3/10/2025,3/11/2025,3/12/2025,3/20/2025,4/10/2025,4/11/2025,4/16/2025,4/14/2025,4/15/2025,4/28/2025,4/29/2025,5/2/2025,5/6/2025,5/13/2025,5/14/2025,,,,,5/28/2025,5/28/2025,5/29/2025,5/29/2025,5/30/2025,6/2/2025,6/3/2025,6/3/2025,6/4/2025,6/4/2025,6/5/2025,6/6/2025,6/6/2025,6/6/2025,,,,,,,,,,,,,,,,,,,,,,9/17/2025,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# instr -> forms -> aero?:
# 118,2511,Active,12/16/2024,12/16/2024,12/17/2024,12/17/2024,12/17/2024,12/18/2024,12/19/2024,12/20/2024,12/20/2024,1/7/2025,1/7/2025,1/8/2025,1/8/2025,1/8/2025,1/10/2025,1/10/2025,1/10/2025,1/13/2025,1/13/2025,1/13/2025,1/14/2025,1/15/2025,1/15/2025,1/16/2025,1/16/2025,1/16/2025,1/17/2025,1/17/2025,1/22/2025,1/23/2025,1/24/2025,1/27/2025,1/28/2025,1/30/2025,2/3/2025,2/7/2025,2/13/2025,2/14/2025,2/18/2025,2/19/2025,2/24/2025,2/25/2025,2/26/2025,2/27/2025,2/28/2025,3/3/2025,3/24/2025,3/25/2025,4/7/2025,4/8/2025,4/9/2025,3/7/2025,3/17/2025,3/18/2025,3/19/2025,3/20/2025,4/10/2025,4/12/2025,4/16/2025,4/14/2025,4/16/2025,5/1/2025,5/13/2025,5/14/2025,5/27/2025,5/28/2025,5/28/2025,,,,,6/4/2025,6/4/2025,6/5/2025,6/5/2025,6/6/2025,6/9/2025,6/10/2025,6/10/2025,6/11/2025,6/11/2025,6/12/2025,6/13/2025,6/13/2025,6/13/2025,6/16/2025,6/16/2025,6/17/2025,6/17/2025,6/18/2025,6/20/2025,6/21/2025,6/23/2025,6/24/2025,6/26/2025,6/30/2025,7/1/2025,7/2/2025,7/7/2025,7/9/2025,7/11/2025,7/14/2025,7/16/2025,7/21/2025,7/22/2025,7/22/2025,7/24/2025,7/30/2025,7/31/2025,8/1/2025,8/4/2025,8/4/2025,8/5/2025,8/5/2025,8/7/2025,8/7/2025,8/8/2025,8/8/2025,8/8/2025,8/12/2025,8/13/2025,8/14/2025,8/14/2025,7/23/2025,8/13/2025,8/19/2025,8/19/2025,8/20/2025,8/25/2025,8/26/2025,8/28/2025,9/9/2025,9/9/2025,9/12/2025,9/16/2025,,,,,,,,
# 134,2444,Active,8/12/2024,8/29/2024,8/13/2024,8/13/2024,8/13/2024,8/14/2024,8/15/2024,8/16/2024,8/16/2024,8/19/2024,8/19/2024,8/20/2024,8/20/2024,8/20/2024,8/21/2024,8/21/2024,8/21/2024,8/22/2024,8/22/2024,8/22/2024,8/23/2024,8/26/2024,8/26/2024,8/27/2024,8/27/2024,8/27/2024,8/28/2024,8/28/2024,9/4/2024,9/5/2024,9/6/2024,9/9/2024,9/11/2024,9/12/2024,9/13/2024,9/16/2024,9/17/2024,9/18/2024,9/19/2024,9/20/2024,9/23/2024,9/24/2024,9/25/2024,9/26/2024,9/30/2024,10/1/2024,10/3/2024,10/7/2024,11/6/2024,11/12/2024,11/14/2024,11/15/2024,1/31/2025,11/20/2024,11/21/2024,12/12/2024,2/6/2025,2/9/2025,3/18/2025,2/26/2025,3/14/2025,3/16/2025,3/25/2025,3/28/2025,4/8/2025,4/9/2025,4/9/2025,,,,,4/16/2025,4/16/2025,4/17/2025,4/17/2025,4/18/2025,4/21/2025,4/22/2025,4/22/2025,4/23/2025,4/23/2025,4/24/2025,4/25/2025,4/25/2025,4/25/2025,4/28/2025,4/28/2025,4/29/2025,4/29/2025,4/30/2025,5/1/2025,5/2/2025,5/6/2025,5/7/2025,5/8/2025,5/12/2025,5/13/2025,5/14/2025,5/15/2025,5/16/2025,5/29/2025,5/20/2025,5/21/2025,5/31/2025,6/3/2025,6/5/2025,6/6/2025,6/9/2025,6/10/2025,6/10/2025,6/11/2025,6/11/2025,7/22/2025,6/12/2025,6/15/2025,6/15/2025,6/15/2025,6/16/2025,6/25/2025,7/5/2025,7/23/2025,7/24/2025,7/28/2025,5/30/2025,6/4/2025,7/29/2025,7/29/2025,7/30/2025,7/31/2025,7/31/2025,8/5/2025,8/7/2025,8/18/2025,8/19/2025,,,,,,,,,
# aero -> instr -> forms?
# 131,2519,Active,2/24/2025,2/24/2025,2/25/2025,2/25/2025,2/25/2025,2/26/2025,2/27/2025,2/28/2025,2/28/2025,3/3/2025,3/3/2025,3/4/2025,3/4/2025,3/4/2025,3/5/2025,3/5/2025,3/5/2025,3/6/2025,3/6/2025,3/6/2025,3/7/2025,3/10/2025,3/10/2025,3/11/2025,3/11/2025,3/11/2025,3/12/2025,3/12/2025,3/13/2025,3/14/2025,3/17/2025,3/18/2025,3/21/2025,3/22/2025,3/24/2025,3/24/2025,3/25/2025,3/26/2025,4/29/2025,3/28/2025,3/31/2025,4/1/2025,4/2/2025,4/3/2025,4/4/2025,4/21/2025,,4/30/2025,5/19/2025,5/29/2025,6/3/2025,6/6/2025,8/14/2025,6/16/2025,6/17/2025,6/18/2025,6/23/2025,7/9/2025,7/15/2025,7/10/2025,7/16/2025,7/17/2025,7/29/2025,8/5/2025,9/4/2025,9/9/2025,9/10/2025,9/11/2025,9/13/2025,9/15/2025,9/16/2025,9/17/2025,9/17/2025,9/18/2025,9/18/2025,9/19/2025,9/22/2025,9/23/2025,9/23/2025,9/24/2025,9/24/2025,9/25/2025,9/26/2025,9/26/2025,9/26/2025,9/29/2025,9/29/2025,9/30/2025,9/30/2025,10/1/2025,10/2/2025,10/2/2025,10/3/2025,10/3/2025,10/6/2025,10/7/2025,10/7/2025,10/8/2025,10/9/2025,10/10/2025,11/5/2025,10/14/2025,10/14/2025,11/6/2025,11/11/2025,11/17/2025,11/18/2025,11/19/2025,,,,,,,,,,,,,,,,11/11/2025,11/12/2025,,,,,,,,,,,,,,,,,,


import datetime
from datetime import date, timedelta, datetime
from collections import deque
import time
import sys
from collections import defaultdict
from eventList import getActivityTime, Event
from stuAndInsrtr import FlightStudent, Instructor
from resources import Classroom, Utd, Oft, Vtd, Mr, Aircraft, Sim
import csv
import pandas as pd
import random
import matplotlib.pyplot as plt
import os
    
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


def class_in_progress(event, classrooms):
    for c in classrooms:
        if event == classrooms[c][1]:
            capacity_index = classrooms[c][2]
            capacity = classrooms[c][3][capacity_index]
            if capacity < c.capacity:
                return c
    return 99

# maybe 
def forms():
    pass

# IMPORTANT: how to keep track of how many students in each training block? Should we make them classes? Because we 
#            need to look at all the counts to decide where to place students after they complete contacts, and then 
#            also for scheduling for forms (need two students and two instructors)
# My opinion:
# 1) we need a function that keeps track of resources and their scheduling 

# SIMULATION LOGIC 
def run_simulation(students, instructors, class_up_size, percent_aero):
    #students, day, instructors, utd, oft, vtd, mr, aircraft, classroom, syllabus
    # look at line 437
    counter = 0 # turning off infinite loop until simulation works

    # run the loop for the amount of days
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


# daytime_hours = 11 ## 7 to 6
# nighttime_hours = 5
# instructors = 40
instructor_rate = 0.9
instructor_daily_hours = 12

def schedule_one_day(students, day, instructors, utd, oft, vtd, mr, aircraft, classroom, syllabus1, syllabus2):# grndSchool, contacts, aero, inst, forms, capstone):
    # events that will be attempted to schedule for each student
    events_to_attempt = []
    successfull_events = []

    students = students = sorted(
    students,
    key=lambda s: s.days_since_last_event or -1,  # None-safe
    reverse=True
)
    print([s.days_since_last_event for s in students])


    for s in students:
        # s.daily_events_done = 0  # unsure if I need this
        if s.completion_date is None:
            if s.days_since_last_event >= 15:
                events_to_attempt.append((s,"warmup flight"))
            else:

                #get the index of the block and event
                block, event = s.next_event()
                
                # get the event from the sylllabus
                syllabus = syllabus1
                if s.syllabus_type == 2:
                    syllabus = syllabus2
                nxt = syllabus[block][event]
            
                events_to_attempt.append((s,nxt))
    # print(events_to_attempt)

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
    # format is Aircraft Object: [Daily Hours Availible, Night Hours Availible, Total uses that day]
    aircraft_hours = {ac: [Aircraft.daytime_hours, Aircraft.nighttime_hours, 0] for ac in working_aircraft}

    # format object: [hours, event, current capacity check, [capacity_event_one, capacity_event_two, etc...]]
    classroom_hours_events = {c: [Classroom.daily_hours, None, -1, [0, 0, 0, 0,0,0,0,0,0]] for c in classroom}

    # instructors now
    # want to leave these as objects because we will need to check their quals later on and check onwings 
    ## these are objects where the mapping is Object: hours ex. UTD object: 17.5
    instructors_available = [instructor for instructor in instructors if random.random() > Instructor.failure_rate]
    instructor_hours = {instructor: Instructor.daily_hours for instructor in instructors_available}

    # looking at student and the event they are scheduled for
    for s, ev in events_to_attempt:
        #getting how long the event it. 
        if ev == "warmup flight":
            needed_time = 2
            needed_resource = "aircraft"
        else:
            needed_time = ev.activity_time
            needed_resource = ev.resource

        if needed_resource == "classroom":
            helper = 0
            fate = class_in_progress(ev, classroom_hours_events)
            if fate != 99:
                successfull_events.append([s,ev, str(day), str(fate) + " Class: " + str(classroom_hours_events[fate][2]) + " Student: " + str(classroom_hours_events[fate][3][classroom_hours_events[fate][2]])])
                s.event_complete(day)
                classroom_hours_events[fate][3][classroom_hours_events[fate][2]] += 1
                helper = 1
            else:
                for c in classroom_hours_events: # classroom is a list of classroom objects 
                # 1) check if the event is already assigned to a classroom
                #   If it is...
                #   a) and there is space in the class, schedule the student and dont need to play around with the classroom's hours, just its current_num
                #   b) if there is no space, go check if another classroom is available
                # 2) if it isn't, then just assign it to a classroom if possible, and update hours and the classroom's current_num
                    if needed_time <= classroom_hours_events[c][0] or str(ev) == "IN1411/IN1412/IN1413A" or str(ev) == "NA1105/NA1106":
                        classroom_hours_events[c][0] -= needed_time
                        classroom_hours_events[c][1] = ev
                        capacity_index = classroom_hours_events[c][2]
                        classroom_hours_events[c][3][capacity_index] = 1
                        classroom_hours_events[c][2] += 1
                        successfull_events.append([s,ev, str(day), str(c) + " Class: " + str(classroom_hours_events[c][2]) + " Student: " + str(classroom_hours_events[c][3][classroom_hours_events[c][2]])])
                        classroom_hours_events[c][3][classroom_hours_events[c][2]] += 1
                        s.event_complete(day)
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
                    successfull_events.append([s,ev, str(day), u])
                    s.event_complete(day)
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
                    successfull_events.append([s,ev, str(day), o])
                    s.event_complete(day)
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
                    successfull_events.append([s,ev, str(day), v])
                    s.event_complete(day)
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
                    mr_hours[m] -= (needed_time + Sim.break_time)
                    # schedule the student
                    successfull_events.append([s,ev, str(day), m])
                    s.event_complete(day)
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

            can_be_night = False

            if ev != "warmup flight" and ev.block == "instruments":
                ## then it can be completed at night
                can_be_night = True

            if can_be_night and s.night_hours < 5:
                for ac in aircraft_hours:
                    instructor_found = 0
                    if needed_time <= aircraft_hours[ac][1] and aircraft_hours[ac][2] < Aircraft.uses_per_day:
                        for inst in instructor_hours:
                            if needed_time <= instructor_hours[inst]:
                                aircraft_hours[ac][1] -= (needed_time + Aircraft.break_time)
                                instructor_hours[inst] -= (needed_time + Instructor.break_time)
                                successfull_events.append([s,ev, str(day), "night",ac,inst])
                                s.event_complete(day)
                                aircraft_hours[ac][2] += 1
                                aircraft_found = 1
                                instructor_found = 1
                                s.night_hours += needed_time
                                break
                        if instructor_found == 1:
                            break
            
            if aircraft_found == 1:
                continue

            # was getting an error so changed ev.names to ev
            running_out_of_events = ev == "I4490" or ev == "N4101" or ev == "FAM4601"

            if aircraft_found == 0 and s.night_hours < 5 and running_out_of_events:
                s.days_since_last_event += 1
                s.total_wait_time += 1
                break


            for ac in aircraft_hours:
                instructor_found = 0
                if needed_time <= aircraft_hours[ac][0] and aircraft_hours[ac][2] < Aircraft.uses_per_day:
                    for inst in instructor_hours:
                        if needed_time <= instructor_hours[inst]:
                            aircraft_hours[ac][0] -= (needed_time + Aircraft.break_time)
                            instructor_hours[inst] -= (needed_time + Instructor.break_time)
                            successfull_events.append([s,ev, str(day), "day",ac,inst])
                            s.event_complete(day)
                            aircraft_hours[ac][2] += 1
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
            
    


# reads in events from a csv file and makes event objects per block and puts that in a list
def make_events(file_path, block):
    # keep track of each event's activity time
    activity_time_dict = getActivityTime()
    events = []
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

# makes a list of current students in the syllabus from a csv file 
'''
IMPORTANT ASSUMPTION BEING MADE:
If there is a gap (gap = event with no date listed with completed events on either side of it), we are going
to assume that that event was completed and that its date of completion was just not listed (some TSHARP error).
So to figure out wihch block a student is in and which event they need to complete next, we are just looking at their
most recent date, and going from there. 
'''
def load_students(file_path):
    student_list = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            status = row["Status"].strip().lower()
            student_id = row["Name"]
            class_id = row["Class"]

            # Find earliest completed event date as start_date
            start_date = None
            last_date = None
            last_event = None

            for key, value in row.items():
                if key in ("Name", "Class", "Status"):
                    continue
                if value.strip():
                    date = datetime.strptime(value.strip(), "%m/%d/%Y").date()

                    if start_date is None or date < start_date:
                        start_date = date
                    if last_date is None or date > last_date:
                        last_date = date
                        last_event = key
                        print(last_event)

            # Create student object
            student = FlightStudent(student_id, class_id, start_date)

            # gets tricky here because need to check if they have done aero
            sys1 = FlightStudent.syllabus1
            sys2 = FlightStudent.syllabus2

            # Mark completed students
            if status == "complete":
                student.completion_date = last_date
                student.completed_blocks = [1, 1, 1, 1, 1, 1, 1]
                # calculate syllabus_type
                date_str1 = row["FAM4703"]  # this could also be "F4290" (last forms event)
                date_str2 = row["FAM4601"]
                # Convert to date objects
                d1 = datetime.strptime(date_str1, "%m/%d/%Y").date()
                d2 = datetime.strptime(date_str2, "%m/%d/%Y").date()
                # Compare
                if d1 < d2:
                    student.syllabus_type = 2
            else:
                # active students
                # Initialize timeline fields
                student.last_completed_event_date = last_date
                student.days_since_last_event = (datetime.today().date() - student.last_completed_event_date).days
                print("last comp event: ", last_event)
                print(last_date)
                found = False 
                for block_index, block in enumerate(sys1):
                    for event_index, event in enumerate(block):
                        if last_event in event.name:
                            student.current_block = block_index
                            student.next_event_index = event_index + 1
                            founds = True
                            break
                    if found:
                        break
                
                # Figure out which syllabus the student is using
                # For syllabus 1:
                # 0 = sys grnd
                # 1 = contacts
                # 2 = instr grnd
                # 3 = instr
                # 4 = aero
                # 5 = forms
                # 6 = capstone
                print("current block: ", student.current_block)
                if student.current_block in (2,3):
                    if not row["FAM4703"].strip():     # if not complete with aero
                        student.syllabus_type = 1
                    else:
                        student.syllabus_type = 2
                        student.current_block += 1

                if student.current_block in (4,5):
                    if not row["FAM4601"].strip():     # if not complete with instruments
                        student.syllabus_type = 2
                        student.current_block -= 2 

                for i in range(0, student.current_block):
                    student.completed_blocks[i] = 1
            
            # Go through and update the completed_dates list
            end_events1 = {0:"G0102", 1:"FAM4501", 2:"NA1190", 3:"FAM4601", 4:"FAM4703", 5:"F4290", 6:"CS4290"}
            end_events2 = {0:"G0102", 1:"FAM4501", 2:"FAM4703", 3:"F4290", 4:"NA1190", 5:"FAM4601", 6:"CS4290"}
            # sometimes they forget to put the completion date if the last two events take place on the same day...
            almost_end_events1 = {0:"G0290", 1:"FAM4490", 2:"NA1106", 3:"N4101", 4:"FAM4702", 5:"F4104", 6:"CS4102"}
            almost_end_events2 = {0:"G0290", 1:"FAM4490", 2:"FAM4702", 3:"F4104", 4:"NA1106", 5:"N4101", 6:"CS4102"}
            for i, block in enumerate(student.completed_blocks):
                if student.syllabus_type == 1:
                    if block == 1:
                        print(1)
                        print(student.student_id)
                        print(student.completed_blocks)
                        date = row[end_events1[i]]
                        if date == '':
                            date = row[almost_end_events1[i]]
                        print(date)
                        student.completed_dates[i] = datetime.strptime(date, "%m/%d/%Y").date()
                if student.syllabus_type == 2:
                    if block == 1:
                        print(2)
                        print(student.student_id)
                        print(student.completed_blocks)
                        date = row[end_events2[i]]
                        if date == '':
                            date = row[almost_end_events2[i]]
                        print(date)
                        student.completed_dates[i] = datetime.strptime(date, "%m/%d/%Y").date()

            student_list.append(student)
    FlightStudent.student_id = len(student_list)+1
    return student_list

#write now, don't care if they're status is 'suspended'. As long as they have something, we will count them as qualified
def load_instructors(file_path):
    instructor_list = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["Name"]

            # Check the two columns we care about
            section_lead = row.get("T_6B_Section_Lead", "").strip()
            formation = row.get("T_6B_Formation", "").strip()

            # True if either column has any letter/value
            is_section_lead =  bool(section_lead)
            is_formation = bool(formation)

            instructor = Instructor(name, is_section_lead, is_formation)
            instructor_list.append(instructor)
    return instructor_list

# this function will be called every monday
# Note: make sure dates can be compared (same format)
# This function creates a list of new students that will be added (.extend) to the student list
# It will be called in the run_simulation function
def students_starting_weekly(file_path, date):
    new_students = []

    # Ensure we are working with a date object
    if isinstance(date, datetime):
        date = date.date()
    elif not isinstance(date, date_type):
        raise TypeError("date must be a datetime.date or datetime.datetime")

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            csv_date = datetime.strptime(
                row["Date"].strip(), "%d-%b-%y"
            ).date()

            if csv_date == date:
                num_students = int(row["Number_of_Students_Classing_Up"])
                class_id = row["class_id"]

                for i in range(num_students):
                    FlightStudent.student_id += 1
                    new_students.append(FlightStudent(FlightStudent.student_id, class_id, date))
    return new_students
    



def main():
    # Resources
    classrooms = "classroom"
    utd_sims = "utd"
    oft_sims = "oft"
    vtd_sims = "vtd"
    mr_sims = "mr"
    aircrafts = "aircraft"

    # going to running run_simulation function multiple times based on different class sizes

    # Initialize a list of event objects for each block
    sysGrndSchoolEvents = make_events(os.path.join("data", "sysGrnd.csv"), "system ground")
    # print("sys grnd: ", sysGrndSchoolEvents)
    # FAM1301, FAM4101, FAM4102, FAM4103, FAM4104, FAM4303, FAM4304 are the required onwing events
    contactsEvents = make_events(os.path.join("data", "contacts.csv"), "contacts")
    aeroEvents = make_events(os.path.join("data","aero.csv"), "contacts")
    instrGrndSchoolEvents = make_events(os.path.join("data", "instrGrnd.csv"), "instrument ground")
    instrumentsEvents = make_events(os.path.join("data", "instr.csv"), "instruments")
    formsEvents = make_events(os.path.join("data", "forms.csv"), "forms")
    capstoneEvents = make_events(os.path.join("data", "capstone.csv"), "capstone")
    
    # syllabus combinations (can add more)
    syllabus1 = [sysGrndSchoolEvents, contactsEvents, instrGrndSchoolEvents, instrumentsEvents, aeroEvents, formsEvents, capstoneEvents]
    syllabus2 = [sysGrndSchoolEvents, contactsEvents, aeroEvents, formsEvents, instrGrndSchoolEvents, instrumentsEvents, capstoneEvents]

    # Resources
    classrooms_list = [Classroom(f"CL{i+1}") for i in range(6)]
    utd_sims_list = [Utd(f"UTD{i+1}") for i in range(6)]
    oft_sims_list = [Oft(f"OFT{i+1}") for i in range(6)]
    vtd_sims_list = [Vtd(f"VTD{i+1}") for i in range(18)]
    mr_sims_list = [Mr(f"MR{i+1}") for i in range(2)]
    aircraft_list = [Aircraft(f"AC{i+1}") for i in range(18)]
    # Run the simulation
    # run_simulation(students, syllabus)

    FlightStudent.syllabus1 = syllabus1
    FlightStudent.syllabus2 = syllabus2

    default_value=10

    students = load_students((os.path.join("students", "current_students.csv")))
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
        if i % 10 == 1:
            new_student.syllabus_type = 2
        students.append(new_student) # **IMPORTANT: change what i is being divided by to control class size (i.e. how many people are starting each week)


    instructors = load_instructors(os.path.join("instructors", "instructor_data.csv"))

    result = []

    user_input = input("Enter a number of days (default 10): ")

    try: 
        value = int(user_input)
    except ValueError:
        value = default_value

    if value > 365:
        value = 365

    # for i in syllabus:
    #     print(i)

    for i in range(value):
        current = date.today() + timedelta(days=i)
        schedule = schedule_one_day(students, current, instructors, utd_sims_list, oft_sims_list, vtd_sims_list, mr_sims_list, aircraft_list, classrooms_list, syllabus1, syllabus2)
        result.append(schedule)

    for i in result:
        for j in i:
            print(j)



    student_wait_times = []
    for s in students:
        # dates = sorted(s.completed_dates)
        dates = sorted(s.completed_dates, key=lambda d: (d is None, d))
        date_to_compare = s.start_date
        wait_times = []

        for i in dates:
            if i is None:
                wait_times.append(None)
                # do NOT update date_to_compare
                continue
            wait_times.append((i-date_to_compare).days)
            date_to_compare = i

        student_wait_times.append([f"Student {s.student_id}", wait_times, f"night hours: {s.night_hours}"])

    print("Wait times for each student by block")
    for i in student_wait_times:
        print(i[0],i[1],i[2], "completion date:",s.completion_date )


if __name__ == "__main__":
    main()
