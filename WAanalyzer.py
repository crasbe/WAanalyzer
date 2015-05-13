#! /usr/bin/python3

# Analysis of whatsapp chat protocols
# written by crasbe, 2015
# copyright crasbe, 2015

import os
import time
import locale
import argparse
import calendar
import operator

import classes.stringanalysis
import classes.stringproc

#-----------------------------------------------------------------------
# gnuplot command
gnuplot =   'set xlabel "{0}"\nset ylabel "{1}"\nset grid\n' + \
            'set datafile separator ","\nset xtics rotate by -45\n' + \
            'set yrange [0:*]\n#set terminal png size 1280,780\n' + \
            'set term png\nset boxwidth 0.75\nset output "pics/{2}.png"\n' + \
            'set style fill solid\nplot "gnuplot/{3}.dat"' + \
            'using 2:xtic(1) with boxes notitle'
            
    # {0}: X-Axis Label
    # {1}: Y-Axis Label
    # {2}: picture filename
    # {3}: gnuplot data file name

#-----------------------------------------------------------------------
parser = argparse.ArgumentParser(description="A script for generating "+\
                                "diagrams from a WhatsApp chatlog.", \
                                prog="WAanalyzer")
parser.add_argument("filename", metavar="file", nargs=1)
parser.add_argument("--alias", action="append", \
                    help="An alias for a name/number. Separated by ':'!")

args = parser.parse_args()

print(args.alias)
aliasses = dict()

for alias in args.alias:
    alias = alias.split(":")
    aliasses[alias[0]] = alias[1]

#-----------------------------------------------------------------------

locale.setlocale(locale.LC_ALL, "de_DE.utf8")

os.makedirs("pics",exist_ok=True)
os.makedirs("gnuplot",exist_ok=True)

os.system("rm -f pics/*.png")
os.system("rm -f gnuplot/*.dat")
os.system("rm -f gnuplot/*.scr")

readobj = open(args.filename[0])


stringpro = classes.stringproc.StringProc(aliasses)
stringpro.newInput(readobj.read())

stringana = classes.stringanalysis.StringAnalysis()
stringana(stringpro.lines)

#-----------------------------------------------------------------------

for command in stringana.comlist:
    xaxisname, yaxisname, filename, xaxisdata, yaxisdata = getattr(stringana, command)()

    datfile = open("gnuplot/"+filename+".dat", "w")
    gpfile = open("gnuplot/"+filename+".scr", "w")
    
    gpfile.write(gnuplot.format(xaxisname,yaxisname,filename,filename))
    gpfile.close()
    
    for i in range(0, len(xaxisdata)):
        datfile.write("{0},{1}\n".format(xaxisdata[i], yaxisdata[i]))
    
    datfile.close()
        
    os.system("gnuplot gnuplot/"+filename+".scr")

os.system("montage pics/*.png -geometry 640 -tile 4x5 pics/output.png")
