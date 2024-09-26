#!/usr/bin/python

import argparse
import csv
import sys

# Constants
MONTH_DICT = {
    '01': "Jan",
    '02': "Feb",
    '03': "Mar",
    '04': "Apr",
    '05': "May",
    '06': "Jun",
    '07': "Jul",
    '08': "Aug",
    '09': "Sep",
    '10': "Oct",
    '11': "Nov",
    '12': "Dec"
}


class MalwareLogAnalyzer:

    def __init__(self, filename):
        self.filename = filename
        self.ip_dict = {}
        self.infected_ips = []
        self.c2_servers = []
        self.first_connection_timestamp = None

    def load_data(self):
        try:
            with open(self.filename) as csv_file:
                reader = csv.reader(csv_file, delimiter=',')
                for row in reader:
                    if self.is_row_valid(row):
                        if row[4] in ['1337', '1338', '1339', '1340']:
                            self.process_infected_system(row)
                            self.process_c2_server(row)
                            self.update_first_connection_timestamp(row[0])
        except FileNotFoundError:
            print("Error! - File Not Found!")
            sys.exit(1)

    def is_row_valid(self, row):
        if len(row) < 6:
            return False
        try:
            int(row[4])
            int(row[5])
            int(row[0])
            return True
        except ValueError:
            return False

    def process_infected_system(self, row):
        src_ip = row[1]
        if src_ip not in self.infected_ips:
            self.infected_ips.append(src_ip)

    def process_c2_server(self, row):
        dest_ip = row[2]
        data_bytes = int(row[5])
        if dest_ip not in self.c2_servers:
            self.c2_servers.append(dest_ip)
        self.ip_dict[dest_ip] = self.ip_dict.get(dest_ip, 0) + data_bytes

    def update_first_connection_timestamp(self, timestamp):
        if self.first_connection_timestamp is None or int(timestamp) < int(
                self.first_connection_timestamp):
            self.first_connection_timestamp = timestamp

    def display_summary(self):
        print("Source File:", self.filename)
        self.display_infected_systems()
        self.display_c2_servers()
        print("First C2 Connection:",
              self.format_timestamp(self.first_connection_timestamp))
        self.display_data_totals()

    def display_infected_systems(self):
        print("Systems Infected:", len(self.infected_ips))
        self.infected_ips.sort(key=lambda ip: tuple(map(int, ip.split('.'))))
        print("Infected System IPs:\n", self.infected_ips)

    def display_c2_servers(self):
        print("C2 Servers:", len(self.c2_servers))
        self.c2_servers.sort(key=lambda ip: tuple(map(int, ip.split('.'))))
        print("C2 Server IPs:\n", self.c2_servers)

    def display_data_totals(self):
        data_totals = sorted(self.ip_dict.items(),
                             key=lambda item: item[1],
                             reverse=True)
        print("C2 Data Totals:", data_totals)

    def format_timestamp(self, timestamp):
        from datetime import datetime
        timestamp_str = datetime.utcfromtimestamp(
            int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        year, month, day, time = timestamp_str.split(" ")[0].split("-") + [
            timestamp_str.split(" ")[1]
        ]
        month_str = MONTH_DICT[month]
        return f"{year}-{month_str}-{day} {time} UTC"


def main():
    parser = argparse.ArgumentParser(description="Analyzes network logs.")
    parser.add_argument("filename", nargs='?', help="Log filename.")
    args = parser.parse_args()
    if not args.filename:
        print("Error! - No Log File Specified!")
        sys.exit(1)

    analyzer = MalwareLogAnalyzer(args.filename)
    analyzer.load_data()
    analyzer.display_summary()


if __name__ == "__main__":
    main()
