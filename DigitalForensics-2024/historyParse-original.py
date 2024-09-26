import sqlite3
import sys
import os
import datetime
import argparse
import pytz
import re

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("history_file", nargs='?', help="Name of the history file")
args = parser.parse_args()

if not args.history_file:
    print("Error! - No History File Specified!")
    sys.exit()

history_file = args.history_file

if not os.path.exists(history_file):
    print("Error! - File Not Found!")
    sys.exit()

# Database connection and cursor
conn = sqlite3.connect(history_file)
cursor = conn.cursor()

# Retrieve the total number of downloads and total bytes
cursor.execute(
    "SELECT COUNT(*) AS num_downloads, SUM(total_bytes) AS total_bytes FROM downloads"
)
total_downloads, total_bytes = cursor.fetchone()

# Find the download with the longest duration
cursor.execute(
    "SELECT MAX(end_time - start_time) AS max_duration FROM downloads")
longest_duration = cursor.fetchone()[0]

cursor.execute(
    "SELECT target_path, total_bytes FROM downloads WHERE end_time - start_time = ? ORDER BY total_bytes DESC LIMIT 1",
    (longest_duration, ))
result = cursor.fetchone()
if result:
    longest_download_path, longest_download_size = result
    longest_download_filename = os.path.basename(
        longest_download_path.split('\\')[-1])
else:
    longest_download_filename, longest_download_size = None, None

# Count the number of unique search terms
cursor.execute(
    "SELECT COUNT(DISTINCT term) FROM keyword_search_terms JOIN urls ON keyword_search_terms.url_id = urls.id"
)
unique_search_terms = cursor.fetchone()[0]

# Retrieve the most recent search term and time
cursor.execute("""
    SELECT julianday((last_visit_time/1000000) - 11644473600, "unixepoch", "localtime") AS recent_search_time, urls.id, keyword_search_terms.term, keyword_search_terms.url_id 
    FROM urls 
    LEFT JOIN keyword_search_terms ON urls.id = keyword_search_terms.url_id 
    WHERE keyword_search_terms.term IS NOT NULL
    ORDER BY urls.last_visit_time DESC 
    LIMIT 1
""")
result = cursor.fetchone()
if result:
    most_recent_search_time, _, most_recent_search_term, _ = result
    dt = datetime.datetime.fromtimestamp(
        (most_recent_search_time - 2440587.5) * 86400.0)
    local_timezone = pytz.timezone("Etc/GMT+5")
    most_recent_search_time_str = local_timezone.localize(dt).strftime(
        "%Y-%b-%d %H:%M:%S")
else:
    most_recent_search_term, most_recent_search_time_str = None, None

# Display results
print(f"Source File: {os.path.basename(history_file)}")
print(f"Total Downloads: {total_downloads}")
if longest_download_filename and longest_download_size:
    print(f"File Name: {longest_download_filename}")
    print(f"File Size: {longest_download_size}")

print(f"Unique Search Terms: {unique_search_terms}")
if most_recent_search_term and most_recent_search_time_str:
    print(f"Most Recent Search: {most_recent_search_term}")
    print(f"Most Recent Search Date/Time: {most_recent_search_time_str}")

# Constant mapping for month names
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

# Retrieve the most recent search date in Julian time
cursor.execute(
    "SELECT datetime(urls.last_visit_time/1000000 + (strftime('%s', '1601-01-01')), 'unixepoch') FROM urls INNER JOIN keyword_search_terms ON keyword_search_terms.url_id=urls.id ORDER BY urls.last_visit_time DESC LIMIT 1"
)
q5_result = cursor.fetchone()
time_index = re.split("[- ]", q5_result[0])
if time_index[1] in MONTH_DICT:
    month = MONTH_DICT[time_index[1]]
    print(
        f"NEW Most Recent Search Date/Time: {time_index[0]}-{month}-{time_index[2]} {time_index[3]}"
    )
