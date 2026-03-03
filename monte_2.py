# @author Anuj Sirsikar and Timothy Kedrowski and Lauren Leckelt
# runs the simulation a lot more times to get a better idea of the true numbers (average of many iterations)

## Feel free to contact for questions: LLECKELT@GMAIL.COM


import datetime
from datetime import date, timedelta, datetime, date as date_type
from collections import deque
import time
import sys
from collections import defaultdict
from eventList import getActivityTime, Event, is_on_wing_needed
from stuAndInsrtr import FlightStudent, Instructor
from resources import Classroom, Utd, Oft, Vtd, Mr, Aircraft, Sim
import csv
import pandas as pd
import random
import matplotlib.pyplot as plt
import os
import tkinter as tk
import numpy as np 
import copy
import json
from matplotlib.patches import Patch
from holiday_loader import load_holiday_ranges


SYLLABUS_BLOCKS = {
        1: ["Ground School", "Contacts", "Instrument Ground", "Instruments", "Aero", "Forms", "Capstone" ],
        2: ["Ground School", "Contacts", "Aero", "Forms", "Instrument Ground", "Instruments", "Capstone" ],
        3: ["Ground School", "Contacts", "Instrument Ground", "Instruments", "Forms", "Aero", "Capstone" ],
        4: ["Ground School", "Contacts", "Aero", "Instrument Ground", "Instruments", "Forms", "Capstone" ]
    }

START_DATE = datetime.strptime("2025-11-23", "%Y-%m-%d").date()
# START_DATE = date.today()


# HELPER FUNCTIONS
def is_valid_day(day):
    # not a weekend, 96 (long weekend), or a holiday period
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
    # holiday_ranges = load_holiday_ranges("holidays.csv")

    for dates in holiday_ranges:
        if (dates["start"]<= day <= dates["end"]):
            return False
    return True


def current_active_students(students):
    count = 0
    for s in students:
        if None in s.completed_dates:
            count+=1

    return count


def clear_insts(insts):
    for i in insts:
        i.on_wings = []

def load_leave_ranges(csv_path):
    """
    Returns:
    {
        1: [(start, end), (start, end), ...],
        2: [(start, end), (start, end), ...]
    }
    """
    leave_ranges = {}

    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue

            label = row[0].strip().lower()  # "holiday leave 1"
            start = datetime.strptime(row[1].strip(), "%Y-%m-%d").date()
            end = datetime.strptime(row[2].strip(), "%Y-%m-%d").date()

            number = int(label.split()[-1])  # extracts 1 or 2

            # Append instead of overwrite
            leave_ranges.setdefault(number, []).append((start, end))

    return leave_ranges

def is_in_leave_range(leave_ranges, leave_number, check_date):
    """
    Returns True if the given date falls in ANY range
    for that leave number (across all fiscal years)
    """
    if leave_number not in leave_ranges:
        return False

    for start, end in leave_ranges[leave_number]:
        if start <= check_date <= end:
            return True

    return False


# SIMULATION LOGIC 
def run_simulation(sim_start_date, days, percent_aero, students, instructors, utd, oft, vtd, mr, aircraft, classroom, syllabus1, syllabus2, syllabus3, syllabus4, class_size_type, class_size, monthly_class_size):
    # sim_start_date = date(2025, 11, 24)   # year, month, day
    current_day = sim_start_date
    reset_on_wing()
    clear_insts(instructors)
    
    
    # run the loop for the amount of days
    while days > 0:  

        ## adding this now to account for every other week.
        weeks_since_start = (current_day - sim_start_date).days // 7 + 1

        if students is None:
            break 
        if is_valid_day(current_day):
            # print("it is a valid day")
            # if it is a monday
            # added it so that it only classes up on first monday and every other monday after that
            if current_day.weekday() == 0 and weeks_since_start % 2 == 0:
                # print("it is a monday")
                if class_size_type == "fixed":
                    new_students = []

                    increase = class_size
                    if max_250:
                        count = current_active_students(students)
                        if count + increase > 250:
                            increase = 0

                    for i in range(increase):
                        FlightStudent.student_id += 1
                        new_student = FlightStudent(FlightStudent.student_id, i//8, current_day)
                        new_student.imported = False
                        new_students.append(new_student)

                elif class_size_type == "FY":
                    new_students = students_starting_weekly(os.path.join("students", "weekly_class_up_fy26.csv"), current_day)

                # # # if the class size is the one with the monthly amounts
                else: 
                    new_students = []
                    ## add the monthly class up numbers here
                    month_index = current_day.month -1
                    class_up_num = monthly_class_size[month_index]

                    for i in range(class_up_num):
                        FlightStudent.student_id += 1
                        new_student = FlightStudent(FlightStudent.student_id, i//8, current_day)
                        new_student.imported = False
                        new_students.append(new_student)


                # assign new_students to a syllabus 
                for stu in new_students:
                    if random.random() <= percent_aero:
                        stu.syllabus_type = 2
                students.extend(new_students)
            schedule_one_day(current_day, students, instructors, utd, oft, vtd, mr, aircraft, classroom, syllabus1, syllabus2, syllabus3, syllabus4)
            # keep track of resource use and students here (print it out or something)
        # else:
        #     print(current_day)
        days -= 1
        current_day += timedelta(days=1)

        # for s in students:
        #     print(s.block_wait_times)


    ## format is list: schedule, list: students    
    return students 
    # return result, students

instructor_rate = 0.9
instructor_daily_hours = 12


# pair up students
def pair_students(queue: dict):
    pairs = []
    used = set()

    # print(queue.items())
    for s, ev in queue.items():
        
        if s.has_partner() and s.get_partner() in queue and s.get_partner() not in used:
            # if queue[s] != queue[s.get_partner()]:
                # print("not scheduled for the same event!!")
            # print("already has partner")
            used.add(s)
            used.add(s.get_partner())
            pairs.append((s, s.get_partner(), ev, queue[s.get_partner()]))
        elif s.has_partner():
            continue
        elif not s.has_partner():
            if s in used:
                continue

            for t, tev in queue.items():
                if t in used or t is s or t.has_partner():
                    continue

                if tev == ev:
                    # print("assigning new partner")
                    # print(ev)
                    used.add(s)
                    used.add(t)
                    s.assign_partner(t)
                    #pairs.append((s, t, ev, queue[s.get_partner()]))
                    pairs.append((s, t, ev, tev))
                    break
    return pairs



def schedule_partner_sim(day, s, ev, used_set, hours, needed_time, sim_type):
    if s.has_partner():
        available_sims = []
        for o in hours:
            if needed_time <= hours[o]:
                available_sims.append(o)
                if len(available_sims) == 2:
                    break

        if len(available_sims) == 2:
            for o in available_sims:
                hours[o] -= (needed_time + Sim.break_time)

            partner = s.get_partner()

            s.event_complete(day)
            partner.event_complete(day)
            s.schedule_failed = False
            partner.schedule_failed = False
            used_set[s] = True
            used_set[partner] = True
            

def schedule_sim(day, s, ev, sim_hours, needed_time, sim_type):
    for o in sim_hours:
        if needed_time <= sim_hours[o]:
            sim_hours[o] -= (needed_time + Sim.break_time)
            # schedule the student
            s.event_complete(day)
            s.schedule_failed = False
            break





def class_in_progress(event, classrooms):
    ## check every classroom
    for c in classrooms:
        ## check the events list in each classroom to see if its present
        if event in classrooms[c]["active_events"]:
            if classrooms[c]["active_events"][event] < c.capacity:
                return c
            # if the event is maxed out then just remove it
            else:
                key = str(event) +"_"+ str(classrooms[c]["string_diff"])
                classrooms[c]["string_diff"] += 1
                classrooms[c]["active_events"][key] = classrooms[c]["active_events"][event]
                del classrooms[c]["active_events"][event]

    return None

def select_classroom(event, needed_time, classrooms):
    class_exists = class_in_progress(event, classrooms)

    if class_exists is not None:
        return {"classroom": class_exists, "state": "existing_class"}

    else:
        for c in classrooms:
            ## if this is the event for the day then it exceeds the classroom hours anyway but itll be scheduled in one day
            exception = (str(event) in ["IN1411/IN1412/IN1413A", "NA1105/NA1106"])

            ## check to see if there is enough availible time. or if it is an empty classroom take the whole day with the above exception
            if classrooms[c]["hours"] >= needed_time or (classrooms[c]["hours"] == Classroom.daily_hours and exception):
                return {"classroom": c, "state": "new_class"}
            
    return None

def reset_on_wing():
    Instructor.on_wing_start = 0

def get_on_wing(instructors):

    selected_inst = None
    n = len(instructors)

    for i in range(n):
        index = (Instructor.on_wing_start + i) % n

        if len(instructors[index].on_wings) < 4:
            selected_inst = index
            break

    Instructor.on_wing_start = (Instructor.on_wing_start + 1) % len(instructors)
    return selected_inst
    


def schedule_one_day(day, students, instructors, utd, oft, vtd, mr, aircraft, classroom, syllabus1, syllabus2, syllabus3, syllabus4):# grndSchool, contacts, aero, inst, forms, capstone):
    # print("------------ NEW DAY --------------", day)
    

    daily_student_distribution = {
            "Ground School": 0, 
            "Contacts": 0, 
            "Aero": 0, 
            "Instrument Ground": 0, 
            "Instruments": 0, 
            "Forms": 0, 
            "Capstone" : 0
        }
    
    # events that will be attempted to schedule for each student
    events_to_attempt = []

    students = sorted(
        students,
        key=lambda s: s.days_since_last_event if s.days_since_last_event is not None else 0,
        reverse=True
    )

    # make this a dictionary where the key is a student and the value is their next event 
    forms_partner_queue = {}
    capstone_partner_queue = {}

    # used to track students that have already been scheduled
    already_used = {}

    for s in students:


        # just assume that each kid starts out with the assumption that they will not be scheduled 
        s.schedule_failed = True    

        # I know that this is repetitive 
        current_block = s.get_block()

        if current_block == "complete":
            continue

        if current_block in daily_student_distribution:
            daily_student_distribution[current_block] += 1
        else:
            raise ValueError(f"Unknown block: {current_block}")


        #if they are not done then check if they need a warmup event. then assign the student and their event to the list.
        on_leave = is_in_leave_range(leave_ranges, s.leave_period, day)

        if s.completion_date is None and not on_leave:
            if s.days_since_last_event >= 15:
                events_to_attempt.append((s,"warmup flight"))
                already_used[s] = False
            else:

                #get the index of the block and event
                block, event = s.next_event()
                
                # get the event from the sylllabus
                syllabus = [syllabus1, syllabus2, syllabus3, syllabus4][s.syllabus_type-1]

                nxt = syllabus[block][event]
            
                if nxt.block == "contacts" and s.on_wing == None:
                    new_on_wing = get_on_wing(instructors)

                    if new_on_wing is not None:
                        # print("scheduled new on wing", s,instructors[new_on_wing], nxt.block)
                        s.on_wing = new_on_wing                   
                        instructors[new_on_wing].on_wings.append(s)

                elif nxt.block != "contacts" and s.on_wing is not None:
                    # print("deleted on wing", s, instructors[s.on_wing], nxt.block,s.syllabus_type)
                    instructors[s.on_wing].on_wings.remove(s)
                    s.on_wing = None

                # if s.on_wing is not None and nxt.block != "contacts":
                #     print("not none", nxt.block)


                events_to_attempt.append((s,nxt))

                already_used[s] = False


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
    # aircraft_hours = {ac: [Aircraft.daytime_hours, Aircraft.nighttime_hours, 0] for ac in working_aircraft}

    aircraft_data = { 
        ac: {

            "day_hours": Aircraft.daytime_hours,
            "night_hours": Aircraft.nighttime_hours,
            "uses": 0
        }
        for ac in working_aircraft
    }


    classroom_data = {
        c: {
            "hours": Classroom.daily_hours,
            ## dictionary of events where the format is name: capacity
            "active_events":{},
            "string_diff": 0
        }
        for c in classroom
    }

    

    # Make the partner pairs for the day
    for s, ev in events_to_attempt:

        

        if ev == "warmup flight":
            continue
        if ev.block == "forms":
            forms_partner_queue[s] = ev
        elif ev.block == "capstone":
            capstone_partner_queue[s] = ev

    pair_students(forms_partner_queue)        # we don't actaully care about the pairs, as long as they exist
    pair_students(capstone_partner_queue)
    # print(forms_pairs)

    # print("capstone pairs",day)
    # for s in capstone_partner_queue:
        # print("s:", s, "partner: ", s.get_partner(), capstone_partner_queue[s])


    # instructors now
    # want to leave these as objects because we will need to check their quals later on and check onwings 
    ## these are objects where the mapping is Object: hours ex. UTD object: 17.5
    instructors_available = [instructor for instructor in instructors if random.random() > Instructor.failure_rate]
    # instructor_hours = {instructor: [Instructor.daily_hours,0] for instructor in instructors_available}

    instructor_data = { instructor:
                       {
                           "hours": Instructor.daily_hours,
                           "uses": 0,
                           "contact flights": 0
                       }
                       for instructor in instructors_available}


    # re-sort the students based on which block has the most students
    # blocks are sorted by most amount of students to least 
    ordered_blocks = sorted(daily_student_distribution, key=daily_student_distribution.get, reverse=True)
    
    # Build a quick lookup for block priority
    block_priority = {block: i for i, block in enumerate(ordered_blocks)}


    # Not sure which one is better

    # this one does over ten sorted by block and under ten sorted by block 
    # events_to_attempt.sort(
    #     key=lambda item: (
    #         item[0].days_since_last_event < 10,
    #         -item[0].days_since_last_event,
    #         block_priority.get(item[0].get_block(), float("inf"))
    #     )
    # )




    ## going to try to integrate it this way. only contacts people who have already failed get moved to front instead of every student
    events_to_attempt.sort(
        key=lambda item: (
            0 if getattr(item[0], "on_wing_event_failed", False)
            else 1 if item[0].days_since_last_event > 10
            else 2,
            -item[0].days_since_last_event,
            block_priority.get(item[0].get_block(), float("inf")),
        )
    )


    # this one does sorted by longest to shortest and then sorted by blck within that queue
    #events_to_attempt.sort(
    #    key=lambda item: (
    #        -item[0].days_since_last_event,
    #        block_priority.get(item[0].get_block(), float("inf"))
    #    )
    #)


    # looking at student and the event they are scheduled for
    for s, ev in events_to_attempt:

        partner_pairs = []
        # if they have already been scheduled. For instance a partner for forms or capstone
        if already_used.get(s, False):
            continue

        #getting how long the event it. 
        if ev == "warmup flight":
            needed_time = 2
            needed_resource = "aircraft"
        else:
            needed_time = ev.activity_time
            needed_resource = ev.resource

        if needed_resource == "classroom":
            classroom_result = select_classroom(ev, needed_time, classroom_data)

            if classroom_result is not None:
                c = classroom_result["classroom"]

                if classroom_result["state"] == "existing_class":
                    ## increase the current number scheduled
                    classroom_data[c]["active_events"][ev] += 1

                ## decrease the number of hours and add a student to the class
                else:
                    classroom_data[c]["hours"] -= needed_time
                    classroom_data[c]["active_events"][ev] = 1
                    # classroom_data[c]["uses"] += 1

                s.event_complete(day)
                s.schedule_failed= False
                already_used[s] = True

                
            
        elif needed_resource == "utd":
            schedule_sim(day, s, ev, utd_hours, needed_time, "utd")

        elif needed_resource == "oft":
            if ev.block == 'forms':
                schedule_partner_sim(day, s, ev, already_used, oft_hours, needed_time, "oft")
            elif ev.block == 'capstone':
                schedule_partner_sim(day, s, ev,  already_used, oft_hours, needed_time, "oft")
            else:
                schedule_sim(day, s, ev, oft_hours, needed_time, "oft")

        elif needed_resource == "vtd":
            schedule_sim(day, s, ev, vtd_hours, needed_time, "vtd")
                
        elif needed_resource == "mr":
            if ev.block == 'forms':
                schedule_partner_sim(day, s, ev,  already_used, mr_hours, needed_time, "mr")
            elif ev.block == 'capstone':
                schedule_partner_sim(day, s, ev,  already_used, mr_hours, needed_time, "mr")
            else:
                schedule_sim(day, s, ev, mr_hours, needed_time, "mr")
            
        else: ##aircraft

            instructor_data = dict(
                sorted(
                    instructor_data.items(),
                    key=lambda item: item[1]["hours"],
                    reverse=True
                )
            )

            aircraft_found = 0
            can_be_night = False

            if ev != "warmup flight" and ev.block == "instruments":
                ## then it can be completed at night
                can_be_night = True
            
            # forms
            
            if ev != "warmup flight" and ev.block == "forms":
                if s.has_partner():
                    used = 1
                    if ev.is_double:
                        used=2
                    available_aircraft = []
                    available_instructors = []
                    for ac in aircraft_data:
                        if needed_time <= aircraft_data[ac]["day_hours"] and aircraft_data[ac]["uses"] < Aircraft.uses_per_day:
                            available_aircraft.append(ac)
                            if len(available_aircraft) == 2:
                                break
                    section_lead_found = False
                    formation_q_found = False
                    for inst in instructor_data:
                        if needed_time > instructor_data[inst]["hours"] or instructor_data[inst]["uses"] >= 4:
                            continue  # not enough hours, skip
                        # If we still need a section lead and this instructor is one, take them
                        if inst.section_lead and not section_lead_found:
                            available_instructors.append(inst)
                            section_lead_found = True
                        # Else if we still need a formation-qualified instructor and this instructor is one, take them
                        elif inst.formation_q and not formation_q_found:
                            available_instructors.append(inst)
                            formation_q_found = True
                        # Stop once we have both roles
                        if section_lead_found and formation_q_found:
                            break
                    # print(available_aircraft)
                    # print(available_instructors)
                    if len(available_aircraft) == 2 and len(available_instructors) == 2:
                        for ac in available_aircraft:
                            aircraft_data[ac]["day_hours"] -= (needed_time + Aircraft.break_time)
                            aircraft_data[ac]["uses"] += used
                        for inst in available_instructors:
                            #print(inst)
                            instructor_data[inst]["hours"] -= (needed_time + Instructor.break_time)
                            instructor_data[inst]["uses"] += used
    

                        partner = s.get_partner()

                        partner_pairs.append((s,partner,ev))

                        s.event_complete(day)
                        partner.event_complete(day)
                        s.schedule_failed = False
                        partner.schedule_failed = False
                        already_used[s] = True
                        already_used[partner] = True
                        # print(forms_students)
                        continue
            elif ev != "warmup flight" and ev.block == "capstone":
                if s.has_partner():
                    used = 1
                    if ev.is_double:
                        used = 2
                    available_aircraft = []
                    available_instructors = []
                    for ac in aircraft_data:
                        if needed_time <= aircraft_data[ac]["day_hours"] and aircraft_data[ac]["uses"] < Aircraft.uses_per_day:
                            available_aircraft.append(ac)
                            if len(available_aircraft) == 2:
                                break
                
                    for inst in instructor_data:
                        if needed_time <= instructor_data[inst]["hours"] and instructor_data[inst]["uses"] < 4:
                            available_instructors.append(inst)
                            if len(available_instructors) == 2:
                                    break
                         
                    # print(available_aircraft)
                    # print(available_instructors)
                    if len(available_aircraft) == 2 and len(available_instructors) == 2:
                        for ac in available_aircraft:
                            aircraft_data[ac]["day_hours"] -= (needed_time + Aircraft.break_time)
                            aircraft_data[ac]["uses"] += used
                        for inst in available_instructors:
                            #print(inst)
                            instructor_data[inst]["hours"] -= (needed_time + Instructor.break_time)
                            instructor_data[inst]["uses"] += used
    

                        partner = s.get_partner()

                        partner_pairs.append((s,partner,ev))

                        s.event_complete(day)
                        if partner.current_block > 6:
                            print(partner_pairs)
                            print(partner.current_block, "this is the error")
                        partner.event_complete(day)
                        s.schedule_failed = False
                        partner.schedule_failed = False
                        already_used[s] = True
                        already_used[partner] = True
                        # print(forms_students)
                        continue
            

            #elif ev != "warmup flight" and ev.on_wing == "solo":
            elif ev != "warmup flight" and ev == "FAM4501":
                # solo flight
                aircraft_found = None
                for ac in aircraft_data:
                        if needed_time <= aircraft_data[ac]["night_hours"] and aircraft_data[ac]["uses"] < Aircraft.uses_per_day:
                            aircraft_found = ac
                            break
                if aircraft_found:
                    aircraft_data[ac_found]["day_hours"] -= (needed_time + Aircraft.break_time)
                    s.event_complete(day)
                    s.schedule_failed = False
                    already_used[s] = True
                    aircraft_data[ac_found]["uses"] += 1
                    continue

            elif ev != "warmup flight" and ev.on_wing == "yes":
                ## the student has moved on to day

                ac_found = None
                inst_found = None

                for ac in aircraft_data:
                    if needed_time <= aircraft_data[ac]["day_hours"] and aircraft_data[ac]["uses"] < Aircraft.uses_per_day:
                        ac_found = ac
                        break
                
                
                if s.on_wing is not None and instructors[s.on_wing] in instructor_data and needed_time <= instructor_data[instructors[s.on_wing]]["hours"] and instructor_data[instructors[s.on_wing]]["uses"] < 4 and instructor_data[instructors[s.on_wing]]["contact flights"] < 2:
                    inst_found = instructors[s.on_wing]

                if ac_found and inst_found:
                    aircraft_data[ac_found]["day_hours"] -= (needed_time + Aircraft.break_time)
                    instructor_data[inst_found]["hours"] -= (needed_time + Instructor.break_time)
                    instructor_data[inst_found]["uses"] += 1
                    instructor_data[inst_found]["contact flights"] += 1
                    
                    s.event_complete(day)
                    s.schedule_failed = False
                    already_used[s] = True
                    aircraft_data[ac_found]["uses"] += 1
                    continue
                else:
                    s.on_wing_event_failed = True

            else:
                used = 1
                if ev != "warmup flight" and ev.is_double:
                    used = 2
                if can_be_night and s.night_hours < 3.4:

                    aircraft_found = None
                    inst_found = None
                    for ac in aircraft_data:
                        if needed_time <= aircraft_data[ac]["night_hours"] and aircraft_data[ac]["uses"] < Aircraft.uses_per_day:
                            aircraft_found = ac
                            break
                    
                    for inst in instructor_data:
                        if needed_time <= instructor_data[inst]["hours"] and instructor_data[inst]["uses"] < 4:
                            inst_found = inst
                            break


                    if aircraft_found and inst_found:
                        aircraft_data[aircraft_found]["night_hours"] -= (needed_time + Aircraft.break_time)
                        instructor_data[inst_found]["hours"] -= (needed_time + Instructor.break_time)
                        instructor_data[inst_found]["uses"] += used

                        
                        s.event_complete(day)
                        s.schedule_failed = False
                        already_used[s] = True
                        aircraft_data[aircraft_found]["uses"] += used
                        s.night_hours += needed_time
                        continue
    

                # was getting an error so changed ev.names to ev
                running_out_of_events = (ev == "I4490" or ev == "N4101" or ev == "FAM4601")

                # if the mandatory flight is the event and they were not scheduled
                # if they do not have enough night hours
                # if they are running out of events to get night hours
                if ev == "FAM4601" or (s.night_hours < 5 and running_out_of_events):
                    continue

                
                
                ## the student has moved on to day

                ac_found = None
                inst_found = None

                for ac in aircraft_data:
                    if needed_time <= aircraft_data[ac]["day_hours"] and aircraft_data[ac]["uses"] < Aircraft.uses_per_day:
                        ac_found = ac
                        break
                
                for inst in instructor_data:
                    if needed_time <= instructor_data[inst]["hours"] and instructor_data[inst]["uses"] < 4:
                        if ev != "warmup flight":
                            if ev.block == "contacts" and ev.is_double and instructor_data[inst]["contact flights"] >= 1:      # do we need this??
                                continue
                            elif ev.block == "contacts" and instructor_data[inst]["contact flights"] >= 2:
                                continue
                        inst_found = inst
                        break

                if ac_found and inst_found:
                    aircraft_data[ac_found]["day_hours"] -= (needed_time + Aircraft.break_time)
                    instructor_data[inst_found]["hours"] -= (needed_time + Instructor.break_time)
                    instructor_data[inst_found]["uses"] += used
                    if ev != "warmup flight" and ev.block == "contacts":
                        instructor_data[inst_found]["contact flights"] += used
                    
                    if ev != "warmup flight":
                        s.event_complete(day)
                    else:
                        s.days_since_last_event = 0
                    s.schedule_failed = False
                    already_used[s] = True
                    aircraft_data[ac_found]["uses"] += used
                    continue
                    


    # now deal with students that failed today 
    for s in students:

        if s.schedule_failed and s.get_block() != "complete":
            s.days_since_last_event += 1
            s.total_wait_time += 1
            s.block_wait_times[s.get_block()] += 1

            block,event = s.next_event()
            # get the event from the sylllabus
            syllabus = [syllabus1, syllabus2, syllabus3, syllabus4][s.syllabus_type-1]

            nxt = syllabus[block][event]

            resource = nxt.resource


            s.unscheduled_per_resource[resource] += 1    # need a way to figure out the resource type 

    year_stats = day.year
    if day.month in [11,12]:
        year_stats += 1


    # summary = fiscal_year_stats(year_stats, students, "year")



# FY number format YYYY, list of students
def fiscal_year_stats(year, students, year_or_total):
    started = 0
    completed = 0
    remaining = 0

    year_start = year - 1
    year_total = year + 3

    year_start_date = date(year_start, 11, 1)

    if year_or_total == "year":
        year_end_date = date(year, 10, 31)
    else:
        year_end_date = date(year_total, 10, 31)

    for s in students:
        if s.start_date >= year_start_date and s.start_date <= year_end_date:
            started += 1
        if s.completion_date == None or s.completion_date > year_end_date:
            remaining += 1
        elif s.completion_date >= year_start_date and s.completion_date <= year_end_date:
            completed += 1
    
    return {
        "started": started,
        "completed": completed,
        "remaining": remaining
    }





# reads in events from a csv file and makes event objects per block and puts that in a list
'''
VT28 Rules on Doubling Events:
- 42 and 43 hundred block events (instruments) can be doubled as well as the sims between them
- Forms can have 2 doubled flights (2 out & in's)
- Capstone can double the sims and then do 1 doubled flight (1 out & in)
'''
# Questions??? -> what's the normal down time between flights and then what's the time for sims?
#              -> do we need to give students and instructors some "down time" in between events if they are doubling?
def make_events(file_path, block, double_sim, double_flight):
    # keep track of each event's activity time
    activity_time_dict = getActivityTime()
    on_wing_need_dict = is_on_wing_needed()
    # -------------------------------------------------
    # 1️⃣ READ CSV INTO RAW ROWS
    # -------------------------------------------------
    rows = []
    with open(file_path, "r") as f:
        next(f)  # skip header
        for line in f:
            event_id, training_day, resource = [x.strip() for x in line.split(",")]
            rows.append((event_id, int(training_day), resource))

    # -------------------------------------------------
    # 2️⃣ OPTIONAL MERGING (DOUBLING)
    # -------------------------------------------------
    def merge_row_pairs(rows, pairs):
        rows = rows[:]  # work on a copy

        for a, b in pairs:
            row_a = next((r for r in rows if r[0] == a), None)
            row_b = next((r for r in rows if r[0] == b), None)

            if row_a and row_b:
                merged_name = f"{a}/{b}"
                merged_day = row_a[1]
                merged_resource = row_a[2]

                rows.remove(row_a)
                rows.remove(row_b)
                rows.append((merged_name, merged_day, merged_resource))

        return rows

    # ---------------- DOUBLING SIMS ----------------
    if double_sim:
        if block == "instruments":
            pairs = [
                ("I3201", "I3202"),
                ("I3203", "I3204"),
                ("I3205", "I3206"),
            ]
            rows = merge_row_pairs(rows, pairs)

        elif block == "capstone":
            pairs = [
                ("CS2101", "CS2102"),
                ("CS3101", "CS3102"),
            ]
            rows = merge_row_pairs(rows, pairs)

    # ---------------- DOUBLING FLIGHTS ----------------
    if double_flight:
        if block == "instruments":
            pairs = [
                ("I4201", "I4202"),
                ("I4203", "I4204"),
                ("I4301", "I4302"),
                ("I4303", "I4304"),
            ]
            rows = merge_row_pairs(rows, pairs)

        elif block == "forms":
            pairs = [
                ("F4101", "F4102"),
                ("F4103", "F4104"),
            ]
            rows = merge_row_pairs(rows, pairs)

        elif block == "capstone":
            pairs = [
                ("CS4101", "CS4102"),
            ]
            rows = merge_row_pairs(rows, pairs)

    # -------------------------------------------------
    # 3️⃣ GROUP EVENTS BY TRAINING DAY
    # -------------------------------------------------
    grouped = defaultdict(lambda: {"names": [], "resource": None, "time": 0.0})

    for event_id, day, resource in rows:
        grouped[day]["names"].append(event_id)
        grouped[day]["resource"] = resource

        # if merged event (contains "/"), sum its components
        if "/" in event_id:
            total_time = sum(activity_time_dict[name] for name in event_id.split("/"))
            if resource == "aircraft":
                total_time += 0.5              # add half an hour for inbetween time for doubled flying events
            if resource in {"utd", "oft", "vtd", "mr"}:
                total_time += 0.2              # inbetween time for doubling up on sims 
        else:
            total_time = activity_time_dict[event_id]

        grouped[day]["time"] += total_time

    # -------------------------------------------------
    # 4️⃣ CREATE FINAL EVENT OBJECTS
    # -------------------------------------------------
    events = []

    for day, data in sorted(grouped.items()):
        merged_name = "/".join(data["names"])
        total_time = data["time"]
        resource = data["resource"]
        ev = Event(merged_name, day, resource, total_time, block)
        if "/" in ev.name and ev.resource in {"aircraft","utd", "oft", "vtd", "mr"}:
            ev.is_double = True
        events.append(ev)
    #for ev in events:
    #    print(ev, " ", ev.activity_time)


    if block == "contacts":
        for ev in events:
            if ev.resource == "aircraft":
                ev.on_wing = on_wing_need_dict[ev.name]


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

            # Create student object
            student = FlightStudent(student_id, class_id, start_date)

            # gets tricky here because need to check if they have done aero
            sys1 = FlightStudent.syllabus1
            sys2 = FlightStudent.syllabus2
            sys3 = FlightStudent.syllabus3
            sys4 = FlightStudent.syllabus4

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
                student.days_since_last_event = (START_DATE - student.last_completed_event_date).days
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
                # Syllabus combinations:
                # 2 -> aero, forms, instruments
                # 3 -> instruments, forms, aero
                # 4 -> aero, instruments, forms
                # instr last event: FAM4601
                # aero last event: FAM4703
                # forms last event: F4290
                if student.current_block in (2,3):     # currently in instruments
                    if not row["FAM4703"].strip():     # if not complete with aero
                        student.syllabus_type = 1
                    else:
                        if not row["F4290"].strip():   # aero complete, forms incomplete
                            student.syllabus_type = 4
                            student.current_block += 1
                        else:                          # aero and forms complete
                            student.syllabus_type = 2
                            student.current_block += 2

                if student.current_block == 4:         # currently in aero
                    if not row["FAM4601"].strip():     # if not complete with instruments (could either make these people 2 or 4)
                        student.syllabus_type = 2      # or 4
                        student.current_block -= 2
                    else:                              # complete with instruments
                        if row["F4290"].strip():
                            student.syllabus_type = 3
                            student.current_block += 1

                if student.current_block == 5:         # currently in forms
                    if not row["FAM4703"].strip():     # not aero complete (have to be in syllabus 3)
                        student.syllabus_type = 3
                        student.current_block -= 1
                    else:
                        if not row["FAM4601"].strip():   # aero complete, not yet done instruments
                            student.syllabus_type = 2
                            student.current_block -= 2

                for i in range(0, student.current_block):
                    student.completed_blocks[i] = 1
            
            # Go through and update the completed_dates list
            end_events1 = {0:"G0102", 1:"FAM4501", 2:"NA1190", 3:"FAM4601", 4:"FAM4703", 5:"F4290", 6:"CS4290"}
            end_events2 = {0:"G0102", 1:"FAM4501", 2:"FAM4703", 3:"F4290", 4:"NA1190", 5:"FAM4601", 6:"CS4290"}
            end_events3 = {0:"G0102", 1:"FAM4501", 2:"NA1190", 3:"FAM4601", 4:"F4290", 5:"FAM4703", 6:"CS4290"}
            end_events4 = {0:"G0102", 1:"FAM4501", 2:"FAM4703", 3:"NA1190", 4:"FAM4601", 5:"F4290", 6:"CS4290"}
            # sometimes they forget to put the completion date if the last two events take place on the same day...
            almost_end_events1 = {0:"G0290", 1:"FAM4490", 2:"NA1106", 3:"N4101", 4:"FAM4702", 5:"F4104", 6:"CS4102"}
            almost_end_events2 = {0:"G0290", 1:"FAM4490", 2:"FAM4702", 3:"F4104", 4:"NA1106", 5:"N4101", 6:"CS4102"}
            almost_end_events3 = {0:"G0290", 1:"FAM4490", 2:"NA1106", 3:"N4101", 4:"F4104", 5:"FAM4702", 6:"CS4102"}
            almost_end_events4 = {0:"G0290", 1:"FAM4490", 2:"FAM4702", 3:"NA1106", 4:"N4101", 5:"F4104", 6:"CS4102"}
            for i, block in enumerate(student.completed_blocks):
                if student.syllabus_type == 1:
                    if block == 1:
                        date = row[end_events1[i]]
                        if date == '':
                            date = row[almost_end_events1[i]]
                        student.completed_dates[i] = datetime.strptime(date, "%m/%d/%Y").date()

                    if student.next_event_index >= len(sys1[student.current_block]):
                        student.completed_blocks[student.current_block] = 1
                        student.current_block += 1
                        student.next_event_index = 0

                elif student.syllabus_type == 2:
                    if block == 1:
                        date = row[end_events2[i]]
                        if date == '':
                            date = row[almost_end_events2[i]]
                        student.completed_dates[i] = datetime.strptime(date, "%m/%d/%Y").date()

                    if student.next_event_index >= len(sys2[student.current_block]):
                        student.completed_blocks[student.current_block] = 1
                        student.current_block += 1
                        student.next_event_index = 0

                elif student.syllabus_type == 3:
                    if block == 1:
                        date = row[end_events3[i]]
                        if date == '':
                            date = row[almost_end_events3[i]]
                        student.completed_dates[i] = datetime.strptime(date, "%m/%d/%Y").date()

                    if student.next_event_index >= len(sys3[student.current_block]):
                        student.completed_blocks[student.current_block] = 1
                        student.current_block += 1
                        student.next_event_index = 0

                elif student.syllabus_type == 4:
                    if block == 4:
                        date = row[end_events4[i]]
                        if date == '':
                            date = row[almost_end_events4[i]]
                        student.completed_dates[i] = datetime.strptime(date, "%m/%d/%Y").date()
                    
                    if student.next_event_index >= len(sys4[student.current_block]):
                        student.completed_blocks[student.current_block] = 1
                        student.current_block += 1
                        student.next_event_index = 0
            
            student_list.append(student)
    FlightStudent.student_id = len(student_list)+5


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
                    new_stu = FlightStudent(FlightStudent.student_id, class_id, date)
                    new_stu.imported = False
                    new_students.append(new_stu)
    return new_students
    

def set_bg(widget, color):
    widget.configure(bg=color)
    for child in widget.winfo_children():
        set_bg(child, color)


import tkinter as tk

def month_class_size_selector(parent):
    container = tk.Frame(parent)
    container.pack(pady=10, fill="x")

    # --- Header row with checkbox ---
    header = tk.Frame(container)
    header.pack(anchor="w")

    use_monthly_var = tk.BooleanVar(value=False)

    tk.Checkbutton(
        header,
        text="Use monthly class-up size",
        variable=use_monthly_var
    ).pack(side="left")

    # --- Preset row ---
    preset_frame = tk.Frame(container)
    preset_frame.pack(anchor="w", pady=(5, 8))

    tk.Label(preset_frame, text="Preset value:").pack(side="left")

    preset_var = tk.IntVar(value=5)

    # Validation: allow empty or integer >= 0
    def validate_non_negative(P):
        if P == "":
            return True
        try:
            return int(P) >= 0
        except ValueError:
            return False

    vcmd = (parent.register(validate_non_negative), "%P")

    preset_spin = tk.Spinbox(
        preset_frame,
        from_=0,
        to=500,
        width=5,
        textvariable=preset_var,
        validate="key",
        validatecommand=vcmd
    )
    preset_spin.pack(side="left", padx=5)

    # --- Month grid ---
    grid = tk.Frame(container)
    grid.pack()

    months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    month_vars = {}
    month_entries = {}

    for idx, m in enumerate(months):
        r = idx // 6
        c = idx % 6

        cell = tk.Frame(grid, padx=4, pady=4)
        cell.grid(row=r, column=c)

        tk.Label(cell, text=m).pack()

        var = tk.StringVar(value="5")
        entry = tk.Entry(
            cell,
            textvariable=var,
            width=4,
            justify="center",
            validate="key",
            validatecommand=vcmd
        )
        entry.pack()

        month_vars[m] = var
        month_entries[m] = entry

    # --- Apply preset to all months ---
    def apply_preset(*_):
        val = str(preset_var.get())
        for v in month_vars.values():
            v.set(val)

    preset_var.trace_add("write", apply_preset)
    apply_preset()

    # --- Enable/disable logic ---
    def toggle_enabled(*_):
        state = "normal" if use_monthly_var.get() else "disabled"

        for entry in month_entries.values():
            entry.config(state=state)

        preset_spin.config(state=state)

    use_monthly_var.trace_add("write", toggle_enabled)
    toggle_enabled()

    # --- Getter to return clean ints ---
    def get_values():
        values = []
        for m in months:
            val = month_vars[m].get()
            if val == "":
                val = 0
            values.append(int(val))
        return values

    return use_monthly_var, get_values


def ask_user():
    result = {}

    root = tk.Tk()
    root.title("VT28 Scheduling Simulation")
    root.geometry("640x980+0+0")
    root.resizable(True, True)

    # bring window to front (temporarily)
    root.update_idletasks()
    root.deiconify()
    root.after_idle(lambda: (
        root.lift(),
        root.attributes("-topmost", True),
        root.after(100, lambda: root.attributes("-topmost", False))
    ))


    # ============================================================
    # QUESTION 3 — Runs per class size (positive integer textbox)
    # ============================================================
    tk.Label(
        root,
        text="How many simulation runs per class size? (100 runs is about 20 seconds)",
        font=("Arial", 12)
    ).pack(pady=(20, 5))

    runs_var = tk.StringVar(value="1")  # default value

    # validation function
    def validate_positive_int(P):
        if P == "":
            return True  # allow empty while typing
        return P.isdigit() and int(P) > 0

    vcmd_runs = (root.register(validate_positive_int), "%P")

    runs_entry = tk.Entry(
        root,
        textvariable=runs_var,
        validate="key",
        validatecommand=vcmd_runs,
        width=10,
        justify="center"
    )
    runs_entry.pack()




    # # ---------------- Toggle Question ----------------
    tk.Label(
        root,
        text="Would you like to MAX the ACTIVE students to 250?",
        font=("Arial", 12)
    ).pack(pady=10)

    choice_tog1 = tk.StringVar(value="no")

    radio_frame_tog = tk.Frame(root)
    radio_frame_tog.pack()

    tk.Radiobutton(radio_frame_tog, text="Yes", variable=choice_tog1, value="yes").pack(side="left", padx=10)
    tk.Radiobutton(radio_frame_tog, text="No", variable=choice_tog1, value="no").pack(side="left", padx=10)


    ## toggle question two

    # # ---------------- Toggle Question (sims) ----------------
    tk.Label(
        root,
        text="Would you like to double up Sims?",
        font=("Arial", 12)
    ).pack(pady=10)

    choice_tog2 = tk.StringVar(value="no")

    radio_frame_tog2 = tk.Frame(root)
    radio_frame_tog2.pack()

    tk.Radiobutton(radio_frame_tog2, text="Yes", variable=choice_tog2, value="yes").pack(side="left", padx=10)
    tk.Radiobutton(radio_frame_tog2, text="No", variable=choice_tog2, value="no").pack(side="left", padx=10)

    # # ---------------- Toggle Question (flights) ----------------
    tk.Label(
        root,
        text="Would you like to double up Flights?",
        font=("Arial", 12)
    ).pack(pady=10)

    choice_tog3 = tk.StringVar(value="no")

    radio_frame_tog3 = tk.Frame(root)
    radio_frame_tog3.pack()

    tk.Radiobutton(radio_frame_tog3, text="Yes", variable=choice_tog3, value="yes").pack(side="left", padx=10)
    tk.Radiobutton(radio_frame_tog3, text="No", variable=choice_tog3, value="no").pack(side="left", padx=10)

    # ============================================================
    # NEW QUESTION 3 — Class sizes (multi-select)
    # ============================================================
    tk.Label(
        root,
        text="Select all class sizes you would like to simulate.",
        font=("Arial", 12)
    ).pack(pady=(20, 5))

    class_sizes = [0,2, 4, 5,6,7,8,10,13,15]
    class_size_vars = {}

    class_size_frame = tk.Frame(root)
    class_size_frame.pack()

    for size in class_sizes:
        var = tk.IntVar(value=0)
        class_size_vars[size] = var
        tk.Checkbutton(
            class_size_frame,
            text=str(size),
            variable=var
        ).pack(side="left", padx=8)

    ## do you want to do monthly
    use_monthly_var, get_monthly_values = month_class_size_selector(root)


    # ============================================================
    # NEW QUESTION 4 — Percent syllabus two (multi-select)
    # ============================================================
    tk.Label(
        root,
        text="Select all percentages of students in the alternate syllabus you would like to simulate.",
        font=("Arial", 12)
    ).pack(pady=(20, 5))

    #percentages = [0, 5, 10, 15, 20]
    percentages = [0, 10, 25, 33, 50, 67, 75, 90, 100]
    percent_vars = {}

    percent_frame = tk.Frame(root)
    percent_frame.pack()

    for p in percentages:
        var = tk.IntVar(value=0)
        percent_vars[p] = var
        tk.Checkbutton(
            percent_frame,
            text=f"{p}%",
            variable=var
        ).pack(side="left", padx=8)

 

    

    set_bg(root, "#2f528a")

    # ---------------- Confirm ----------------
    def confirm():
        result["double_sim"] = (choice_tog2.get() == "yes")
        result["double_flight"] = (choice_tog3.get() == "yes")
        result["max_250"] = (choice_tog1.get() == "yes")
        result["use_monthly_class_sizes"] = use_monthly_var.get()
        result["monthly_class_sizes"] = get_monthly_values()

        # collect multi-select results
        selected_class_sizes = [size for size, var in class_size_vars.items() if var.get() == 1]
        selected_percentages = [p for p, var in percent_vars.items() if var.get() == 1]

        # apply defaults if none selected
        if not selected_class_sizes:
            selected_class_sizes = []

        if not selected_percentages:
            selected_percentages = [0]

        result["class_sizes"] = selected_class_sizes
        result["syllabus_two_percentages"] = selected_percentages

        runs_value = runs_var.get()
        if runs_value == "":
            runs_value = 1
        else:
            runs_value = int(runs_value)

        result["runs_per_class_size"] = runs_value

        root.destroy()
    tk.Button(root, text="Confirm", width=15, command=confirm).pack(pady=20)

    root.mainloop()

    return result


# # ## student list in format 
# # '''
# # [
# # [[list 1],[list2],[list3]],
# # [[list 1],[list2],[list3]],
# # [[list 1],[list2],[list3]],
# # etc
# # ]
# # '''
# # # class up size in format [1,2,3,...]
# # #remove current students is a bool
# returns in format [wait1, wait2,... ] no class sizes
def compute_average_waits(student_lists, remove_current_students=True, debug=False):
    """
    Computes average wait times for a list of student lists.
    Returns a list of average waits corresponding to each run.
    """
    average_waits = []

    for run_idx, run in enumerate(student_lists):
        total_waits = []   # ✅ FIX: initialize early

        for s in run:
            start = s.start_date
            if isinstance(start,datetime):
                start=start.date()

            # Exclude current students if requested
            if remove_current_students and s.imported:
                continue
            # else:

            if None in s.completed_dates:
                continue

            completed_dates = [
                d.date() if isinstance(d, datetime) else d
                for d in s.completed_dates
            ]

            total_waits.append(
                (completed_dates[-1] - start).days / 7
            )

        avg_wait = sum(total_waits) / len(total_waits) if total_waits else np.nan
        average_waits.append(avg_wait)


    return average_waits




def plot_grouped_results(data_dict, xlabel = "Class Size", ylabel = "Wait time", title = "Monte Carlo Results"):
    plt.figure()

    for key, points in data_dict.items():
        # sort by x to avoid zig-zag lines
        points = sorted(points, key=lambda t: t[0])

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        plt.plot(xs, ys, marker='o', label=str(key))

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(title="Group")
    plt.grid(True)
    plt.tight_layout()

    save_dir = "."

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"monte_carlo_{timestamp}.png"

    full_path = os.path.join(save_dir, filename)

    plt.savefig(full_path, dpi=300)

    plt.show()
    print(f"Saved to: {full_path}")


def main():
    # Resources
    classrooms = "classroom"
    utd_sims = "utd"
    oft_sims = "oft"
    vtd_sims = "vtd"
    mr_sims = "mr"
    aircrafts = "aircraft"

    global holiday_ranges,leave_ranges

    holiday_ranges = load_holiday_ranges("holidays.csv")
    leave_ranges = load_leave_ranges("holiday_leave.csv")

    # going to running run_simulation function multiple times based on different class sizes

    user_input = ask_user()

    #### can use these variables to determine if sims and/or flights should be double scheduled. 
    double_sim = user_input["double_sim"]
    double_flight = user_input["double_flight"]

    # Initialize a list of event objects for each block
    sysGrndSchoolEvents = make_events(os.path.join("data", "sysGrnd.csv"), "system ground", double_sim, double_flight)
    # FAM1301, FAM4101, FAM4102, FAM4103, FAM4104, FAM4303, FAM4304 are the required onwing events
    contactsEvents = make_events(os.path.join("data", "contacts.csv"), "contacts", double_sim, double_flight)


    aeroEvents = make_events(os.path.join("data","aero.csv"), "aero", double_sim, double_flight)
    instrGrndSchoolEvents = make_events(os.path.join("data", "instrGrnd.csv"), "instrument ground", double_sim, double_flight)
    instrumentsEvents = make_events(os.path.join("data", "instr.csv"), "instruments", double_sim, double_flight)
    formsEvents = make_events(os.path.join("data", "forms.csv"), "forms", double_sim, double_flight)
    capstoneEvents = make_events(os.path.join("data", "capstone.csv"), "capstone", double_sim, double_flight)
    
    # syllabus combinations (can add more)
    syllabus1 = [sysGrndSchoolEvents, contactsEvents, instrGrndSchoolEvents, instrumentsEvents, aeroEvents, formsEvents, capstoneEvents]
    syllabus2 = [sysGrndSchoolEvents, contactsEvents, aeroEvents, formsEvents, instrGrndSchoolEvents, instrumentsEvents, capstoneEvents]
    
    # current students may have one of these syllabi, but new students will stick to 1 or 2 for now:
    syllabus3 = [sysGrndSchoolEvents, contactsEvents, instrGrndSchoolEvents, instrumentsEvents, formsEvents, aeroEvents, capstoneEvents]
    syllabus4 = [sysGrndSchoolEvents, contactsEvents, aeroEvents, instrGrndSchoolEvents, instrumentsEvents, formsEvents, capstoneEvents]


    # Resources
    classrooms_list = [Classroom(f"CL{i+1}") for i in range(6)]
    utd_sims_list = [Utd(f"UTD{i+1}") for i in range(6)]
    oft_sims_list = [Oft(f"OFT{i+1}") for i in range(6)]
    vtd_sims_list = [Vtd(f"VTD{i+1}") for i in range(18)]
    mr_sims_list = [Mr(f"MR{i+1}") for i in range(2)]
    aircraft_list = [Aircraft(f"AC{i+1}") for i in range(18)]

    # Run the simulation
    # run_simulation(students, syllabus).syllabus1 = syllabus1
    FlightStudent.syllabus1 = syllabus1
    FlightStudent.syllabus2 = syllabus2
    FlightStudent.syllabus3 = syllabus3
    FlightStudent.syllabus4 = syllabus4


    global max_250

    max_250 = user_input["max_250"]
    
    instructors = load_instructors(os.path.join("instructors", "instructor_data.csv"))

    percentages = user_input["syllabus_two_percentages"]
    class_size = user_input["class_sizes"]
    run_count = user_input["runs_per_class_size"]


    # format {percentone: data, percenttwo: data, ...}
    data = {}
    for p in percentages:
        data[p] = []
        for c in class_size:
            start_time = time.perf_counter()
            average_for_class_size = 0
            print("class size",c)

            for x in range(run_count):
                students = []
                FlightStudent.student_id = 0
                students = load_students(os.path.join("students", "current_students.csv"))
                computed_students = run_simulation(START_DATE, 365*1.5, p, students, instructors, utd_sims_list, oft_sims_list, vtd_sims_list, mr_sims_list,aircraft_list,classrooms_list, syllabus1,syllabus2,syllabus3,syllabus4,"fixed",c,None)
                average_for_class_size += compute_average_waits([computed_students], False)[0]
            average_for_class_size = average_for_class_size/run_count

            elapsed = time.perf_counter() - start_time   # end timer

            print(f"Class size {c} completed in {elapsed:.2f} seconds")

            data[p].append((c,average_for_class_size))
            

        if user_input["use_monthly_class_sizes"]:

            start_time = time.perf_counter()
            average_for_class_size = 0
            print("class size",c)
            
            for x in range(run_count):
                students = []
                FlightStudent.STATIC_ID = 0
                
                students = load_students(os.path.join("students", "current_students.csv"))
                computed_students = run_simulation(START_DATE, 365*1.5*7, p, students, instructors, utd_sims_list, oft_sims_list, vtd_sims_list, mr_sims_list, aircraft_list, classrooms_list, syllabus1, syllabus2, syllabus3, syllabus4, "Variable", 0, user_input["monthly_class_sizes"])
                average_for_class_size += compute_average_waits([computed_students],False)[0]

            average_for_class_size = average_for_class_size/run_count

            elapsed = time.perf_counter() - start_time   # end timer

            print(f"Class size variable completed in {elapsed:.2f} seconds")

            data[p].append((100,average_for_class_size))




    print(data)
    plot_grouped_results(data, title = f"Monte Carlo {run_count} runs per point")



if __name__ == "__main__":
    main()
