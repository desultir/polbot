import sys
import time
import xmpp

from PyGtalkRobot import GtalkRobot

roster = [] #all people online, not just logged in
users = {} #keep track of all users logged in here for reply to all
nicks = []
killList = {}

class polbot(GtalkRobot):
    status = "Pol Bot"
    
    #def command_priority###_name

    def echoToAll(self, message):
        for user in users:
            self.replyMessage(users[user][0], message)

    def echoToEveryoneElse(self, message, userME):
        for user in users:
            if user != userME.getStripped():
                self.replyMessage(users[user][0], message)

    def sendCommands(self, user):
        self.replyMessage(user, "HELP: Valid commands are /me, /who, /whois, /join, /quit, /help, /topic and /nick")
        self.replyMessage(user, "HELP: If your client filters out /, use # (ie #me, #who...)")
        
    def command_001_join(self, user, message, args):
        '''^[/#]join( .*)?$(?i)'''    
        if user.getStripped() not in users:
            nick = user.getStripped()
            if nick.find('@') is not -1:
                nick = nick[0:nick.find('@')]
            self.replyMessage(user, "You have joined #khmer")
            self.sendCommands(user)
            self.echoToAll(nick + " has joined #khmer")
            users[user.getStripped()] = [user, nick] 
            nicks.append(nick)
            
    def command_002_quit(self, user, message, args):
        '''^[/#]quit( .*)?$(?i)'''
        if user.getStripped() in users:
            self.echoToAll(users[user.getStripped()][1] + " has left #khmer")
            nicks.remove(users[user.getStripped()][1])
            del users[user.getStripped()]
            
    def command_007_nick(self, user, message, args):
        '''^[/#]nick ([a-zA-Z0-9]+)$(?i)'''
        if user.getStripped() in users:
            #import pdb; pdb.set_trace()
            newnick = args[0]
            if len(args[0]) > 15:
                newnick = args[0][0:15]
            if newnick.lower() in map(lower, nicks):
                self.replyMessage(user, "NICK: Someone already exists with that nickname. Cleanse the population of them first")
            else:
                oldnick = users[user.getStripped()][1]
                users[user.getStripped()][1] = newnick
                self.echoToAll("NICK: " + oldnick + " changed nickname to " + newnick)
                nicks.remove(oldnick)
                nicks.append(newnick)

    def command_009_nickfail(self, user, message, args):
        '''^[/#]nick.*(?i)'''
        if user.getStripped() in users:
            self.replyMessage(user, "Invalid nick. Only A-Z and numbers are allowed")
            
    def command_010_who(self, user, message, args):
        '''^[/#]who( .*)?$(?i)'''
        everybody = "CURRENT KHMER ROUGE MEMBERS ARE: "
        for person in users:
            everybody = everybody + users[person][1] + ", "
            
        everybody = everybody[0:-1]
        self.replyMessage(user, everybody)


    def command_011_whois(self, user, message, args):
        '''^[/#]whois( [a-zA-Z0-9]+)?$(?i)'''
        if args[0]:
            nickToLookup = args[0].lstrip()
            if nickToLookup in nicks:
                for key in users:
                    if users[key][1] == nickToLookup:
                        self.replyMessage(user, "WHOIS: " + nickToLookup + "'s gmail handle is " + users[key][0].getStripped())
            else:
                self.replyMessage(user, "WHOIS: No user nicknamed " + nickToLookup)
        else:
            self.replyMessage(user, "WHOIS: Command format is /whois NICK")

    def command_015_topic(self, user, message, args):
        '''^[/#]topic (.*)$(?i)'''
        if user.getStripped() in users:
            self.status = args[0]
            self.setState("default", args[0])
            self.echoToAll(users[user.getStripped()][1] + " changed topic to '" + args[0] +"'")

    def command_020_help(self, user, message, args):
        '''[/#]help( .*)?$(?i)'''
        self.sendCommands(user)

    def command_020_me(self, user, message, args):
        '''[/#]me( .*)?$(?i)'''
        if user.getStripped() in users:
            if args[0]:
                self.echoToAll("*"+ users[user.getStripped()][1] + args[0]) 

    def command_021_ohno(self, user, message, args):
        '''[#/]o\\\\( .*)?'''
        if user.getStripped() in users:
            if args[0]:
                restOfLine = args[0]
            else:
                restOfLine = ""
            #self.echoToEveryoneElse("<"+ users[user.getStripped()][1] + "> /o\\" + restOfLine, user)
            if restOfLine:
                restOfLine = restOfLine + "!?!?!?!"
            self.echoToAll("<polbot> /o\\ /o\\" + restOfLine)

    def command_030_poke(self, user, message, args):
        '''[/#]poke (.*)$(?i)'''
        if "desultir" in user.getStripped():
            for connection in roster:
                if args[0] in str(connection):
                    self.replyMessage(connection, "oi")

    def command_030_kick(self, user, message, args):
        '''[/#]kick (.*)$(?i)'''
        if "desultir" in user.getStripped():
            for nick in nicks:
                if args[0] in nick:
                    self.echoToAll(" * "+ nick + " was kicked out of the Khmer Rouge by "+ users[user.getStripped()][1])
                    nicks.remove(nick)
                    for user, rec in users.items():                 
			if args[0] in rec[1]:
                            del(users[user])




    def command_030_roster(self, user, message, args):
        '''[/#]roster'''
        if "desultir" in user.getStripped():
            rosterString = "ROSTER: "
            for connection in roster:
                rosterString = rosterString + " " + str(connection)
            self.replyMessage(user, rosterString)
    def command_080_echofail(self, user, message, args):
        '''^<.*'''
        None

    def command_099_commandfail(self, user, message, args):
        '''^(/.*)'''
        self.replyMessage(user, "UNKNOWN COMMAND: " + args[0])
        self.sendCommands(user)
        
    #someone typed something non-command, echo to all
    def command_100_default(self, user, message, args):
        '''(.*)'''
        if killList:
            delete = []
            for kill in killList:
                if int(time.time()) - killList[kill] > 30:
                    #user timed out
                    if kill in users:
                        self.echoToEveryoneElse(users[kill][1] + " has left #Khmer - timed out", users[kill][0])
                        nicks.remove(users[kill][1])
                        del users[kill]
                    delete.append(kill)
            for item in delete:
                del killList[item]
        if user.getStripped() in users:
            self.echoToEveryoneElse("<"+ users[user.getStripped()][1] + "> " + message, user)
        else:
            self.replyMessage(user, "You are not currently in channel. Type /join or #join to join")

    def presenceHandler(self, conn, presence):
        UID = self.getUIDfromPresence(presence)
        if presence.getType()=='unavailable':
            print presence.getFrom(), ",", presence.getType()
            
            connectioncount = 0
            if presence.getFrom() in roster:
                roster.remove(presence.getFrom())

            for connection in roster:
                connectionString = str(connection)
                if connectionString[0:connectionString.find('/')] == UID:
                    if connection != presence.getFrom():
                        #user still connected from somewhere else
                        connectioncount = connectioncount + 1
            if connectioncount == 0:
                #wait 30 seconds
                #then kill
                #import pdb; pdb.set_trace()
                killList[UID] = int(time.time())
        elif presence.getType()=='subscribe':
                jid = presence.getFrom().getStripped()
                self.authorize(jid)
        else:
            print presence.getFrom(), ",", presence.getType()
            if UID in killList:
                del killList[UID]
            if presence.getFrom() not in roster:
                roster.append(presence.getFrom())

            #if "desultir" in presence.getFrom().getStripped():
                #self.replyMessage(presence.getFrom(), "hai")
            GtalkRobot.presenceHandler(self, conn, presence)

    def getUIDfromPresence(self, presence):
        UID = str(presence.getFrom())
        return UID[0:UID.find('/')]


def lower(input):
    return input.lower()

if __name__ == "__main__":
    bot = polbot()
    conf = open('config.txt', 'r')
    username = conf.readline().strip()
    password = conf.readline().strip()
    import pdb; pdb.set_trace()
    conf.close()
    bot.setState('default', bot.status)
    while True:
        try:
		bot.start(username, password)
        except xmpp.protocol.SeeOtherHost:
		print sys.exc_info()[0]
		pass
	import xmpp
        log = open("log.txt", 'w+')
        log.write("crash")
        log.close()
    
        
