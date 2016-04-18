import os.path

class Plan(object):
	def __init__(self):

		# get functions involve accessing to files
		self.newestPlanSig = self.getNewestPlanSig()
		self.newestPlanList = self.getPlanList(self.newestPlanSig)
		self.keys = self.newestPlanList.keys()
		self.keys.sort()
		self.noti = set([])

	def dump(self, dateSig):
		with open('plans/' + dateSig, 'w') as f:
			for key in self.newestPlanList:
				for content in self.newestPlanList[key]:
					writedown = "{} {}\n".format(
						key, content)
					f.write(writedown)

	def getNewestPlanSig(self): #Only use for initialisation
		FIRST_DATE = '0000-00-00'
		allPlan = os.listdir('plans')
		if allPlan == list():
			with open('plans/' + FIRST_DATE, 'w') as f:
				f.write('')
			return FIRST_DATE
		else:
			allPlan.sort()
			return allPlan[len(allPlan)-1]

	def getPlanList(self, planSig):
		with open('plans/' + planSig,'r') as f:
			pl = f.readlines()
		planList = dict()
		planList['TODO'] = list()
		for point in pl:
			p = point.strip()
			p = p.split()
			content = ' '.join(p[1:])
			if p[0] != 'TODO':
				if int(p[0]) in planList:
					planList[int(p[0])].append(content)
				else:
					planList[int(p[0])] = [content]
			else:
				planList['TODO'].append(content)
		return planList

	def thereIsComingEvent(self, time, notiSoon):
		stamps = self.keys
		timeStamp = time.timeStamp
		for stamp in stamps:
			if stamp == 'TODO': continue
			coming = stamp > timeStamp
			if not coming: return False
			within = time.minus(stamp, timeStamp) <= notiSoon
			notyet = not (stamp in self.noti)
			if within and notyet:
				return stamp
		return False

	def eventMailFormat(self, stamp):
		mail = dict()
		mail['title'] = 'event'
		mail[stamp] = self.newestPlanList[stamp]
		mail['todos'] = self.newestPlanList['TODO']
		return mail

	def sketch(self, time, wtab, tenw):
		self.dump(self.newestPlanSig)
		planList = wtab.getPlan(time.nextwday)
		planList['TODO'] = tenw.todos(time.tmrSig)
		with open('plans/' + time.tmrSig,'w') as f:
			for key in planList.keys():
				for item in planList[key]:
					f.write(' '.join([str(key), item]))
					f.write('\n')

		#-RESET all
		self.newestPlanSig = time.tmrSig
		self.newestPlanList = planList
		self.keys = planList.keys()
		self.keys.sort()
		self.dump(self.newestPlanSig)
		self.noti = set([])

	def mailFormat(self, planDate = ''):
		if planDate == '':
			planDate = self.newestPlanSig
		mail = dict()
		if planDate == self.newestPlanSig:
			planList = self.newestPlanList
		else:
			planList = self.getPlanList(planDate)
		mail = planList
		mail['title'] = 'plan {}'.format(planDate)
		return mail

	def delete(self, order): # return a mailPart
		mail = dict()
		if len(order) == 1:
			todo_i = int(order[0])-1
			deleted = self.newestPlanList['TODO'][todo_i]
			del self.newestPlanList['TODO'][todo_i]
			mail['plan'] = "deleted todo #{}: '{}'".format(
				todo_i+1, deleted)
		else:
			time_i = ord(order[0])-97
			key = self.keys[time_i]
			deleted = self.newestPlanList[key][int(order[1])-1]
			del self.newestPlanList[key][int(order[1])-1]
			mail['plan'] = "deleted timed {}#{}: '{}'".format(
				key, order[1], deleted)
		return mail

	def add(self, order):
		mail = dict()
		added = order[1]
		if order[0] == 'todo':
			self.newestPlanList['TODO'].append(added)
			mail['plan'] = "added '{}' into todo".format(added)
		else:
			if len(order[0]) == 1:
				time_i = ord(order[0])-97
				key = self.keys[time_i]
			else:
				key = int(order[0])
			if key in self.newestPlanList:
				self.newestPlanList[key].append(added)
			else:
				self.newestPlanList[key] = [added]
				self.keys.append(key)
				self.keys.sort()
			mail['plan'] = "added '{}' into {}".format(added, key)
		return mail

	def change(self, order):
		mail = dict()
		if len(order) == 2 :
			todo_i = int(order[0])-1
			change = self.newestPlanList['TODO'][todo_i]
			to = order[1]
			self.newestPlanList['TODO'][todo_i] = to
			mail['plan'] = "changed todo #{}: from '{}' to '{}'".format(
				todo_i+1, change, to)
		else:
			try:
				time_i = ord(order[0])-97
				key = self.keys[time_i]
			except:
				key = int(order[0])			
			change = self.newestPlanList[key][int(order[1])-1]
			to = order[2]
			self.newestPlanList[key][int(order[1])-1] = to
			mail['plan'] = "changed timed {}#{}: from '{}' to '{}'".format(
				key, order[1], change, to)
		return mail

	def move(self, order):
		mail = dict()
		todo_i = int(order[0])-1
		content = self.newestPlanList['TODO'][todo_i]
		del self.newestPlanList['TODO'][todo_i]

		if len(order[1]) == 1:
			time_i = ord(order[0])-97
			key = self.keys[time_i]	
		else:
			key = int(order[1])
			if key in self.newestPlanList:
				self.newestPlanList[key].append(content)
			else:
				self.newestPlanList[key] = [content]
				self.keys.append(key)
				self.keys.sort()
		mail['plan'] = "Moved todo #{}: '{}' to timed {}".format(
			todo_i, content, key)
		return mail

	def finish(self, order):
		todo_i = int(order[0])-1
		self.newestPlanList['TODO'][todo_i] += ' [DONE]'