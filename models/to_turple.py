import csv

with open('KaihuaLiu_JCR_JournalResults_10_2021.csv','r') as f:
	lines = csv.reader(f)
	next(lines)
	next(lines)
	next(lines)
	journalList = []
	for line in lines:
		if len(line) == 0:
			continue
		journalList.append((line[0],('2021','05','01'),('2021','10','01')))
print(journalList)

