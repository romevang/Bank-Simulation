##Romeo Vanegas
##Bank Simluation - CSCI 154

from random import randint
from collections import deque
import copy

#Customer and teller deque's, cust. maxlen is arbitrary
#Simluation requires maxlen 10 for teller deque

#Customer Deque
cust = deque(maxlen=20)
#Teller Deque
tell = deque(maxlen=10)

####Globals#####
#global for number of minutes in 8 hours (sim run time)
minutes = 480
#total number of work units per Teller
workUnits = 80
#total number of customers in 8 hours
totalCustomers = 160
#All teller windows busy counter
tellerBusyCounter = 0

####################################################################
##################### Customer/Teller classes ######################

class Customer:
    def __init__(self, wu, status,vip):
        ##Initialize member varibles
        #Work units variable
        self.wu = wu
        # Customer status 0 = helped and 1 = waiting
        self.status = status
        # VIP (priority) flag is set to 0 unless given higher priority then 1
        self.vip = vip

    def custStats(self):
        ##Customer Statistics
        print(f"{self.wu} work units")
        print(f"{self.status} current status")
        print(f"{self.vip} current VIP status\n")

##Teller Class
class Teller:
    def __init__(self, wu, status,currentCust):
        ##Initialize member varibles
        # Work units variable
        self.wu = wu
        # Teller status 0 = idle or 1 = busy
        self.status = status
        # Current customer class varibles (workunits,status,vip)
        self.currentCust = currentCust

    def tellStats(self):
        ##Teller statistics
        print(f"{self.wu} work units")
        print(f"{self.status} current status\n")

########################################################
##################### Functions ########################
########################################################
#When teller is avaiable, calls next customer. Also sets 
#Teller status to Busy (1). IDX passes the index of avaiable teller.
def helpCustomer(IDX):
    #Pops from customer deque and assigns customer to teller IDX (swap)
    nextp = cust.pop()
    tell[IDX].currentCust = nextp
    #Customer status set to helped (0)
    tell[IDX].currentCust.status = 0
    #Teller Status set to busy (1)
    tell[IDX].status = 1
    tell[IDX].tellStats()
    #print functions for debugging
    #print(tell[IDX].currentCust.wu,tell[IDX].currentCust.status,tell[IDX].currentCust.vip)

#Populates Teller line for simulation start - with maxlen(10) amount of tellers
#Each teller is set with max amount of workunits(80)
def tellerPopulate():
    counter = 0
    while counter < (tell.maxlen):
        tellerDefault = Teller(workUnits,0,0)
        tell.append(tellerDefault)
        counter += 1
    #print functions for debugging
    tell[0].tellStats()
    tell[4].tellStats()

#Polulates (append) Customer deque - one customer at a time
#Work units are randomly generated - values between 5-15
#All customers status is set to waiting (1) by default
def customerPopuluate():
    workunits = randint(5,15)
    custDefault = Customer(workunits,1,0)
    cust.append(custDefault)
    ##print function for debugging
    cust[0].custStats() 

#Moves customer from one teller window to another by deepcopying
#customer class values to the new teller window, the old teller's
#current customer class values are set to 0
def moveCurrentCust(old,new):
    #New teller accepts customer from old teller (swap)
    newt = copy.deepcopy(tell[old].currentCust)
    tell[new].currentCust = newt
    #Updates previous teller currentCust class varibles to 0
    #Sets teller status to idle
    tell[new].status = 1
    tell[old].status = 0
    tell[old].currentCust.wu = 0
    tell[old].currentCust.status = 0
    tell[old].currentCust.vip = 0
    #print functions for debugging
    tell[old].tellStats()
    tell[new].tellStats()

#Checks for which teller window is available to help a customer
#Checks teller stats: 1 = busy or 0 = available
def openWindow():
    counter = 0
    while counter < (tell.maxlen):
        if (tell[counter].status == 0 and tell[counter].wu > 0):
            helpCustomer(counter)
            print(f"Found one at: ", counter)
            break
        elif tell[counter].status == 0:
            counter += 1
            print(counter)
        else:
            print("Windows full")
            break
 
############################################################################################
#################################### Main Program ##########################################
tellerPopulate()
customerPopuluate()
cnt = 0
while cnt < (tell.maxlen):
    tell[cnt].status = 1
    cnt += 1

openWindow()
#helpCustomer(9)
#moveCurrentCust(9,0)


#############################################################


