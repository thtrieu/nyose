from time import sleep
import sys
from Mail import *

class Clock(object):
	def __init__(self, debug = False, interval = 5.0, 
		notiSoon = 10, dayend = 2340, refMail = 60):
		self.interval = interval
		self.notiSoon = notiSoon
		self.dayend = dayend
		self.refMail = refMail
		self.debug = debug
		self.sent = False
		self.exit = False
		self.mailReInit = False
		self.pwIssue = False

	def config(self, new_conf):
		if new_conf[0] > 0:
			print "change interval"
			self.interval = int(new_conf[0])
		if new_conf[1] > 0:
			print "change noti interval"
			self.notiSoon = int(new_conf[1])
		if new_conf[2] > 0:
			print "change dayend point"
			self.dayend = int(new_conf[2])
		if new_conf[3] > 0:
			print "change refresh Mail interval"
			self.refMail = int(new_conf[3])
		if new_conf[4]:
			print "received terminal signal"
			self.exit = True

	def checkAndDo(self, time, tenw, wtab, jnal, plan, mail):

		# Priority 01: Reminder
		time.update()
		comingStamp = plan.thereIsComingEvent(time, self.notiSoon)
		if not (comingStamp is False) and comingStamp < self.dayend:
			print 'send notification at {} of {}'.format(
				time.timeStamp, time.tdSig)
			mail.send(plan.eventMailFormat(comingStamp))
			plan.noti.add(comingStamp)

		# Priority 02: Order from the master
		mail.update()
		if mail.received(): # Set latest processed received email Sigature here
			time.update()
			print 'received order at {} of {}'.format(
				time.timeStamp, time.tdSig)
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
			print "all processed"

		# Priority 03: Day end, next day planning + revive
		time.update()
		dayendNoPlan = time.timeStamp >= self.dayend and time.tdSig >= plan.newestPlanSig
		daybeingNoPlan = time.timeStamp < self.dayend and time.tdSig > plan.newestPlanSig
		# If both is false, planFor is for today
		planFor = dayendNoPlan * time.tmrSig + (not dayendNoPlan) * time.tdSig
		if dayendNoPlan or daybeingNoPlan:
			print "log down journal {}".format(time.tdSig)
			jnal.logdown(time) # anything happen next belong to next day.
			print "dump plan {}".format(plan.newestPlanSig)
			plan.dump()
			print "clean communications"
			mail.clean()
			plan.sketch(time, wtab, tenw, self.dayend) # this set the newestPlan to a new one.
			self.sent = False
		
		# Basically system just start = day end - log down.
		# self.sent is the bridge.
		# Priority 04: System just start
		if not self.sent:
			if time.timeStamp >= self.dayend:
				leftover = time.tdSig
			else:
				leftover = time.past(1)
			mail.send(plan.leftoverMailFormat(leftover))
			print "send notice list {}".format(planFor)
			tenw.revive(planFor) # because tenw.todayNotice is not for dump and load at __init__
			mail.send(tenw.todayDlMailFormat(time, self.dayend))
			
			print "send plan {}".format(planFor)
			mail.send(plan.mailFormat())
			self.sent = True

	def run(self, time, tenw, wtab, jnal, plan):
		mail = Mail(self.mailReInit, self.debug)
		print 'mail: On'
		print 'enter loop'
		time.update()
		start = time.timeStamp
		while not self.exit:
			try:
			# Infinite loop until master send EXIT email.
				self.checkAndDo(time, tenw, wtab, jnal, plan, mail)
				if time.minus(time.timeStamp, start) >= self.refMail:
					print("time to refresh mail connection")
					# For safety, not necessary dump plan and jnal here
					plan.dump()
					jnal.logdown(time)
					self.mailReInit = True
					break
				sleep(self.interval)
			except:
				if self.debug:
					raise
				err = str(sys.exc_info()[0])
				print '\nERROR: {}. Log down'.format(err)
				time.update()
				with open('ERRORLOG','a') as f:
					f.write('{}: {}\n'.format(time.timeStamp, err))
				print "save plan and journal"
				# For safety, not necessary dump plan and jnal here
				plan.dump()
				jnal.logdown(time)
				if err == "<class 'httplib2.ServerNotFoundError'>":
					print "Big issue. sleep for long and reinitialise"
					sleep(self.interval * 20)
					self.exit = True
					self.pwIssue = True
				else:
					print 'reinitialise mail'
					self.mailReInit = True
				break
		if self.exit and not self.pwIssue:
			print "clean and say goodbye"
			mail.clean()
			mail.sendExit()
		print 'mail: Off'