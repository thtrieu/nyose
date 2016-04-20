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
			del plan.newestPlanList['TODO'][todo_i]
			mail['plan'] = "todo #{}: '{}' is migrated".format(
				todo_i + 1, content)
		if len(order) == 2:
			if len(order[0]) == 1:
				time_i = ord(order[0])-97
				key = plan.keys[time_i]
			else:
				key = int(order[0])
			content = plan.newestPlanList[key][int(order[1])-1]
			del plan.newestPlanList[key][int(order[1])-1]
			if len(plan.newestPlanList[key]) == 0:
				del plan.newestPlanList[key]
				plan.keys = plan.newestPlanList.keys()
				plan.keys.sort()
			mail['plan'] = "timed {}#{}: '{}' is migrated".format(
				key, order[1], content)
		if time.tmrSig in self.tenw:
			self.tenw[time.tmrSig]['TODO'].append(content)
		else:
			self.tenw[time.tmrSig] = {'TODO': [content], 'DEADLINE': []}
		mail['tenw'] = "{} received todo '{}'".format(
			time.tmrSig, content)
		self.dump()
		return mail

	def dateRegul(self, date, tdSig):
		dates = date.split('/')
		day = dates[0]
		month = dates[1]
		if len(dates) == 2:
			year = tdSig.split('-')[0]
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
			date = self.dateRegul(order[0], time.tdSig)
			content = order[1]

		if date in self.tenw:
			self.tenw[date]['TODO'].append(content)
		else:
			self.tenw[date] = {'TODO': [content], 'DEADLINE': []}
		mail['tenw'] = "{} received todo '{}'".format(
			date, content)
		self.dump()
		return mail

	def deadline(self, tdSig, order):
		mail = dict()
		date = self.dateRegul(order[0], tdSig)
		if date == tdSig:
			mail['plan_changed'] = True
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

	def submitted(self, tdSig, order):
		mail = dict()
		for i in range(0, len(order)):
			order_i = int(order[i])	- 1
			content = self.todayNotice[order_i]
			if content[0] == tdSig:
				mail['plan_changed'] = True
			self.todayNotice[order_i] = (content[0],content[1],True)
			temp = self.tenw[content[0]]['DEADLINE'][content[1]][0]
			self.tenw[content[0]]['DEADLINE'][content[1]] = (temp, True)
		
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

	def delete(self, tdSig, order):
		mail = dict()
		date = self.dateRegul(order[0], tdSig)
		if date not in self.tenw:
			mail['tenw'] = '{} is empty, nothing to be deleted'.format(
				date)
			self.dump()
			return mail
		if len(order) == 1:
			if date == tdSig and self.tenw[date]['DEADLINE'] != []:
				mail['plan_changed'] = True
			del self.tenw[date]
			mail['tenw'] = 'deleted whole {}'.format(date)
			self.dump()
			return mail
		if order[1].lower() == 'td':
			kind = 'TODO'
		else:
			kind = 'DEADLINE'
		if len(order) == 2:
			if date == tdSig and self.tenw[date]['DEADLINE'] != []:
				mail['plan_changed'] = True
			self.tenw[date][kind] = []
			mail['tenw'] = "{} of {} is emptied".format(
				kind, date)
			if self.tenw[date] == {'TODO':[], 'DEADLINE':[]}:
				del self.tenw[date]
				mail['tenw'] += ", turn out {} is now empty, deleted it.".format(date)
			self.dump()
			return mail
		num = int(order[2]) - 1
		if not num < len(self.tenw[date][kind]):
			mail['tenw'] = "{} of {} does not have at least {} elements".format(
				kind, date, num + 1)
			return mail
		if date == tdSig and kind == 'DEADLINE':
			mail['plan_changed'] = True
		del self.tenw[date][kind][num]
		mail['tenw'] = "{}#{} of {} is removed".format(
			kind, num+1, date)
		if self.tenw[date] == {'TODO':[], 'DEADLINE':[]}:
			del self.tenw[date]
			mail['tenw'] += ", turn out {} is now empty, deleted it.".format(date)
		self.dump()
		return mail

	def query(self, time, order):
		mail = dict()
		if len(order) == 1:
			if order[0].lower() == 'ten':
				return self.calendar()
			else:
				from_str = to_str = self.dateRegul(order[0],time.tdSig)
		if len(order) == 2:
			from_str = self.dateRegul(order[0],time.tdSig)
			to_str = self.dateRegul(order[1],time.tdSig)
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
			return content

	def dlns(self, dateSig):
		if dateSig not in self.tenw:
			return []
		else:
			content = []
			for dln in self.tenw[dateSig]['DEADLINE']:
				if not dln[1]:
					content.append(
						'{} [NOT YET SUBMITTED]'.format(dln[0]))
				else:
					content.append(
						'{} [SUBMITTED]'.format(dln[0]))
			return content

	def calendar(self):
		mail = dict()
		mail['transfer'] = 'next ten weeks calendar'
		mail['message'] = 'not yet implemented'
		return mail