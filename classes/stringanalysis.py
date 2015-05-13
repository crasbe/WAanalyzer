#! /usr/bin/python3

# String-Analyse

import locale
import hashlib
import inspect
import calendar
import operator
from datetime import date, time, datetime

class StringAnalysis:
    
    def __init__(self):
        ''' __init__
        
        '''
        
        self.__processedInput = list()
        self.__postNumByDateCache = {"hash" : str()}
        self.__mostWordCache = {"hash" : str()}
        
    def __getattr__(self, comlist):
        """ __getattr__:
        """

        # this ignores private methods because they can be used in
        # plugins for internal processing
        
        commands = list()
        
        
        for command in list(set(dir(self))):
            if command[0:1] != "_":
                commands.append(command)
                
        return commands
        
    def __call__(self, lines):
        self.__processedInput = lines
    

    #-------------------------------------------------------------------
    # Command area:
    # -------------
    #
    # Command format:
    #    The command must be a generator and there is a special order of
    #    the returned values:
    #    1) str:  X-Axis Label
    #    2) str:  Y-Axis Label
    #    3) str:  filename (gnuplot, picture and gnuplot-data)
    #    4) list: the X-Values
    #    5) list: the Y-Values
    #

    def __dictToListXSorted(self, inputList):
        """
        """
        # keys
        keys = sorted(inputList.keys())
        yield keys
        yield [inputList[x] for x in keys]

    def __dictToListSorted(self, inputList, reverseOrder):
        """ __dictToListSorted (private):
        Converts a dictionary in a given order and returns keys and values in a list.
        """
        
        # keys
        yield [x[0] for x in sorted(inputList.items(), key=operator.itemgetter(1), reverse=reverseOrder)]
        # values
        yield [x[1] for x in sorted(inputList.items(), key=operator.itemgetter(1), reverse=reverseOrder)]

    def __mostWord(self):
        """ __mostWord (plugin-support):
        """
        if hashlib.sha224(bytes(repr(self.__processedInput),"utf8")).hexdigest() == self.__mostWordCache["hash"]:
            return self.__mostWordCache["woerterbuch"]
        
        woerterbuch = dict()
        
        for line in self.__processedInput:
            line = line["message"]
            
            for word in line.split(" "):
                if not word in [":", "", "<Medien", "weggelassen>"]:
                    word = word.lower()
                    if word in woerterbuch:
                        woerterbuch[word] += 1
                    else:
                        woerterbuch[word] = 1
                        
        self.__mostWordCache["woerterbuch"] = woerterbuch
        return woerterbuch

    def mostWord(self):
        """ mostWord (plugin):
        """
        woerterbuch = self.__mostWord()
        
        yield "Häufigste Wörter"
        yield "Anzahl"
        yield "wörter"
        xaxisdata, yaxisdata = self.__dictToListSorted(woerterbuch, True)
        yield xaxisdata[0:20]
        yield yaxisdata[0:20]
    
    def mostWordAboveFour(self):
        """ mostWordAboveFour (plugin):
        """
        woerterbuch = self.__mostWord()
        for word in self.__mostWord():
            if len(word) < 4:
                del woerterbuch[word]
                        
        yield "Häufigste Wörter >= 4"
        yield "Anzahl"
        yield "wörterbigger4"
        xaxisdata, yaxisdata = self.__dictToListSorted(woerterbuch, True)
        yield xaxisdata[0:20]
        yield yaxisdata[0:20]
        
    def longWord(self):
        """ longWord (plugin):
        """
        words = list()
        for line in self.__processedInput:
            for word in line["message"].split(" "):
                if not word in words and not "http" in word:
                    words.append(word)
                    
        words.sort(key=len, reverse=True)

        words = words[0:20]
        
        yield "Längste Wörter"
        yield "Länge"
        yield "langeWorte"
        yield words
        yield [len(x) for x in words]
        
    def cry(self):
        """ cry (plugin):
        """
        schreihals = dict()
        wortzahl = dict()
        
        for line in self.__processedInput:
            for word in line["message"].split(" "):
                if not word in [":", "", "<Medien", "weggelassen>",":D",":-D","1-3°C","12:-D","S.113",] and len(word) > 4:
                    if word.isupper():
                        if line["sender"] in schreihals:
                            schreihals[line["sender"]] += 1
                            wortzahl[line["sender"]] += 1
                        else:
                            schreihals[line["sender"]] = 1
                            wortzahl[line["sender"]] = 1
                    if line["sender"] in wortzahl:
                        wortzahl[line["sender"]] += 1
                    else:
                        wortzahl[line["sender"]] = 1
        
        for mensch in schreihals:
            schreihals[mensch] = schreihals[mensch]*100 / wortzahl[mensch]
        
        yield "Schreihälse"
        yield "Anteil geschrien"
        yield "schreihals"
        xaxisdata, yaxisdata = self.__dictToListSorted(schreihals, True)
        yield xaxisdata[0:20]
        yield yaxisdata[0:20]

    def __bigArrayStuff(self, inputlist):
        
        # format: [[ str(), [], int()], ...]
        output = inputlist
        
        for line in self.__processedInput:
            for word in line["message"].split(" "):
                word = word.lower()
                
                for category in inputlist:
                    if word in category[1]:
                        output[output.index(category)][2] += 1
                        
        return output
    
    def lieblingsDrogen(self):
        """
        """
        drogen = [[  "gras", [ "thc", "gras", "weed", "cannabis", \
                            "marihuana", "ganja", "joint", "spliff", \
                            "dope", "pape", "papes"], 0], \
                    ["nikotin", ["nikotin", "zigarette", "zigarre", \
                                "zigaretten", "zigarren", "schachel", \
                                "kippe", "kippen", "raucher", "tabak", \
                                "filter"], 0], \
                    ["alkohol", ["alkohol", "alk", "hacke", \
                                "hackedicht","ethanol", "methanol", \
                                "breit", "methyl", "alohol", "alki", \
                                "besoffen", "alkoholiker", "betrunken", \
                                "getrunken", "bier", "wodka", "vodka", \
                                "jägermeister", "bacardi", "havanna", \
                                "saufen", "angetrunken", "dicht"], 0]]
        
        output = self.__bigArrayStuff(drogen)
        
        output = sorted(output, key=lambda droge: droge[2], reverse=True)
        
        yield "Lieblingsdrogen"
        yield "Erwähnungen"
        yield "lieblingsdrogen"
        yield [x[0] for x in output]
        yield [x[2] for x in output]

    def messageTimeElapsed(self):
        prevline = datetime.fromtimestamp(0)
        
        # 0<=x<1 min, 1<=x<5min 5-10min, 10-30min 30-60min 60-120min >120min
        elapsedMin = [0]*7
        
        for line in self.__processedInput:
            line = line["datetime"]
            delta = (line - prevline).total_seconds() / 60
            if delta >= 0 and delta < 1:
                elapsedMin[0] += 1
            elif delta >= 1 and delta < 5:
                elapsedMin[1] += 1
            elif delta >= 5 and delta < 10:
                elapsedMin[2] += 1
            elif delta >= 10 and delta < 30:
                elapsedMin[3] += 1
            elif delta >= 30 and delta < 60:
                elapsedMin[4] += 1
            elif delta >= 60 and delta < 120:
                elapsedMin[5] += 1
            elif delta >= 120:
                elapsedMin[6] += 1
            
            prevline = line
        
        yield "Durchschnittliche Antwortzeit"
        yield "Anzahl"
        yield "antwortzeit"
        yield [ "0-1 Min.", "1-5 Min.", "5-10 Min.", "10-30 Min", \
                "30-60 Min.", "60-120 Min.", ">120 Min."]
        yield elapsedMin
    
    def laengenrekord(self):
        """
        """
        out = self.__postNumByDate("längenrekord")
        
        yield "Längste Nachricht"
        yield "Länge"
        yield "laengenrekord"
        xaxisdata, yaxisdata = self.__dictToListSorted(out, True)
        yield xaxisdata[0:20]
        yield yaxisdata[0:20]
    
    def stunde(self):
        """
        """
        out = self.__postNumByDate("hour")
        
        yield "Aktivität bei Uhrzeiten"
        yield "Anzahl der Nachrichten"
        yield "uhrzeit"
        xaxisdata, yaxisdata = self.__dictToListXSorted(out)
        yield xaxisdata[0:20]
        yield yaxisdata[0:20]
    
    def jahr(self):
        """
        """
        out = self.__postNumByDate("year")
        
        yield "Übersicht der Jahre"
        yield "Anzahl der Nachrichten"
        yield "jahresuebersicht"
        xaxisdata, yaxisdata = self.__dictToListXSorted(out)
        yield xaxisdata[0:20]
        yield yaxisdata[0:20]
    
    def monat(self):
        """
        """
        out = self.__postNumByDate("month")
        
        yield "Übersicht der Monate"
        yield "Anzahl der Nachrichten"
        yield "monatsuebersicht"
        yield calendar.month_name[1::]
        yield [out[x] for x in calendar.month_name[1::]]
    
    def tag(self):
        out = self.__postNumByDate("day")
        
        yield "Übersicht der Tage"
        yield "Anzahl der Nachrichten"
        yield "tagesuebersicht"
        yield calendar.day_name
        yield [out[x] for x in calendar.day_name]
        
    def topposter(self):
        """
        """
        out = self.__postNumByDate("topposter")
        
        yield "Meiste Nachrichten"
        yield "Anzahl an Nachrichten"
        yield "topposter"
        xaxisdata, yaxisdata = self.__dictToListSorted(out, True)
        yield xaxisdata[0:20]
        yield yaxisdata[0:20]
        
    def medienschleuder(self):
        """
        """
        out = self.__postNumByDate("medienschleuder")
        
        yield "Meiste Mediendateien"
        yield "Anzahl an Mediendateien"
        yield "medienschleuder"
        xaxisdata, yaxisdata = self.__dictToListSorted(out, True)
        yield xaxisdata[0:20]
        yield yaxisdata[0:20]
    
    def durchschnittslaenge(self):
        """
        """
        out = self.__postNumByDate("nachrichtenlänge")
        
        yield "Durchschnittslänge der Nachrichten"
        yield "Länge"
        yield "durchschnittslaenge"
        xaxisdata, yaxisdata = self.__dictToListSorted(out, True)
        yield xaxisdata[0:20]
        yield yaxisdata[0:20]
    
    def __postNumByDate(self, part):
        ''' yearPostNum:
        '''
        if hashlib.sha224(bytes(repr(self.__processedInput),"utf8")).hexdigest() == self.__postNumByDateCache["hash"]:
            return self.__postNumByDateCache[part]
        
        year = {2014:0, 2015:0}
        month = dict(list(zip(calendar.month_name[1::], [0]*12)))
        day = dict(list(zip(calendar.day_name, [0]*7)))
        hour = dict(list(zip(range(0,24), [0]*24)))
        topposter = dict()
        bilderschleuder = dict()
        zeichen = dict()
        laengenrekord = dict()
        frage = dict()
        ausrufung = dict()
        
        locale.setlocale(locale.LC_ALL, "de_DE.utf8")
        
        for msg in self.__processedInput:
            msgdatetime = msg["datetime"]
            
            year[int(msgdatetime.strftime("%Y"))] += 1
            month[msgdatetime.strftime("%B")] += 1
            day[msgdatetime.strftime("%A")] += 1
            hour[int(msgdatetime.strftime("%H"))] += 1
        
            if msg["sender"] in topposter:
                topposter[msg["sender"]] += 1
                zeichen[msg["sender"]] += len(msg["message"])
                if len(msg["message"]) > laengenrekord[msg["sender"]]:
                    laengenrekord[msg["sender"]] = len(msg["message"]) 

            else:
                topposter[msg["sender"]] = 1
                zeichen[msg["sender"]] = len(msg["message"])
                laengenrekord[msg["sender"]] = len(msg["message"])
                
            if msg["message"] != "":
                if msg["message"][-1] == "?":
                    if msg["sender"] in frage:
                        frage[msg["sender"]] += 1
                    else:
                        frage[msg["sender"]] = 1
                elif msg["message"][-1] == "!":
                    if msg["sender"] in ausrufung:
                        ausrufung[msg["sender"]] += 1
                    else:
                        ausrufung[msg["sender"]] = 1
            
            if "<Medien weggelassen>" in msg["message"]:
                if msg["sender"] in bilderschleuder:
                    bilderschleuder[msg["sender"]] += 1
                else:
                    bilderschleuder[msg["sender"]] = 1
        
        for poster in zeichen:
            zeichen[poster] = zeichen[poster] / topposter[poster]
            if poster in frage:
                frage[poster] = frage[poster]*100 / topposter[poster]
            if poster in ausrufung:
                ausrufung[poster] = ausrufung[poster]*100 / topposter[poster]
        
        self.__postNumByDateCache["year"] = year
        self.__postNumByDateCache["month"] = month
        self.__postNumByDateCache["day"] = day
        self.__postNumByDateCache["hour"] = hour
        self.__postNumByDateCache["topposter"] = topposter
        self.__postNumByDateCache["medienschleuder"] = bilderschleuder
        self.__postNumByDateCache["nachrichtenlänge"] = zeichen
        self.__postNumByDateCache["längenrekord"] = laengenrekord
        self.__postNumByDateCache["fragen"] = frage
        self.__postNumByDateCache["ausrufungen"] = ausrufung
        
        if part in self.__postNumByDateCache:
            return self.__postNumByDateCache[part]
        else:
            exit("Wrong part for __postNumByDateCache: "+part)
