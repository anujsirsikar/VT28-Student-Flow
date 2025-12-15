# Take care of all the resources, and what defines them
# Note: these things can't be used everyday (usually just mon-fri)

class Classroom():
    amount = 6
    daily_hours = 12                         #0600 to 1800
    break_time = 0

    def __init__(self, name, capacity=8):
        self.name = name
        self.capacity = capacity
        self.current_num = 0
        self.event = None
        self.daily_hours = 12

    def __repr__(self):
        return self.name
  
class Sim():
    amount = 32
    daily_hours = 17.5                       # 0530 to 2300
    failure_rate = 0.02                      # 98% chance that the given sim is working 
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

class Vtd(Sim):                           # subclass of Sim
    amount = 18
    def __init__(self, name):
        super().__init__()
        self.name = name

class Utd(Sim):                           # subclass of Sim
    amount = 6
    def __init__(self, name):
        super().__init__()
        self.name = name

class Mr(Sim):                           # subclass of Sim
    amount = 2
    def __init__(self, name):
        super().__init__()
        self.name = name

# Subclass of Mediums
class Aircraft():
    amount = 18
    daily_hours = 16                     # 11 for the day and 5 for the night (0700 to 2300)
    break_time = 1
    failure_rate = 0.25                  # 75% chance given aircraft is working
    uses_per_day = 4                
    def __init__(self, name, capacity=1):
        self.name = name
        self.capacity = capacity
        self.breakTime = 1               # hours
        self.failureRate = 0.25          # 75% chance given aircraft is working


    def __str__(self):
        return f"Aircraft: {self.name}"
    
    def __repr__(self):
        return str(self)

# now can write all the functions that alter the resources
