# Take care of all the resources, and what defines them



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

# now can write all the functions that alter the resources