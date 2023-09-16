#!/usr/bin/python

import argparse
import csv
import datetime
import operator
import sys
import re

# Constants
MONTH_DICT = {'01': "Jan", '02': "Feb", '03': "Mar", '04': "Apr", '05': "May", '06': "Jun", '07': "Jul", '08': "Aug", '09': "Sep", '10': "Oct", '11': "Nov", '12': "Dec"}

parser = argparse.ArgumentParser()
parser.add_argument("filename", nargs='?', help="the name of the CSV log file")
args = parser.parse_args()

if args.filename is None:
    print("Error! - No Log File Specified!")
    sys.exit()

try:
    with open(args.filename) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        ip_dict = {}
        ip_list = []
        port_list = []
        infected_ip_list = []
        c2_list = []
        connection = 0
        print("Source File:", args.filename)

        for row in reader:
            if row[4] in ['1337', '1338', '1339', '1340']:
                if row[1] not in ip_list:
                    ip_list.append(row[1])
                if row[2] not in c2_list and row[1] in ip_list:
                    c2_list.append(row[2])
                if connection == 0:
                    connection = row[0]

        for i in ip_list:
            port_list.append(i.split("."))
        port_list.sort(key=lambda port_list: int(port_list[3]))

        for i in port_list:
            s = "."
            s = s.join(i)
            infected_ip_list.append(s)
        print("Systems Infected:", len(infected_ip_list))
        print("Infected System IPs:\n", infected_ip_list, sep='')
        print("C2 Servers:", len(c2_list))

        port_list.clear()
        infected_ip_list.clear()
        for i in c2_list:
            port_list.append(i.split("."))
        port_list.sort(key=operator.itemgetter(1, 2, 3))

        for i in port_list:
            s = "."
            s = s.join(i)
            infected_ip_list.append(s)

        print("C2 Server IPs:\n", infected_ip_list, sep='')
        date = datetime.datetime.utcfromtimestamp(float(connection)).strftime('%Y-%m-%d %H:%M:%S')

        list2 = re.split("[- ]", date)

        if list2[1] in MONTH_DICT:
            month = MONTH_DICT[list2[1]]
        print("First C2 Connection: ", list2[0], "-", month, "-", list2[2], " ", list2[3], " UTC", sep='')

        csv_file.seek(0)
        for row in reader:
            if row[2] in infected_ip_list and (row[2] not in ip_dict.keys()):
                ip_dict[row[2]] = int(row[5])
            elif row[2] in infected_ip_list and (row[2] in ip_dict.keys()):
                ip_dict[row[2]] += int(row[5])
        data = sorted(ip_dict.items(), key=operator.itemgetter(1), reverse=True)

        print("C2 Data Totals:", data)

except FileNotFoundError:
    print("Error! - File Not Found!")
    
#Sources Consulted:
#https://pypi.org/project/browserhistory/
#https://docs.python.org/3/library/operator.html
#https://www.geeksforgeeks.org/python-program-to-get-month-name-from-month-number/
