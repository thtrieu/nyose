import cPickle as pickle
import urllib2 as web
import re
import os
from time import sleep

class TenWeek(object):

	def __init__(self):
		self.file = 'tenw.PICKLE'
		self.tenw = dict()
		self.todayNotice = list()
		self.load()
		self.moodle()
		self.dump()

	def load(self):
		if not os.path.exists(self.file):
			with open(self.file, 'wb') as f:
				pickle.dump([self.tenw],f,protocol=-1)
		else:
			with open(self.file, 'rb') as f:
				self.tenw = pickle.load(f)[0]

	def dump(self):
		with open(self.file, 'wb') as f:
			pickle.dump([self.tenw],f,protocol=-1)

	def moodle(self, console = False):
		with open('calenda','r') as f:
			calenda = f.read()
		success = False
		while success is False:
			try:
				calenda = web.urlopen(calenda)
				if calenda.getcode() == 200:
					success = True
					print "revived moodle information"
			except Exception, e:
				print e
				sleep(5)
				print "error retrieving moodle deadlines, trying again..."
		
		events = calenda.read().split('\n')
		# Sweeping variables
		dls = dict()
		smr = str()
		tag = str()
		dln = str()

		for event in events:
			event = event.strip()
			event = re.sub(r"\\","",event)
			event = re.sub(r"\r","",event)
			event = re.sub(r"\t","",event)
			event = re.sub(r"\s{2,}"," ",event)
			event = event.split(':')
			if event[0] == 'SUMMARY':
				smr = ''.join(event[1:])
			if event[0] == 'DESCRIPTION':
				patch = ''.join(event[1:])
				if patch != smr:
					smr += ': ' + patch
			if event[0] == 'CATEGORIES':
				tag = event[1][:5]
			if event[0] == 'DTSTART':
				date = event[1][:8]
				year = date[:4]
				month = date[4:6]
				day = date[6:8]
				dln = '-'.join([year, month, day])
			if event == ['END','VEVENT']:
				content = '>> '.join([tag,smr])
				if console:
					print dln, content
				if dln in self.tenw:
					avail = self.tenw[dln]['DEADLINE']
					if (content, True) in avail or (content, False) in avail:
						pass
					else:
						self.tenw[dln]['DEADLINE'].append((content, False))
				else:
					self.tenw[dln] = {'TODO':[], 'DEADLINE': [(content, False)]}
		

	def revive(self, timeSig):
		self.moodle()
		marks = self.tenw.keys()
		marks.sort()
		i = 0
		while marks[i] < timeSig: i += 1
		marks = marks[i:]
		self.todayNotice = list()
		for mark in marks:
			dlns = self.tenw[mark]['DEADLINE']
			for i in range(0,len(dlns)):
				dln = dlns[i]
				if not dln[1]:
					self.todayNotice.append((mark, i, False))
		self.dump()

	def migrate(self, time, plan, order):
		mail = dict()
		if len(order) == 1:
			todo_i = int(order[0]) - 1
			content = plan.newestPlanList['TODO'][todo_i]
			plan.newestPlanList['TODO'][todo_i] += ' [MIGRATED]'
			mail['plan'] = "todo #{}: '{}' is migrated".format(
				todo_i + 1, content)
		if len(order) == 2:
			time_i = ord(order[0])-97
			key = plan.newestPlanList.keys[time_i]
			content = plan.newestPlanList[key][int(order[1])-1]
			plan.newestPlanList[key][int(order[1])-1] += ' [MIGRATED]'
			mail['plan'] = "timed {}#{}: '{}' is migrated".format(
				key, order[1], content)

		if time.tmrSig in self.tenw:
			self.tenw[time.tmrSig]['TODO'].append(content)
		else:
			self.tenw[time.tmrSig] = {'TODO': [content], 'DEADLINE': []}
		mail['tenw'] = "{} received todo '{}'".format(
			tmrSig, content)
		self.dump()
		return mail

	def dateRegul(self, date, time):
		dates = date.split('/')
		day = dates[0]
		month = dates[1]
		if len(dates) == 2:
			year = time.tmrSig.split('-')[0]
		else:
			year = dates[2]
		if len(day) == 1:
			day = '0'+ day
		if len(month) == 1:
			month = '0'+ month
		date = '-'.join([year, month, day])	
		return date

	def pin(self, time, order):
		mail = dict()
		if len(order) == 1:
			date = time.tmrSig
			content = order[0]
		if len(order) == 2:
			date = self.dateRegul(order[0], time)
			content = order[1]

		if date in self.tenw:
			self.tenw[date]['TODO'].append(content)
		else:
			self.tenw[date] = {'TODO': [content], 'DEADLINE': []}
		mail['tenw'] = "{} received todo '{}'".format(
			date, content)
		self.dump()
		return mail

	def deadline(self, time, order):
		mail = dict()
		date = self.dateRegul(order[0], time)
		content = order[1]
		index = int()
		if date in self.tenw:
			self.tenw[date]['DEADLINE'].append((content,False))
			index = len(self.tenw[date]['DEADLINE']) - 1
		else:
			self.tenw[date] = {'TODO': [], 'DEADLINE': [(content,False)]}
			index = 0
		
		# Insert to today's notice list
		if self.todayNotice != list():
			pos = 0
			while self.todayNotice[pos][0] < date:
				pos += 1
			self.todayNotice.insert(pos, (date, index, False))
		else:
			self.todayNotice = [(date, index, False)]

		mail['tenw'] = "{} received deadline '{}'".format(
			date, content)
		self.dump()
		return mail

	def submitted(self, order):
		mail = dict()
		for i in range(0, len(order)):
			order_i = int(order[i])	- 1
			content = self.todayNotice[order_i]
			self.todayNotice[order_i] = (content[0],content[1],True)
			self.tenw[content[0]]['DEADLINE'][content[1]][1] = True
		
		mail['tenw'] = "submitted '{}' deadlines".format(
			len(order))
		self.dump()
		return mail

	def todayDlMailFormat(self, time, dayend):
		mail = dict()
		if time.timeStamp >= dayend:
			date = time.tmrSig
		else:
			date = time.tdSig
		mail['title'] = 'deadlines notices of {}'.format(date)
		noticeList = list()
		for dl in self.todayNotice:
			content = "{} ({}d): ".format(
				dl[0], time.substract(dl[0],date))
			content += "{}".format(
				self.tenw[dl[0]]['DEADLINE'][dl[1]][0])
			content += int(dl[2])*' [SUBMITTED]'
			noticeList.append(content)
		mail['notice'] = noticeList
		return mail

	def query(self, time, order):
		mail = dict()
		if len(order) == 1:
			from_str = to_str = self.dateRegul(order[0],time)
		if len(order) == 2:
			from_str = self.dateRegul(order[0],time)
			to_str = self.dateRegul(order[1],time)
		dayList = time.daySeri(from_str, to_str)
		content = ['events from {} to {}:'.format(
			from_str, to_str)]
		for day in dayList:
			if day in self.tenw:
				content.append('\n[[{}]]:'.format(day))
				todos = self.tenw[day]['TODO']
				if todos != list():
					content.append('  (todos)')
					for todo in todos:
						content.append('. {}'.format(todo))
				dlns = self.tenw[day]['DEADLINE']
				if dlns != list():
					content.append('  (deadlines)')
					for dln in dlns:
						content.append('. {}'.format(
							dln[0])+int(dln[1])*' [SUBMITTED]')
		if len(content) == 1: content.append('nothing')
		if len(content) >= 15:
			mail['transfer'] = content[0]
		mail['tenw'] = '\n\t'.join(content)
		return mail

	def todos(self, dateSig):
		if dateSig not in self.tenw:
			return []
		else:
			content = [] + self.tenw[dateSig]['TODO']
			for dln in self.tenw[dateSig]['DEADLINE']:
				if not dln[1]:
					content.append(
						'<+deadline+> {}'.format(dln[0]))
			return content

	def calendar(self):
		mail = dict()
		mail['transfer'] = 'next ten weeks calendar'
		mail[''] = 'not yet implemented'
		return mail