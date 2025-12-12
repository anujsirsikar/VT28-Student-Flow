# Take care of all the resources, and what defines them
# Note: these things can't be used everyday (usually just mon-fri)

# Subclass of Mediums
class Classroom():
    amount = 6
    daily_hours = 12  #0600 to 1800
    break_time = 0
    # ***is a classroom capacity a factor? -> no, but later on add a class size variable
    def __init__(self, name, capacity=8):
        self.name = name
        self.status = 0 # 0 = available and 1 = occupied
        self.capacity = capacity
        self.current_num = 0
        self.event = None
        self.daily_hours = 12

    def __repr__(self):
        return self.name
  
# Subclass of Mediums
class Sim():
    amount = 32
    daily_hours = 17.5  # 0530 to 2300
    failure_rate = 0.02  # 98% chance that the given sim is working 
    break_time = 0.5
    def __init__(self, capacity=1):
        self.capacity = capacity
        self.name = "sim"

    def __str__(self):
        return f"Name: {self.name}"
    
    def __repr__(self):
        return str(self)

class Oft(Sim):                           # subclass of Sim
    amount = 6
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.status = 0 # 0 = available and 1 = occupied
class Vtd(Sim):                           # subclass of Sim
    amount = 18
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.status = 0 # 0 = available and 1 = occupied
class Utd(Sim):                           # subclass of Sim
    amount = 6
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.status = 0 # 0 = available and 1 = occupied
class Mr(Sim):                           # subclass of Sim
    amount = 2
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.status = 0 # 0 = available and 1 = occupied

# Subclass of Mediums
class Aircraft():
    amount = 18
    daily_hours = 16   # 11 for the day and 5 for the night (0700 to 2300)
    break_time = 1
    failure_rate = 0.25 # 75% chance given aircraft is working
    def __init__(self, name, capacity=1):
        self.name = name
        self.status = 0 # 0 = available and 1 = occupied
        self.capacity = capacity
        self.use_per_day = 0  # no more than 4 times per day
        #self.currentLoad = 0  # i think we can delete this
        self.start = 7  # represents 0700
        self.day_stop = 18
        self.night_start = 18
        self.stop = 23 # represents 2300 
        self.breakTime = 1 # hours
        self.failureRate = 0.25  # 75% chance given aircraft is working
        self.usePerDay = 0  # no more than 4 times per day

# now can write all the functions that alter the resources
