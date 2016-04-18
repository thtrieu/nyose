import datetime
from datetime import datetime as timer


class Time(object):
	def __init__(self):
		self.tdSig = '0000-00-00'
		self.timeStamp = 0
		self.wday = 0
		self.nextwday = 0
		self.tmrSig = '0000-00-00'
		self.format = u'%Y-%m-%d'
		self.update()

	def update(self):
		timenow = timer.now()
		self.tdSig, stamp = str(timenow).split()
		self.timeStamp = int(''.join(stamp[0:5].split(':')))
		self.wday = timenow.weekday()
		self.nextwday = (self.wday+1)%7
		nextDay = timenow + datetime.timedelta(days=1)
		self.tmrSig = str(nextDay).split()[0]

	def substract(self, str_to, str_from):
		if str_to == str_from: return 0
		dt_to = timer.strptime(str_to,self.format)
		dt_from = timer.strptime(str_from, self.format)
		return int(str(dt_to-dt_from).split()[0])

	def daySeri(self, from_str, to_str):
		if from_str == to_str: return [from_str]
		dt_from = timer.strptime(from_str, self.format)
		dt_to = timer.strptime(to_str, self.format)
		seri = list()
		while (dt_from <= dt_to):
			seri.append(str(dt_from).split()[0])
			dt_from += datetime.timedelta(1)
		return seri

	def minus(self, time1, time2):
		h1 = int(time1) / 100
		m1 = int(time1) % 100
		h2 = int(time2) / 100
		m2 = int(time2) % 100
		return 60*(h1-h2) + (m1-m2)