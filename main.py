import Clock as cl
import WeekTable as wt
import TenWeek as tw
import Journal as jn
import Plan as pl
import Time as tm
import Mail as ml
import sys

if __name__ == "__main__":
	wtab = wt.WeekTable() # The template for planner
	jnal = jn.Journal() # The Journal
	plan = pl.Plan() # The planner
	time = tm.Time() # Lazy time tracker
	tenw = tw.TenWeek() # The long run
	print('wtab, jnal, plan, time, tenw: On')
	if len(sys.argv) == 1:
		debug = False
	else:
		debug = True
		print('debug mode')
	tick = cl.Clock(debug) # The loop
	print('tick: On')

	while not tick.exit:
		# Mail receive a special treatment since 
		tick.run(ml, time, tenw, wtab, jnal, plan)
		if tick.update:
			# TODO: Run git synchorise here
			ml = reload(ml)
			tm = reload(tm)
			tw = reload(tw)
			wt = reload(wt)
			jn = reload(jn)
			pl = reload(pl)
			cl = reload(cl)
			print ('all code reloaded')
			time = tm.Time()
			tenw = tw.TenWeek()
			wtab = wt.WeekTable()
			jnal = jn.Journal()
			plan = pl.Plan()
			save = tick.dump()
			tick = cl.Clock(debug)
			tick.load(save)
			del save
			tick.update = 'done'

	print "save plan and journal"
	plan.dump()
	jnal.logdown(time)
	print "wtab, jnal, plan, time, tenw, tick: Off"
	print "terminate"