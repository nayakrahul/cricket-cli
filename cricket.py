import urllib.parse
import urllib.request
import json
import sys
import getopt
from texttable import Texttable


args = {'apikey': 'vkYYojXc77f2PxnpDaAcmucLSX12'}
USAGE = "Usage: cricket [-a] [-m] [-s <match_no>] [-c] [-d <match_no>] [-p <match_no>] [-x <player_name>]\n \
        -a --> All matches\n \
        -m --> Current matches\n \
        -s --> Scoreboard of a match\n \
        -c --> Cricket calender\n \
        -d --> Match details\n \
        -p --> PlayingXI of a match\n \
        -x --> Player Statistics"
BASE_URL = "http://cricapi.com/api/"


def getResponse(args, url):
    url = url.format(urllib.parse.urlencode(args))
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    # print(data)
    return data


def makeTable(statements):
    table = Texttable()
    table.add_rows(statements)
    print(table.draw())


def getPlayerName(pid):
    url = BASE_URL + "playerStats?{}"
    args.update({'pid': pid})
    data = getResponse(args, url)
    if data.get('fullName'):
        return data['fullName']
    else:
        return "Unknown"


def allMatches():
    url = BASE_URL + "matches?{}"
    data = getResponse(args, url)
    counter = 1
    matches = []
    uniqueIds = []
    for datum in data['matches']:
        teams = datum['team-1'] + ' vs ' + datum['team-2']
        date = datum['date'].split('T')[0]
        if 'winner_team' in datum:
            status = "Finished"
        elif datum['matchStarted']:
            status = 'Live'
        else:
            status = 'Not Started'
        match = [counter, teams, date, status]
        counter += 1
        matches.append(match)
        uniqueIds.append(datum)
    statements = [['No.', 'Matches', 'Date', 'Status']] + matches
    return statements, uniqueIds


def currentMatches():
    url = BASE_URL + "cricket?{}"
    data = getResponse(args, url)
    matches = []
    for datum in data['data']:
        matches.append([datum['description']])
    statements = [['Current Matches']] + matches
    makeTable(statements)


def getScore(input):
    uniqueIds = allMatches()[1]
    try:
        uniqueId = uniqueIds[input - 1]['unique_id']
        url = BASE_URL + "cricketScore?{}"
        args.update({'unique_id': uniqueId})
        data = getResponse(args, url)
        statements = []
        statements.append([data['team-1'] + ' vs ' + data['team-2']])
        statements.append([uniqueIds[input - 1]['type']])
        statements.append([data['score']])
        if 'innings-requirement' in data:
            statements.append([data['innings-requirement']])
        elif 'winner_team' in uniqueIds[input - 1]:
            statements.append([uniqueIds[input - 1]['winner_team'] + " won"])
        else:
            statements.append(["Ongoing"])
        makeTable(statements)
    except (KeyError, ValueError, IndexError):
        print("Invalid Input")


def matchCalendar():
    url = BASE_URL + "matchCalendar?{}"
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
        uniqueId = uniqueIds[input - 1]['unique_id']
        url = BASE_URL + "fantasySummary?{}"
        args.update({'unique_id': uniqueId})
        data = getResponse(args, url)
        statements = [[data['data']['team'][0]['name'] +
                       " vs " + data['data']['team'][1]['name']]]
        statements.append([data['type']])
        if 'toss_winner_team' in data['data']:
            statements.append(
                [data['data']['toss_winner_team'] + " won the toss"])
        if 'winner_team' in data['data']:
            statements.append(["Winner - " + data['data']['winner_team']])
        if 'name' in data['data']['man-of-the-match']:
            statements.append(["Man of the Match - " +
                               data['data']['man-of-the-match']['name']])
        makeTable(statements)
        for i in range(len(data['data']['batting'])):
            batting = data['data']['batting'][i]
            makeTable([[batting['title']]])
            statements = [["Batsman", "Details",
                           "Runs(Balls)", "Fours and Sixes", "Strike Rate"]]
            for datum in batting['scores'][:-1]:
                statements.append([datum['batsman'],
                                   datum['dismissal-info'],
                                   "{}({})".format(datum['R'],
                                                   datum['B']),
                                   "{} fours and {} sixes".format(datum['4s'],
                                                                  datum['6s']),
                                   datum['SR']])
            statements.append(
                [batting['scores'][-1]['batsman'], "", batting['scores'][-1]['detail'], "", ""])
            makeTable(statements)
            bowling = data['data']['bowling'][i]
            makeTable([[bowling['title']]])
            statements = [["Bowler", "O - M - R- W",
                           "Economy Rate", "Fours and Sixes", "Dots"]]
            for datum in bowling['scores']:
                statements.append([datum['bowler'],
                                   "{} - {} - {} - {}".format(datum['O'],
                                                              datum['M'],
                                                              datum['R'],
                                                              datum['W']),
                                   datum['Econ'],
                                   "{} fours and {} sixes".format(datum['4s'],
                                                                  datum['6s']),
                                   datum['0s']])
            makeTable(statements)
    except (KeyError, ValueError, IndexError):
        print("Invalid Input")


def getPlayingXI(input):
    uniqueIds = allMatches()[1]
    try:
        uniqueId = uniqueIds[input - 1]['unique_id']
        url = BASE_URL + "fantasySummary?{}"
        args.update({'unique_id': uniqueId})
        data = getResponse(args, url)
        statements = [[data['data']['team'][0]['name'],
                       data['data']['team'][1]['name']]]
        for i in range(11):
            players = [
                data['data']['team'][0]['players'][i]['name'],
                data['data']['team'][1]['players'][i]['name']]
            statements.append(players)
        makeTable(statements)
    except (KeyError, ValueError, IndexError):
        print("Invalid Input")


def getPlayerStatistics(name):
    url = BASE_URL + "playerFinder?{}"
    args.update({'name': name})
    data = getResponse(args, url)
    args.pop('name')
    for datum in data['data']:
        pid = datum['pid']
        url = BASE_URL + "playerStats?{}"
        args.update({'pid': pid})
        p_data = getResponse(args, url)
        s1 = []
        s2 = []
        if 'name' in p_data:
            s1.append("Name")
            s2.append(p_data['name'])
        if 'fullName' in p_data:
            s1.append("Full Name")
            s2.append(p_data['fullName'])
        if 'currentAge' in p_data:
            s1.append("Current Age")
            s2.append(p_data['currentAge'])
        if 'born' in p_data:
            s1.append("Born")
            s2.append(p_data['born'])
        if 'country' in p_data:
            s1.append("Country")
            s2.append(p_data['country'])
        makeTable([s1, s2])
        s1 = []
        s2 = []
        if 'playingRole' in p_data:
            s1.append("Playing Role")
            s2.append(p_data['playingRole'])
        if 'battingStyle' in p_data:
            s1.append("Batting Style")
            s2.append(p_data['battingStyle'])
        if 'bowlingStyle' in p_data:
            s1.append("Bowling Style")
            s2.append(p_data['bowlingStyle'])
        if 'majorTeams' in p_data:
            s1.append("Major Teams")
            s2.append(p_data['majorTeams'])
        makeTable([s1, s2])
        for key, value in p_data['data']['batting'].items():
            makeTable([["Batting - " + key]])
            s1 = []
            s2 = []
            for k, v in value.items():
                s1.append(k)
                s2.append(v)
            makeTable([s1, s2])
        for key, value in p_data['data']['bowling'].items():
            makeTable([["Bowling - " + key]])
            s1 = []
            s2 = []
            for k, v in value.items():
                s1.append(k)
                s2.append(v)
            makeTable([s1, s2])
        if 'profile' in p_data and p_data['profile'] != "":
            statements = [["Profile"], [p_data['profile']]]
            makeTable(statements)
        print("*" * 100)


def main(argv):
    try:
        opts, args = getopt.getopt(
            argv, "hams:cd:p:x:", [
                "score=", "details=", "playingxi=", "playerstats="])
    except getopt.GetoptError:
        print(USAGE)
        sys.exit(2)
    if len(opts) == 0:
        print(USAGE)
    for opt, arg in opts:
        if opt in ("-h"):
            print(USAGE)
            sys.exit()
        elif opt in ("-a"):
            makeTable(allMatches()[0])
        elif opt in ("-m"):
            currentMatches()
        elif opt in ("-s", "--score"):
            input = arg
            getScore(int(input))
        elif opt in ("-c"):
            matchCalendar()
        elif opt in ("-d", "--details"):
            input = arg
            matchDetails(int(input))
        elif opt in ("-p", "--playingxi"):
            input = arg
            getPlayingXI(int(input))
        elif opt in ("-x", "--playerstats"):
            input = arg
            getPlayerStatistics(input)


if __name__ == '__main__':
    main(sys.argv[1:])
