# Romeo Vanegas
# CSCI 154 - Bank Simulation
# Spring 2022 

from collections import deque
import copy
from scipy.stats import truncnorm
import numpy as np
import math
import matplotlib.pyplot as plt


# Customer and teller deque's, cust. maxlen is arbitrary
# Simluation requires maxlen 10 for teller deque
tellerTotal = 10
totalLoops = 5000

# Flag if using Priority Queue
usingPq = True

# Customer Deque
cust = deque(maxlen=160)
# Teller Deque
tell = deque(maxlen=tellerTotal)

# Customer VIP Deque
fastService = deque(maxlen=20)
# Array Holding Waiting Time of Customers
waitTimePerCust = []

#Array holding total customers not attended to at end of day
custUnserved = []

#Array holding number of customers served per iteration
custServed = []

#Array to hold customer workunits to determine average
custWorkUnits = []

#List of All Customer arrival times Generated per day (iterations)
custTotalArrivalTimes = []

# Stats Variables
low = 5
high = 15
mean = 5
var = 0.5

####Globals#####
# global for number of minutes in 8 hours (sim run time)
minutes = 480
# total number of work units per Teller
workUnits = 160
workUnitsTotal = workUnits * tellerTotal
# total number of customers in 8 hours
totalCustomers = 160
# All teller windows busy counter
tellerBusyCounter = 0
# Customer Waiting Time
waitingTime = 0


# Array of normal distribution of arrival times
s = np.random.uniform(0, minutes, totalCustomers)

####################################################################
##################### Customer/Teller classes ######################

class Customer:
    def __init__(self, wu, status, vip, waitTime):
        # Initialize member varibles
        # Work units variable
        self.wu = wu
        # Customer status 0 = helped and 1 = waiting
        self.status = status
        # VIP (priority) flag is set to 0 unless given higher priority then 1
        self.vip = vip
        # Customers Individual Waiting Time
        self.waitTime = waitTime

    def custStats(self):
        # Customer Statistics
        print(f"{self.wu} work units")
        print(f"{self.status} current status")
        print(f"{self.vip} current VIP status\n")

# Teller Class


class Teller:
    def __init__(self, wu, status, currentCust):
        # Initialize member varibles
        # Work units variable
        self.wu = wu
        # Teller status 0 = idle or 1 = busy
        self.status = status
        # Current customer class varibles (workunits,status,vip)
        self.currentCust = currentCust

    def tellStats(self):
        # Teller statistics
        print(f"{self.wu} work units")
        print(f"{self.status} current status\n")

########################################################
##################### Functions ########################
########################################################

# When teller is avaiable, calls next customer. Also sets
# Teller status to Busy (1). IDX passes the index of avaiable teller.
def helpCustomer(IDX):
    """When teller becomes available (status = 0), function will assign next available
    customer (either from priority queue or normal queue ) to idle teller window. Queue choice
    depends if usingPq is true or false.

    Args:
        IDX (integer): teller window number.
    """
    global waitTimePerCust

    if usingPq and len(fastService) > 0:
        nextp = fastService.popleft()
        tell[IDX].currentCust = nextp
        tell[IDX].currentCust.status = 0
        tell[IDX].status = 1
        waitTimePerCust.append(tell[IDX].currentCust.waitTime)
        tell[IDX].currentCust.waitTime = 0

    else:
        # Pops from customer deque and assigns customer to teller IDX (swap)
        nextp = cust.popleft()
        tell[IDX].currentCust = nextp
        # Customer status set to helped (0)
        tell[IDX].currentCust.status = 0
        # Teller Status set to busy (1)
        tell[IDX].status = 1
        waitTimePerCust.append(tell[IDX].currentCust.waitTime)
        tell[IDX].currentCust.waitTime = 0

# Handles decrementing customer and teller work units with passage of time
def workUnitDec():
    """Decrements work units for customer and teller by -1 with each call. 
    """
    counter = 0
    global workUnitsTotal
    while counter < tell.maxlen:
        if tell[counter].status == 1:
            tell[counter].wu -= 1
            tell[counter].currentCust.wu -= 1
            workUnitsTotal -= 1
        counter += 1

# Handles checking if Customer's transaction has finished
def custTransaction():
    """Checks teller's status. If teller workunits reaches 0, then customer is either
    marked as served, or reassigned back to the front of the queue (or priority queue,
    depending if usingPq is true).
    """
    counter = 0
    global customersServed
    while counter < tell.maxlen:
        if tell[counter].status == 1:
            if tell[counter].currentCust.wu <= 0:
                tell[counter].status = 0
                tell[counter].currentCust.status = 0
                customersServed += 1

            elif tell[counter].wu == 0 and usingPq:
                tell[counter].currentCust.vip = 1
                fastService.appendleft(tell[counter].currentCust)

            elif tell[counter].wu == 0:
                tell[counter].currentCust.vip = 1
                cust.appendleft(tell[counter].currentCust)
        counter += 1

# Handles increasing each customers wait time in line
def custWaitTime():
    """Increments customer wait times while waiting in line.
    """
    for i in range(0, len(cust)):
        if cust[i].status == 1:
            cust[i].waitTime += 1
    if usingPq:
        for i in range(0,len(fastService)):
            if fastService[i].status == 1:
                fastService[i].waitTime += 1

# Populates Teller line for simulation start - with maxlen(10) amount of tellers
# Each teller is set with max amount of workunits(80)
def tellerPopulate():
    """Populates teller 'line' with teller defaults. 
    Teller Class defaults (workUnits, status, current customer)
    """
    counter = 0
    while counter < (tell.maxlen):
        tellerDefault = Teller(workUnits, 0, 0)
        tell.append(tellerDefault)
        counter += 1

# Polulates (append) Customer deque - one customer at a time
# Work units are randomly generated - values between 5-15
# All customers status is set to waiting (1) by default
def customerPopuluate(isPq):
    """Function for customer 'insertion.' 1 customer per call.
    Work units are generated via normal distribution. Fills both 
    queues (normal and priority).

    Args:
        isPq (bool): True = priority queue, False = normal. 
    """
    wu = get_truncated_normal(mean, var, low, high)
    units = wu.rvs(1)
    custWorkUnits.append(round(units[0]))
    custDefault = Customer(round(units[0]), 1, 0, 0)
    if isPq and units[0] <= 5:
        fastService.append(custDefault)
    else:
        cust.append(custDefault)

# Moves customer from one teller window to another by deepcopying
# customer class values to the new teller window, the old teller's
# current customer class values are set to 0
def moveCurrentCust(old, new):
    """Function copies current customer at teller window [old], and moves them
    to another window [New]. 

    Args:
        old (Integer): Originating teller window.
        new (Integer): Destination teller window.
    """
    # New teller accepts customer from old teller (swap)
    newt = copy.deepcopy(tell[old].currentCust)
    tell[new].currentCust = newt
    # Updates previous teller currentCust class varibles to 0
    # Sets teller status to idle
    tell[new].status = 1
    tell[old].status = 0
    tell[old].currentCust.wu = 0  # Might be unneccessary
    tell[old].currentCust.status = 0
    tell[old].currentCust.vip = 0

# Checks for which teller window is available to help a customer
# Checks teller stats: 1 = busy or 0 = available
def openWindow():
    """Checks teller window status: 1 = busy or 0 = idle for either priority or
    normal queue. Will assign customer to a teller if status is 0 and has 
    work units available.  
    """
    counter = 0
    global waitingTime

    if len(fastService) > 0 and usingPq:
        while counter < (tell.maxlen):
            if (tell[counter].status == 0 and tell[counter].wu > 0 and fastService[0].vip == 0):
                helpCustomer(counter)
                break

            elif tell[counter].status == 0 and tell[counter].wu > 0 and fastService[0].vip == 1:
                helpCustomer(counter)
                break
            elif tell[counter].status == 1:
                counter += 1
        
        waitingTime += 1

    elif len(cust) > 0:
        while counter < (tell.maxlen):
            if (tell[counter].status == 0 and tell[counter].wu > 0 and cust[0].vip == 0):
                helpCustomer(counter)
                break

            elif tell[counter].status == 0 and tell[counter].wu > 0 and cust[0].vip == 1:
                helpCustomer(counter)
                break
            elif tell[counter].status == 1:
                counter += 1

        waitingTime += 1

# Creates Normal Distribution of numbers
def get_truncated_normal(mean, var, low, high):
    """Creates a truncated normal distribution for work unit generation. 

    Args:
        mean (Integer): Mean (average)
        var (Float): Variance
        low (Integer): Lowest value of range
        high (integer): Highest value of range

    Returns:
        float : returns a distribution between 5(low) - 15(high), with a mean of 5, varience of 0.5. 
    """
    return truncnorm(
        (low - mean) / var, (high - mean) / var, loc=mean, scale=var)

# Uniform distribution of numbers
def norm_dist():
    """Returns a list of numbers in the form of a uniform normal distribution. 
    The floor value is taken for each value due to logic constraints. 
    """
    count = 0
    arry = []
    s.sort()
    while count < s.size:
        arry.append(math.floor(s[count]))
        count += 1
    return(arry)

############################################################################################
#################################### Main Program ##########################################

print("--------Please wait while simulation runs. For totalLoops > 1000, it may take a while.--------")

for i in range(0,totalLoops):
    # Initialization Step
    tellerPopulate()
    custArrivalTimes = norm_dist()
    custTotalArrivalTimes.extend(custArrivalTimes)

    # 480 Minutes representative of 8 hours
    workDayTime = minutes
    timePassed = 0
    customersServed = 0
    laterArrival = False
    workUnitsTotal = tellerTotal * workUnits
   

    while (workDayTime > 0 and customersServed < 160 and workUnitsTotal > 0):
        while True and len(custArrivalTimes) > 0:
            if custArrivalTimes[0] == timePassed:
                customerPopuluate(usingPq)
                custArrivalTimes.pop(0)
            else:
                break

        openWindow()
        
        if (timePassed % 6 == 0 and timePassed > 0):
            workUnitDec()
            
        custTransaction()
        custWaitTime()
        workDayTime -= 1
        timePassed += 1

    for i in range(0,len(tell)):
        if tell[i].status == 1:
            cust.appendleft(tell[i].currentCust)
            tell[i].status = 0
    
    custUnserved.append(len(cust))
    if usingPq:
        custUnserved.append(len(fastService))
        fastService.clear()
    custServed.append(customersServed)
    
    tell.clear()
    cust.clear()

print("Number of Customer Wait Times: %d" %len(waitTimePerCust))

avgWorkUnits = np.average(custWorkUnits)
avgWaitTime = np.average(waitTimePerCust)
avgUnserved = np.average(custUnserved)
avgCustServed = np.average(custServed)
print("Average Customer Workunit Transaction: %f" %avgWorkUnits)
print("Average Customer Wait Time: %f" %avgWaitTime)
print("Average Customers Unserved Per Day: %f" %avgUnserved)
print("Average Customers Served Per Work Day: %f" % avgCustServed)


f = open('statsfile.txt','a')

if usingPq != True:
    f.write('%d Loops with No Priority Queue, %d Tellers, ~N(5,0.5) Customer Distribution \n' % (totalLoops, tell.maxlen))
    f.write('Average Customer Workunit Transaction: %f \n' %avgWorkUnits)
    f.write('Average Customer Wait Time: %f \n'% avgWaitTime)
    f.write('Average Customers Unserved Per Day: %f \n' % avgUnserved)
    f.write('Average Customers Served Per Work Day: %f \n'% avgCustServed)
    f.write('\n')


    data = np.asarray(custWorkUnits)
    plt.hist(data, bins=15)
    plt.xlabel('Work Units')
    plt.ylabel('Number of Customers')
    plt.title('Distribution of Customers and Work Units')
    plt.savefig(fname="Distribution of Customers and Work Units")
    plt.clf()

    data = np.asanyarray(custServed)
    plt.hist(data)
    plt.xlabel('Customers Served')
    plt.ylabel('Frequency')
    plt.title('Customers Served Over %d Days (Iterations) without Priority Queue' %totalLoops)
    plt.savefig(fname='Customers Served Over %d Days (Iterations) without Priority Queue' %totalLoops)
    plt.clf()

    data = np.asanyarray(custUnserved)
    plt.hist(data)
    plt.xlabel('Customers Not Served')
    plt.ylabel('Frequency')
    plt.title('Customers Not Served Over %d Days (Iterations) without Priority Queue' %totalLoops)
    plt.savefig(fname='Customers Not Served Over %d Days (Iterations) without Priority Queue' %totalLoops)
    plt.clf()

    data = np.asanyarray(waitTimePerCust)
    plt.hist(data)
    plt.xlabel('Time Spent Waiting')
    plt.ylabel('Frequency')
    plt.title('Customer Waiting Times Over %d Days (Iterations) without Priority Queue' %totalLoops)
    plt.savefig(fname='Customer Waiting Times Over %d Days (Iterations) without Priority Queue' %totalLoops)
    plt.clf()

    data = np.asanyarray(custTotalArrivalTimes)
    plt.hist(data)
    plt.xlabel('Time of Arrival (8 hours = 480 Minutes)')
    plt.ylabel('Frequency')
    plt.title('Customer Arrival Times by Minute Over %d Days (Iterations)' %totalLoops)
    plt.savefig('Customer Arrival Times by Minute Over %d Days (Iterations)' %totalLoops)
    plt.clf()

    print("Customer Arrival Time Array Length: %d" %len(custTotalArrivalTimes))


else:
    f.write('%d Loops with a Priority Queue, %d Tellers, ~N(5,0.5) Customer Distribution \n' % (totalLoops, tell.maxlen))
    f.write('Average Customer Workunit Transaction: %f \n' %avgWorkUnits)
    f.write('Average Customer Wait Time: %f \n'% avgWaitTime)
    f.write('Average Customers Unserved Per Day: %f \n' % avgUnserved)
    f.write('Average Customers Served Per Work Day: %f \n'% avgCustServed)
    f.write('\n')

    data = np.asarray(custWorkUnits)
    plt.hist(data, bins=15)
    plt.xlabel('Work Units')
    plt.ylabel('Number of Customers')
    plt.title('Distribution of Customers and Work Units')
    plt.savefig(fname='Distribution of Customers and Work Units')
    plt.clf()

    data = np.asanyarray(custServed)
    plt.hist(data)
    plt.xlabel('Customers Served')
    plt.ylabel('Frequency')
    plt.title('Customers Served Over %d Days (Iterations) With Priority Queue' %totalLoops)
    plt.savefig(fname='Customers Served Over %d Days (Iterations) With Priority Queue' %totalLoops)
    plt.clf()

    data = np.asanyarray(custUnserved)
    plt.hist(data)
    plt.xlabel('Customers Not Served')
    plt.ylabel('Frequency')
    plt.title('Customers Not Served Over %d Days (Iterations) With Priority Queue' %totalLoops)
    plt.savefig(fname='Customers Not Served Over %d Days (Iterations) With Priority Queue' %totalLoops)
    plt.clf()

    data = np.asanyarray(waitTimePerCust)
    plt.hist(data)
    plt.xlabel('Time Spent Waiting')
    plt.ylabel('Frequency')
    plt.title('Customer Waiting Times Over %d Days (Iterations) With Priority Queue' %totalLoops)
    plt.savefig(fname='Customer Waiting Times Over %d Days (Iterations) With Priority Queue' %totalLoops)
    plt.clf()

    data = np.asanyarray(custTotalArrivalTimes)
    plt.hist(data)
    plt.xlabel('Time of Arrival (8 hours = 480 Minutes)')
    plt.ylabel('Frequency')
    plt.title('Customer Arrival Times by Minute Over %d Days (Iterations)' %totalLoops)
    plt.savefig(fname='Customer Arrival Times by Minute Over %d Days (Iterations)' %totalLoops)
    plt.clf()

    

f.close()
#########################################################################################################
