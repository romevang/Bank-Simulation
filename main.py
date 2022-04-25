# Romeo Vanegas
# CSCI 154 - Bank Simulation

from audioop import avg
from collections import deque
import copy
from scipy.stats import truncnorm
import numpy as np
import math
import matplotlib.pyplot as plt

# Customer and teller deque's, cust. maxlen is arbitrary
# Simluation requires maxlen 10 for teller deque

# Customer Deque
cust = deque(maxlen=160)
# Teller Deque
tell = deque(maxlen=10)

# Customer VIP Deque
custVip = deque(maxlen=15)
fastService = deque(maxlen=15)
# Array Holding Waiting Time of Customers
waitTimePerCust = []

#Array holding total customers not attended to at end of day
custUnserved = []

#Array holding number of customers served per iteration
custServed = []

# Stats Variables
low = 5
high = 15
mean = 5
std = 0.5

####Globals#####
# global for number of minutes in 8 hours (sim run time)
minutes = 480
# total number of work units per Teller
workUnits = 80
workUnitsTotal = 800
# total number of customers in 8 hours
totalCustomers = 160
# All teller windows busy counter
tellerBusyCounter = 0
# Customer Waiting Time
waitingTime = 0

# Flag if using Priority Queue
usingPq = False
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
    global waitTimePerCust
    # Pops from customer deque and assigns customer to teller IDX (swap)
    nextp = cust.popleft()
    tell[IDX].currentCust = nextp
    # Customer status set to helped (0)
    tell[IDX].currentCust.status = 0
    # Teller Status set to busy (1)
    tell[IDX].status = 1
    waitTimePerCust.append(tell[IDX].currentCust.waitTime)
    tell[IDX].currentCust.waitTime = 0
    # tell[IDX].tellStats()
    # print functions for debugging
    # print(tell[IDX].currentCust.wu,tell[IDX].currentCust.status,tell[IDX].currentCust.vip)

# Handles decrementing customer and teller work units with passage of time


def workUnitDec():
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
    counter = 0
    global customersServed
    while counter < tell.maxlen:
        if tell[counter].status == 1:
            if tell[counter].currentCust.wu <= 0:
                tell[counter].status = 0
                tell[counter].currentCust.status = 0
                customersServed += 1

            elif tell[counter].wu == 0:
                tell[counter].currentCust.vip = 1
                cust.appendleft(tell[counter].currentCust)
        counter += 1


# Handles increasing each customers wait time in line
def custWaitTime():
    for i in range(0, len(cust)):
        if cust[i].status == 1:
            cust[i].waitTime += 1

# Populates Teller line for simulation start - with maxlen(10) amount of tellers
# Each teller is set with max amount of workunits(80)


def tellerPopulate():
    counter = 0
    while counter < (tell.maxlen):
        tellerDefault = Teller(workUnits, 0, 0)
        tell.append(tellerDefault)
        counter += 1
    # print functions for debugging
    # print("Debug: Printing Teller Stats for Tellers 1 and 5")
    # tell[0].tellStats()
    # tell[4].tellStats()

# Polulates (append) Customer deque - one customer at a time
# Work units are randomly generated - values between 5-15
# All customers status is set to waiting (1) by default


def customerPopuluate(isPq):
    #workunits = randint(5,15)
    wu = get_truncated_normal(mean, std, low, high)
    units = wu.rvs(1)

    custDefault = Customer(round(units[0]), 1, 0, 0)
    if isPq:
        fastService.append(custDefault)
    else:
        cust.append(custDefault)
    # print function for debugging
    #print("Debut: Printing Customer 1's Stats")
    # cust[0].custStats()
    # cust[19].custStats()

# Moves customer from one teller window to another by deepcopying
# customer class values to the new teller window, the old teller's
# current customer class values are set to 0


def moveCurrentCust(old, new):
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
    # print functions for debugging
    print("Debug: Printing old and new teller stats after transfer")
    tell[old].tellStats()
    tell[new].tellStats()

# Checks for which teller window is available to help a customer
# Checks teller stats: 1 = busy or 0 = available


def openWindow():
    counter = 0
    global waitingTime
    if len(cust) > 0:
        while counter < (tell.maxlen):
            if (tell[counter].status == 0 and tell[counter].wu > 0 and cust[0].vip == 0):
                helpCustomer(counter)

                #print(f"Found one at: ", counter)
                break

            elif tell[counter].status == 0 and tell[counter].wu > 0 and cust[0].vip == 1:
                # moveCurrentCust(prevWindow,counter)
                helpCustomer(counter)
                break
            elif tell[counter].status == 1:
                counter += 1
                #print("Window Current Counter: %d" %counter)
            # else:
            #     print("Windows full")
            #     break
        waitingTime += 1

# Creates Normal Distribution of numbers


def get_truncated_normal(mean, std, low, high):
    return truncnorm(
        (low - mean) / std, (high - mean) / std, loc=mean, scale=std)

# Uniform distribution of numbers


def norm_dist():
    count = 0
    arry = []
    s.sort()
    while count < s.size:
        arry.append(math.floor(s[count]))
        count += 1
    return(arry)

############################################################################################
#################################### Main Program ##########################################
# tellerPopulate()
# customerPopuluate()

#cnt = 0
# while cnt < (cust.maxlen):
#     customerPopuluate()
#     cust[cnt].status = 1
#     cust[cnt].custStats()
#     cnt += 1

# cust.custStats()
# openWindow()
# helpCustomer(9)
# moveCurrentCust(9,0)


#------------------------------- My Main Testing----------------------------------#


for i in range(0,1000):

    # Initialization Step
    tellerPopulate()
    # for i in range(0,cust.maxlen):
    #     customerPopuluate(usingPq)

    custArrivalTimes = norm_dist()

    # for i in range(0,len(custArrivalTimes)):
    #     print(custArrivalTimes[i])
    # for i in range(0,cust.maxlen):
    #     print("Printing Stats of Customer: %d in Queue" % (i+1))
    #     cust[i].custStats()

    # 480 Minutes representative of 8 hours
    workDayTime = minutes
    timePassed = 0
    customersServed = 0
    laterArrival = False
    workUnitsTotal = 800
    print("--------Moving on to Main Loop--------")
    # print(len(custArrivalTimes))
    while workDayTime > 0 and customersServed < 160 and workUnitsTotal > 0:
        while True and len(custArrivalTimes) > 0:
            if custArrivalTimes[0] == timePassed:
                # print(custArrivalTimes[timePassed])
                customerPopuluate(usingPq)
                custArrivalTimes.pop(0)
            else:
                break

        openWindow()
        # print(len(cust))
        
        if (timePassed % 6 == 0 and timePassed > 0):
            workUnitDec()
            
        custTransaction()
        custWaitTime()
        workDayTime -= 1
        timePassed += 1
    #print("Work Units remaning %d" %workUnitsTotal)
# print(cust.maxlen)

    print("Work Units remaning %d" % workUnitsTotal)

    for i in range(0,len(tell)):
        if tell[i].status == 1:
            # print("Clearing Teller windows")
            cust.appendleft(tell[i].currentCust)
            tell[i].status = 0
    
    custUnserved.append(len(cust))
    custServed.append(customersServed)
    tell.clear()
    cust.clear()

# for i in range(0, len(cust)):
#     print("Cust %d" % (i+1))
#     cust[i].custStats()


# print("Printing Wait Times List")
# for i in range(0, len(waitTimePerCust)):
#     print("Customer %d : " % (i+1))
#     print(waitTimePerCust[i])

# print("Teller Window Status")
# for i in range(0,len(tell)):
#     print(tell[i].status)
#     print(tell[i].currentCust.wu)

# print("Total Number of Served Customers: %d" %customersServed)
print("Number of Customer Wait Times: %d" %len(waitTimePerCust))
# print("Simulation Finished")

avgWaitTime = np.average(waitTimePerCust)
avgUnserved = np.average(custUnserved)
print(avgWaitTime)
print("Average Customer Wait Time: %d" %avgWaitTime)
print("Average Customers Unserved Per Day: %d" %avgUnserved)

#############################################################
