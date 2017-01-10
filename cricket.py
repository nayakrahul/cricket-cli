import urllib, json
from texttable import Texttable
import sys, getopt

args = {'apikey':'vkYYojXc77f2PxnpDaAcmucLSX12'}

def getResponse(args, url):
	url = url.format(urllib.urlencode(args))
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	return data

def makeTable(statements):
	table = Texttable()
	table.add_rows(statements)
	print table.draw()

def getPlayerName(pid):
	url = "http://cricapi.com/api/playerStats?{}"
	args.update({'pid':pid})
	data = getResponse(args, url)
	return data['fullName']

def allMatches():
	url = "http://cricapi.com/api/matches?{}"
	data = getResponse(args, url)
	counter = 1
	matches = []
	uniqueIds = []
	for datum in data['matches']:
		teams = datum['team-1'] + ' vs ' + datum['team-2']
		date = datum['date'].split('T')[0]
		if datum['matchStarted']:
			status = 'Live'
		else:
			status = 'Not Started'
		match = [counter, teams, date, status]
		counter += 1
		matches.append(match)
		uniqueIds.append(datum['unique_id'])
	statements = [['No.', 'Matches', 'Date', 'Status']] + matches
	return statements, uniqueIds
	
def currentMatches():
	url = "http://cricapi.com/api/cricket?{}"
	data = getResponse(args, url)
	matches = []
	for datum in data['data']:
		matches.append([datum['description']])
	statements = [['Current Matches']] + matches
	makeTable(statements)

def getScore(input):
	uniqueIds = allMatches()[1]
	try:
		uniqueId = uniqueIds[input-1]
		url = "http://cricapi.com/api/cricketScore?{}"
		args.update({'unique_id':uniqueId})
		data = getResponse(args, url)
		statements = []
		statements.append([data['team-1'] + ' vs ' + data['team-2']])
		statements.append([data['type']])
		statements.append([data['score']])
		statements.append([data['innings-requirement']])
		makeTable(statements)
	except (KeyError, ValueError, IndexError):
		print "Invalid Input"

def matchCalendar():
	url = "http://cricapi.com/api/matchCalendar?{}"
	data = getResponse(args, url)
	matches = []
	for datum in data['data']:
		match = [datum['name'], datum['date']]
		matches.append(match)
	statements = [['Matches', 'Date']] + matches
	makeTable(statements)

def matchDetails(input):
	uniqueIds = allMatches()[1]
	try:
		uniqueId = uniqueIds[input-1]
		url = "http://cricapi.com/api/ballByBall?{}"
		args.update({'unique_id':uniqueId})
		data = getResponse(args, url)
		for datum in data['data']:
			statements = []
			summary = ""
			if datum.get('over_complete'):
				teamName = data['team'][0]['team_name'] \
							if data['team'][0]['team_id'] == datum['team_id'] else data['team'][1]['team_name']
				summary += "End of over %s (%s) %s %s/%s\n" % \
							(datum['over_number'], datum['event_string'], teamName, datum['runs'], datum['wickets'])
				if datum['required_string'] != "":
					summary += "(%s)\n" % (datum['required_string'])
				for batsman in datum['batsman']:
					batsmanName = getPlayerName(batsman['pid'])
					words = batsmanName.split()
					lastName = words.pop()
					acronym = "".join(w[0] for w in words)
					summary += "%s %s 	%s (%sb %s*4 %s*6)\n" % \
								(acronym, lastName, batsman['runs'], batsman['balls_faced'], batsman['fours'], batsman['sixes'])
				for bowler in datum['bowler']:
					batsmanName = getPlayerName(bowler['pid'])
					words = batsmanName.split()
					lastName = words.pop()
					acronym = "".join(w[0] for w in words)
					summary += "%s %s 	%s-%s-%s-%s" % \
								(acronym, lastName, bowler['overs'].split('.')[0], bowler['maidens'], bowler['conceded'], bowler['wickets'])
					break
			statements.append([summary])
			balls = []
			for ball in datum['ball']:
				ball_description = "%s 	%s, %s, %s" % (ball['overs_actual'], ball['players'], ball['event'], ball['text'])
				balls.append([ball_description])
			statements += balls
			makeTable(statements)
	except (KeyError, ValueError, IndexError):
		print "Invalid Input"

def getPlayingXI(input):
	uniqueIds = allMatches()[1]
	try:
		uniqueId = uniqueIds[input-1]
		url = "http://cricapi.com/api/ballByBall?{}"
		args.update({'unique_id':uniqueId})
		data = getResponse(args, url)
		statements = [[data['team'][0]['team_name'], data['team'][1]['team_name']]]
		for i in range(11):
			players = [data['team'][0]['player'][i]['known_as'], data['team'][1]['player'][i]['known_as']]
			statements.append(players)
		makeTable(statements)
	except (KeyError, ValueError, IndexError):
		print "Invalid Input"

def main(argv):
   	try:
   		opts, args = getopt.getopt(argv,"hams:cd:p:",["match=","score="])
   	except getopt.GetoptError:
   		print 'Usage: cricket [-a] [-m] [-s <match_no>] [-c] [-d <match_no>] [-p <match_no>]'
   		sys.exit(2)
   	for opt, arg in opts:
   		if opt == '-h':
   			print 'Usage: cricket [-a] [-m] [-s <match_no>] [-c] [-d <match_no>] [-p <match_no>]'
   			sys.exit()
   		elif opt == '-a':
   			makeTable(allMatches()[0])
   		elif opt in ("-m", "--match"):
   			currentMatches()    
   		elif opt in ("-s", "--score"):
   			input = arg
   			getScore(int(input))
   		elif opt in ("-c", "--calender"):
   			matchCalendar()
   		elif opt in ("-d", "--details"):
   			input = arg
   			matchDetails(int(input))
   		elif opt in ("-p", "--playingxi"):
   			input = arg
   			getPlayingXI(int(input))
   
if __name__ == '__main__':
		main(sys.argv[1:])
