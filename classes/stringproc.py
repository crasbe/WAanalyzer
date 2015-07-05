#! /usr/bin/python3

import re
import locale
import string
from datetime import date, time, datetime

class StringProc:
    def __init__(self, aliasses):
        ''' __init__
        
        '''
        self.inputString = str()
        self.processedInfo = list()
        self.waMessageCache = {"line" : str(), "validaty" : bool() }

        self.inputfile = str()
        
        self.aliasses = aliasses
        
    def __getattr__(self, lines):
        return self.processedInfo

    def sanitize(self, line):
        ''' sanatize:
        A little hack to get rid of special unicode controls.
        '''
        return str(line.encode("cp1252", errors="ignore"), "cp1252")

    def newInput(self, rawInput):
        self.inputfile = rawInput
        self.processInfo()

    def waMessage(self, line, part):
        ''' datestring:
        '''
         # valid date format of WhatsApp chat logs:
        # 2014 and earlier:
        # -> 14.11.2014, 18:18 - Max Mustermann hat Eigene Rufnummer hinzugefügt
        # -> 27.12.2014, 1:07 - Musterine: Wintersonnenwende
        # 2015 and later(?):
        # -> 1. Jan., 11:53 - Matze Mustermann: Und wie is das neue jahr bei euch so?
        # -> 3. Jan., 2:24 - Maximiliane: Reit noch darauf rum..
        # -> 23. Mär., 20:54 - Mark: :(
        # -> 3. Mai, 18:10 - Motzi: Zäh
        
        #----------------------------------------------
        # Date-Part
        
        # regular expression for the valid date formats:
       
        if self.waMessageCache["line"] == line:
            return self.waMessageCache[part]
        
        datere = re.compile('^(((\d{2}\.\d{2}\.\d{4})|(\d?\d\.\s[\wöäü]{3}\.?))\,\ \d?\d\:\d{2}\s\-\s)')
        
        dateTimeStr = datere.search(line)
        if dateTimeStr == None:
            self.waMessageCache["validaty"] = False
            return False
        else:
            self.waMessageCache["validaty"] = True

        dateTimeStr = dateTimeStr.group()
        
        pre14 = re.compile('(((\d{2}\.\d{2}\.\d{4}))\,\ \d?\d\:\d{2}\ \-\ )')
        post15 = re.compile('(^(\d?\d\.\s[\wäöü]{3}\.)\,\s\d?\d\:\d{2}\s\-\s)')
        post15s = re.compile('(^(\d?\d\.\s[\wäöü]{3})\,\s\d?\d\:\d{2}\s\-\s)') # for Mai...
        
        locale.setlocale(locale.LC_ALL, "de_DE.utf8")
        msgDateTime = str()
        
        if pre14.match(dateTimeStr) != None:
            # this message comes from 2014 or earlier
            msgDateTime = datetime.strptime(dateTimeStr, "%d.%m.%Y, %H:%M - ")

        elif post15.match(dateTimeStr) != None:
            # this message comes from 2015 or later....
            msgDateTime = datetime.strptime(dateTimeStr, "%d. %b., %H:%M - ")
            msgDateTime = msgDateTime.replace(year=2015)
        elif post15s.match(dateTimeStr) != None:
            msgDateTime = datetime.strptime(dateTimeStr, "%d. %b, %H:%M - ")
            msgDateTime = msgDateTime.replace(year=2015)
        else:
            raise "Weird err2or: "+msgDateTimeStr
        
        #---------------------------------------
        # Sender-Part
        
        msgWithSender = line[len(dateTimeStr)::]
        
        senderre = re.compile("^(([\wäöüÄÜÖ()]+[\s\-]?[\wäöüÄÜÖ()]*[\s\-]?[\wäöüÄÜÖ()]*[\s\-]?[\wäöüÄÜÖ()]*((\shat\s)|\:\s|\swurde\s))|(\+\d{2}\s\d{3,4}\s\d+((\shat\s)|\:\s))|(Du hast ))")
        
        sender = senderre.match(msgWithSender)
        if sender == None:
            exit("Weird error: "+msgWithSender)
        
        sender = sender.group()
        
        # Sender-Part again
        if ": " in sender:
            sender = sender.rstrip(": ")
        elif " hat " in sender:
            sender = sender.rstrip(" hat ")
        elif " hast " in sender:
            sender = sender.rstrip(" hast ")
        
        if sender in self.aliasses.keys():
            sender = self.aliasses[sender]
        
        self.waMessageCache["line"] = line
        self.waMessageCache["wadatetime"] = dateTimeStr
        self.waMessageCache["datetime"] = msgDateTime
        self.waMessageCache["sender"] = sender
        self.waMessageCache["message"] = line[len(dateTimeStr+sender)::]
        if len(self.waMessageCache["message"]) > 25000:
            self.waMessageCache["message"] = "bla"
        
        if part in self.waMessageCache:
            return self.waMessageCache[part]
        else:
            exit("Unknown part specified: "+part)        

    def processInfo(self):
        prev = str()
        
        for line in self.inputfile.splitlines():
            line = self.sanitize(line).strip("\n")
            if self.waMessage(line, "validaty") == False:
                line = prev + ": " + line
            else:
                prev =  self.waMessage(line, "wadatetime") + \
                        self.waMessage(line, "sender")
                line = line
            
            self.processedInfo.append({ "datetime"  : self.waMessage(line, "datetime"), \
                                        "sender"    : self.waMessage(line, "sender"), \
                                        "message"   : self.waMessage(line, "message") })
