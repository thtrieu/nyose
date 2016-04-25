import os.path

class Journal(object):
	def __init__(self):
		self.logList = list()

	def logdown(self, time):
		if os.path.isfile('journals/'+time.tdSig):
			mode = 'a'
		else:
			mode = 'w'
		with open('journals/' + time.tdSig, mode) as f:
			for line in self.logList:
				f.write(line+'\n')
		self.logList = list()

	def finish(self, order, plan, time):
		mail = dict()
		mail['plan'] = str()
		doneList = list()

		for i in range(0, len(order)):
			todo_i = int(order[i])-1
			content = plan.newestPlanList['TODO'][todo_i]
			self.logList.append("[{}] done todo: '{}'".format(
				time.timeStamp, content))
			plan.finish(todo_i)
			doneList.append(order[i])

		doneList = ", ".join(doneList)
		mail['journal'] =  "logged that at {}, done todo ".format(time.timeStamp) + doneList 
		mail['plan'] = "marked that you have done todo " + doneList
		return mail

	def log(self, order, time):
		mail = dict()
		self.logList.append("[{}] {}".format(
			time.timeStamp, order[0]))
		mail['journal'] = "journal logged at {}: '{}'".format(
			time.timeStamp, order[0])
		return mail

	def review(self, order, time):
		mail = dict()
		if len(order) == 0:
			num = 1
		if len(order):
			num = int(order[0])
		self.logdown(time)
		allJnals = os.listdir('journals')
		allJnals.sort()
		jnals = allJnals[-num:]
		content = ['review of {} recent day:'.format(num)]
		for i in range(0, num):
			jnal = jnals[num-i-1]
			with open('journals/'+jnal, 'r') as f:
				retrieved = f.read()
			content += ['\n>> {}:'.format(jnal)] + retrieved.split('\n')
		mail['jnal'] = '\n\t'.join(content)
		if len(content) >= 15:
			mail['transfer'] = 'journal review'
		return mail