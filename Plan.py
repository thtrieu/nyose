import os.path

class Plan(object):
	def __init__(self):

		# get functions involve accessing to files
		self.newestPlanSig = self.getNewestPlanSig()
		self.newestPlanList = self.getPlanList(self.newestPlanSig)
		self.keys = self.newestPlanList.keys()
		self.keys.sort()
		self.noti = set([])
		
	def dump(self):
		dateSig = self.newestPlanSig
		with open('plans/' + dateSig, 'w') as f:
			for key in self.keys:
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
		file = 'plans/' + planSig
		if not os.path.exists(file):
			with open(file,'w') as f:
				f.write('')
		with open(file,'r') as f:
			pl = f.readlines()
		planList = dict()
		planList['TODO'] = list()
		planList['DEADLINE'] = list()
		for point in pl:
			p = point.strip()
			p = p.split()
			content = ' '.join(p[1:])
			try:
				key = int(p[0])
				if key in planList:
					planList[key].append(content)
				else:
					planList[key] = [content]
			except:
				key = p[0]
				planList[key].append(content)
		return planList

	def thereIsComingEvent(self, time, notiSoon):
		stamps = self.keys
		timeStamp = time.timeStamp
		for stamp in stamps:
			if stamp in ['TODO','DEADLINE']: continue
			coming = stamp > timeStamp
			if not coming: continue
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
		mail['deadlines'] = self.newestPlanList['DEADLINE']
		return mail

	def sketch(self, time, wtab, tenw, dayend):
		if time.timeStamp < dayend:
			wday = time.wday
			dSig = time.tdSig
		else:
			wday = time.nextwday
			dSig = time.tmrSig
		planList = wtab.getPlan(wday)
		planList['TODO'] = tenw.todos(dSig)
		planList['DEADLINE'] = tenw.dlns(dSig)
		self.newestPlanSig = dSig
		self.newestPlanList = planList
		self.keys = planList.keys()
		self.keys.sort()
		self.dump()
		self.noti = set([])

	def leftoverMailFormat(self, planDate = ''):
		if planDate == '':
			planDate = self.newestPlanSig
		mail = dict()
		if planDate == self.newestPlanSig:
			planList = self.newestPlanList
		else:
			planList = self.getPlanList(planDate)
		key = 'not marked done in {}'.format(planDate)
		mail[key] = list()
		todos = planList['TODO']
		for todo in todos:
			if '[DONE]' not in todo:
				mail[key].append(todo)
		if mail[key] == list():
			del mail[key]
			mail['message'] = ['good job, no leftover at all ;)']
		mail['title'] = 'what is left from {}?'.format(planDate)
		return mail

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
			if len(self.newestPlanList[key]) == 0:
				del self.newestPlanList[key]
				del self.keys[time_i]
			mail['plan'] = "deleted timed {}#{}: '{}'".format(
				key, order[1], deleted)
		return mail

	def move(self, order):
		print order
		mail = dict()
		try: # Move todo -> somewhere
			todo_i = int(order[0])-1
			if todo_i > 100: #commit suicide
				temp = int('a')
			content = self.newestPlanList['TODO'][todo_i]
			del self.newestPlanList['TODO'][todo_i]
			try: # Merge todos
				todo_j = int(order[1])-1
				if todo_j > 100: #commit suicide
					temp = int('a')
				if (todo_i == todo_j):
					self.newestPlanList['TODO'].insert(todo_i, content)
					mail['plan'] = "move from {} to {}??".format(todo_i, todo_j)
				else:
					inc = int(todo_j > todo_i)
					todo_j -= inc
					self.newestPlanList['TODO'][todo_j] += '; ' + content
					mail['plan'] = "merged todo {} and {}".format(
						todo_i+1, todo_j + inc + 1)
			except: # Move todo -> timed
				if len(order[1]) == 1:
					time_i = ord(order[1])-97
					key = self.keys[time_i]	
				else:
					key = int(order[1])
				if len(order) == 2: # append
					if key in self.newestPlanList:
						self.newestPlanList[key].append(content)
					else:
						self.newestPlanList[key] = [content]
						self.keys.append(key)
						self.keys.sort()
					mail['plan'] = "moved todo #{}: '{}' to timed {}".format(
						todo_i+1, content, key)
				else: # merge
					num = int(order[2])-1
					self.newestPlanList[key][num] += '; ' + content
					mail['plan'] = "merged todo {} and timed {}#{}".format(
						todo_i+1, key, num+1)

		except: # Move timed -> somewhere
			if len(order[0]) == 1:
				time_i = ord(order[0])-97
				key = self.keys[time_i]
			else:
				key = int(order[0])
			num = int(order[1])-1
			content = self.newestPlanList[key][num]
			del self.newestPlanList[key][num]
			if len(self.newestPlanList[key]) == 0:
				del self.newestPlanList[key]
				self.keys = self.newestPlanList.keys()
				self.keys.sort()
			if len(order) == 2: # Move timed -> TODO
				self.newestPlanList['TODO'].append(content)
				mail['plan'] = "moved timed {}#{}: '{}' to TODO".format(
					key, num+1, content)
			else: # Merge timed -> TODO or move timed -> time
				try: # Merge timed -> TODO
					todo_i = int(order[2]) - 1
					if todo_i > 100: #commit suicide
						temp = int('a') 
					self.newestPlanList['TODO'][todo_i] += '; ' + content
					mail['plan'] = "merged timed {}#{}: '{}' into todo {}".format(
						key, num+1, content, todo_i+1)
				except: # Move timed -> somewhere not todo
					if len(order[2]) == 1:
						time_i_ = ord(order[2])-97
						key_ = self.keys[time_i_]
					else:
						key_ = int(order[2])
					if len(order) == 3: # Move timed to another
						if key_ in self.newestPlanList:
							self.newestPlanList[key_].append(content)
						else:
							self.newestPlanList[key_] = [content]
							self.keys.append(key_)
							self.keys.sort()
						mail['plan'] = "moved timed {}#{}: '{}' to timed {}".format(
							key, num+1, content, key_)
					else: #len == 4, merge two timed
						num_ = int(order[3])-1
						if key == key_:
							if num == num_:
								mail['plan'] = "moved timed {}#{} to {}#{} ??".format(
									key, num+1, key_, num_+1)
								if key in self.newestPlanList:
									self.newestPlanList[key].insert(num, content)
								else:
									self.newestPlanList[key] = [content]
									self.keys.append(key)
									self.keys.sort()
							else:
								inc =  int(num_ > num)
								num_ -= inc
								self.newestPlanList[key][num_] += '; ' + content
								mail['plan'] = 'merged timed {}#{} to {}#{}.'.format(
									key, num+1, key_, num_+inc+1)
						else:
							self.newestPlanList[key_][num_] += '; '+ content
							mail['plan'] = 'merged time {}#{} to {}#{}.'.format(
								key, num+1, key_, num_+1)
		return mail

	def finish(self, todo_i):
		self.newestPlanList['TODO'][todo_i] += ' [DONE]'