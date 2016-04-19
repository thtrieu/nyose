from Clock import *
from WeekTable import *
from TenWeek import *
from Journal import *
from Plan import *
from Time import *

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

while not tick.exit:
	tick.run(time, tenw, wtab, jnal, plan)

print "save plan and journal"
plan.dump()
jnal.logdown(time)
print "wtab, jnal, plan, time, tenw, tick: Off"
print "terminate"