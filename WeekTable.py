import csv

class WeekTable(object):
	def __init__(self):
		self.table = []
		with open('wtab.csv','r') as f:
			data = csv.reader(f)
			for row in data:
				self.table.append(row[1:])

	def int(self, col):
		if col == 'mon': return 0
		if col == 'tue': return 1
		if col == 'wed': return 2
		if col == 'thu': return 3
		if col == 'fri': return 4
		if col == 'sat': return 5
		if col == 'sun': return 6

	def rowRegularise(self, row):
		row = int(row)
		if row >= 100:
			row = (row/100-7)*2+int(row%100>=30)
		return row

	def colRegularise(self, col):
		if type(col) is str:
			if len(col) == 1: 
				col = int(col)
			else: 
				col = self.int(col.lower())
		return col

	def rowToStamp(self, row):
		return (row/2+7)*100+(row%2*30)

	def floor(self, row, col):
		lrow = row
		while self.table[lrow][col] == '':
			lrow -= 1
		return lrow

	def ceiling(self, row, col):
		hrow = row + 1
		while self.table[hrow][col] == '':
			hrow += 1
		return hrow

	def tableQuery(self, order):
		mail = dict()
		col = self.colRegularise(order[0])
		if len(order) == 0:
			mail['transfer'] = 'your current week table'
			mail['wtab'] = 'not yet implemented'
			return mail
		if len(order) == 1:
			srow = 0
			erow = len(self.table)-2
		if len(order) == 2:
			srow = self.rowRegularise(order[1])
			erow = srow
		if len(order) == 3:
			srow = self.rowRegularise(order[1])
			erow = self.rowRegularise(order[2])
		lrow = self.floor(srow, col)
		hrow = self.ceiling(erow, col)
		mail['wtab'] = [order[0]]
		for irow in range(lrow, hrow+1):
			if self.table[irow][col] != '':
				mail['wtab'].append('[{}]: {}'.format(
					self.rowToStamp(irow), self.table[irow][col]))
		mail['wtab'] = '\n\t'.join(mail['wtab'])
		return mail

	def set(self, order):
		mail = dict()
		col = self.colRegularise(order[0])
		if len(order) == 2:
			srow = 0
			erow = len(self.table)-2
			content = order[1]
		if len(order) == 3:
			srow = self.rowRegularise(order[1])
			erow = srow
			content = order[2]
		if len(order) == 4:
			srow = self.rowRegularise(order[1])
			erow = self.rowRegularise(order[2])
			content = order[3]
		self.table[srow][col] = content
		if erow < len(self.table) - 1:
			if self.table[erow+1][col] != '':
				pass
			else:
				lrow = self.floor(erow, col)
				if self.table[lrow][col] == content:
					self.table[erow+1][col] = 'break'
				else:
					self.table[erow+1][col] = self.table[lrow][col]
		for irow in range(srow+1, erow+1):
			self.table[irow][col] = ''
		self.logdown()
		mail['wtab'] = "{} to {} is set to {}".format(
			self.rowToStamp(srow), self.rowToStamp(erow), content)
		return mail

	def logdown(self):
		with open('wtab.csv', 'w') as f:
			writer = csv.writer(f)
			for i in range(0, len(self.table)):
				row_i = self.table[i]
				stramp = int(i<6)*'0'+str(self.rowToStamp(i))
				writer.writerow([stramp] + row_i)

	def getPlan(self, wday):
		planList = dict()
		for row_i in range(0, len(self.table)):
			if self.table[row_i][wday] != '':
				key = self.rowToStamp(row_i)
				planList[key] = self.table[row_i][wday].split(';')
		return planList