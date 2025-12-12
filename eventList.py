


# This code will address the flight schedule and different events and the resources they need
class TrainingBlock:
    def __init__(self, name, num_events, events, total_days, total_activity_time):
        self.name = name # name of the block (i.e. aero, contacts, etc...)
        self.num_events = num_events
        self.events = events  # a list of the actual event objects
        self.total_days = total_days
        self.total_activity_time = total_activity_time   # in hours
        self.num_students = 0 

class Event:
    def __init__(self, name, training_day, resource, activity_time, block):
        self.name = name # i.e. FAM2101, etc...
        self.training_day = training_day
        self.activity_time = activity_time # in hours
        self.resource = resource
        # need to add this:
        self.block = block 

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

# returns the times associated with each event
def getActivityTime():

    event_times = {
        # sysGrndSchoolEvents
        "G0101": 3.65, "G6001": 3.65, "G0107": 1.5, "SY0101": 1.5, "SY0102": 1.5,
        "SY0106": 1.9, "SY0112": 3.5, "SY0190": 1.45, "SY0203": 1.45, "SY0206": 1.25,
        "G0106": 1.25, "SY0290": 2.167, "G0104": 2.167, "G0105": 2.167, "SY0301": 1.83,
        "PR0101": 1.83, "PR0102B": 1.83, "PR0103": 1.83, "PR0104": 1.83, "PR0105": 1.83,
        "FAM1106": 2.5, "FAM1190": 1.75, "FAM1203": 1.75, "FAM1290": 2.33, "G0201": 2.33,
        "G0103": 2.33, "G0290": 3.5, "G0102": 3.5,

        # contactsEvents
        "FAM2101": 1.3, "FAM2102": 1.3, "FAM2201": 1.3, "FAM2202": 1.3,
        "IN1104": 1.0, "I2101": 1.3, "I2102": 1.3, "I2103": 1.3,
        "FAM3101": 1.3, "FAM3102": 1.3, "FAM3103": 1.3, "FAM6101": 1.3,
        "FAM6102": 1.3, "FAM6201": 1.3, "FAM6202": 1.3, "FAM6203": 1.3,
        "FAM6301": 1.3, "FAM6302": 1.3, "FAM1301": 1.3, "FAM4101": 3.0,
        "FAM4102": 1.5, "FAM4103": 1.5, "FAM4104": 1.5, "FAM3201": 1.5,
        "FAM3202": 1.3, "FAM3301": 1.3, "FAM6401": 1.3, "FAM6402": 1.3,
        "FAM4201": 1.3, "FAM4202": 1.6, "FAM1206": 1.6, "FAM4203": 1.0,
        "FAM4204": 1.6, "FAM4301": 1.6, "FAM4302": 1.7, "FAM4303": 1.7,
        "FAM4304": 1.7, "FAM4490": 1.7, "FAM4501": 1.7,

        # aeroEvents
        "FAM3401": 1.7, "FAM4701": 1.5, "FAM4702": 1.3, "FAM4703": 1.3,

        # instrGrndSchoolEvents
        "IN1202": 1.7, "IN1203": 1.7, "IN1205": 1.7, "IN1206": 1.7,
        "IN1290": 4.0, "IN1305": 4.0, "IN1306": 4.0, "IN1307": 1.0,
        "IN1308": 1.0, "IN1390": 4.0, "IN1403": 4.0, "IN1406": 5.0,
        "IN1411": 4.5, "IN1412": 4.5, "IN1413A": 4.5, "IN1490": 2.0,
        "IN1501": 2.0, "NA1105": 6.5, "NA1106": 6.5, "NA1190": 2.0,

        # instrumentsEvents
        "I2201": 6.5, "I2202": 2.0, "I2203": 4.0, "N3101": 1.0,
        "N6101": 1.3, "I6101": 1.3, "I6102": 1.3, "I3101": 1.3,
        "I3102": 1.3, "I3103": 1.3, "I3104": 1.3, "I6201": 1.3,
        "I6202": 1.3, "I4101": 1.3, "I4102": 1.3, "I4103": 1.3,
        "SY0302": 1.6, "I3201": 1.6, "I3202": 1.6, "I3203": 3.5,
        "I3204": 1.0, "I3205": 2.0, "I3206": 1.3, "I6301": 1.3,
        "I4201": 1.7, "I4202": 1.7, "I4203": 1.7, "I4204": 1.7,
        "I4301": 1.6, "I4302": 1.6, "I4303": 1.6, "I4304": 1.6,
        "I4490": 1.6, "N4101": 1.7, "FAM4601": 1.7,

        # formsEvents
        "F1102": 1.7, "FF190": 1.7, "FF1201": 1.3, "F3101": 1.3,
        "F2101": 1.3, "F4101": 1.3, "F4102": 1.6, "F4103": 1.6,
        "F4104": 1.6, "F4290": 1.6,

        # capstoneEvents
        "CS1101": 1.7, "CS2101": 1.7, "CS2102": 1.7, "CS3101": 4.0,
        "CS3102": 4.0, "CS4101": 1.7, "CS4102": 1.7, "CS4290": 1.7,
    }

    return event_times