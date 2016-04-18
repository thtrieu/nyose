from threading import Timer
from time import sleep

# Repeated Timer, for scheduling
# What's good? : change interval/ exit anytime!
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


# Use Repeated Timer to do jobs
class Clock(object):
	def __init__(self, interval = 5.0, notiSoon = 10, dayend = 2340):
		self.interval = interval
		self.notiSoon = notiSoon
		self.dayend = dayend
		self.exit = False

	def config(self, new_conf):
		if new_conf[0] > 0:
			self.interval = new_conf[0]
		if new_conf[1] > 0:
			self.notiSoon = new_conf[1]
		if new_conf[2] > 0:
			self.dayend = new_conf[2]
		if new_conf[3]:
			self.exit = True

	def checkAndDo(self, time, tenw, wtab, jnal, plan, mail):

		# Priority 01: Reminder
		time.update()
		comingStamp = plan.thereIsComingEvent(time, self.notiSoon)
		if not (comingStamp is False) and comingStamp < self.dayend:
			print 'sending notification at {} of {}'.format(
				time.timeStamp, time.tdSig)
			mail.send(plan.eventMailFormat(comingStamp))
			plan.noti.add(comingStamp)

		# Priority 02: Order from the master
		mail.update()
		if mail.received(): # Set latest processed received email Sigature here
			print 'received order at {} of {}'.format(
				time.timeStamp, time.tdSig)
			time.update()
			self.config(mail.conf())
			if mail.howto():
				mail.doHowto()
			if mail.plan():
				mail.doPlan(plan) # Send comfirmation inside
			if mail.jnal():
				mail.doJournal(plan, jnal, time) # Send confirmation inside
			if mail.wtab():
				mail.doWeekTable(wtab) # Send confirmation inside
			if mail.tenw():
				mail.doTenWeek(time, plan, tenw, self.dayend) # Send confirmation inside
			mail.allProcessed()

		# Priority 03: Day end, next day planning + revive
		time.update()
		if time.tdSig >= plan.newestPlanSig and time.timeStamp >= self.dayend:
			print "cleaning communications"
			mail.clean()
			print "log down jounal {}".format(time.tdSig)
			jnal.logdown(time) # anything happen next belong to next day.
			tenw.revive(time)
			print "sending notice list {}".format(time.tmrSig)
			mail.send(tenw.todayDlMailFormat(time, self.dayend))
			plan.sketch(time, wtab, tenw) # this set the newestPlan to a new one.
			print "sending plan {}".format(time.tmrSig)
			mail.send(plan.mailFormat())			

	def run(self, time, tenw, wtab, jnal, plan, mail):
		print "run ..."
		rt = RepeatedTimer(self.interval, self.checkAndDo,
			time, tenw, wtab, jnal, plan, mail)
		try:
			# Infinite loop until master send EXIT email.
			while not self.exit:
				sleep(4.9)
		finally:
			rt.stop()
			mail.clean()
			jnal.logdown(time)
			tenw.revive(time)
			mail.sendExit()