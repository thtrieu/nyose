from WeekTable import *
from TenWeek import *
from Journal import *
from Plan import *
from Time import *
from Clock import *
from Mail import *

# a system that regard 2330 as dayend.
wtab = WeekTable() # The template for planner
print('wtab: On')
jnal = Journal() # The Journal
print('jnal: On')
plan = Plan() # The planner
print('plan: On')
time = Time() # Lazy time tracker
print('time: On')
tenw = TenWeek() # The long run
print('tenw: On')
tick = Clock() # The loop
print('tick: On')
mail = Mail() # The communicator
print('mail: On')
tick.run(time, tenw, wtab, jnal, plan, mail)