# Bank-Simulation Project - Spring 2022
This project was for my [CSCI 154](https://www.fresnostate.edu/catalog/courses-by-department/computer-science/#csci154) - Simulation course at CSU - Fresno.

Prompt:
***Simulate a bank with 10 windows with the same efficiency of 10 wu/hr. Assume that 160 customers arrive in a working day (of 8 hours) following a uniform distribution. The work-units of the customers follow a normal distribution ~N(5,0.5) truncated within the range [5,15].***

To execute, run *main.py* in a terminal or your favorite integrated development environment. Code was written using python 3.8 but will execute on newer versions as well.

These global variables will affect results and execution time (especially totalLoops):
```
*Maxiumum length of the deque*
cust = deque(maxlen=160)

Size of the VIP line
fastService = deque(maxlen=20)

*Number of teller windows*
tellerTotal = 10

*Total number of iterations*
totalLoops = 5000
```

5000 iterations on a 2019 Macbook pro (Intel Core i7 9750H) took almost 5 minutes. At the end of the run, it will produce graphs. Therefore, make sure you save them before your next iteration. Otherwise they will be overwritten. In linux and MacOS they will be found in the **Home** folder. In windows, I'm not sure, haven't done enough testing. 

**Note**: *The normal distribution is calculated with integers instead of decimals, further debugging is required and is likely skewing simulation results by a tracable amount.*

##Screenshots of simulation run: 1000 iterations(days).
![Title](githubLinkToPhoto?raw=true)
