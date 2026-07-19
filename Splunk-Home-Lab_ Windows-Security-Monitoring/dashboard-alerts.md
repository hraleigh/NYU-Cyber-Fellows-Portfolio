Panel 1: Failed Logins



index=windows sourcetype=WinEventLog:Security EventCode=4625 

| stats count by src\_ip, Account\_Name 

| sort -count



Panel 2: Successful Logins



index=windows sourcetype=WinEventLog:Security EventCode=4624 

| stats count by Account\_Name, src\_ip





Brute Force Alerts:



index=windows sourcetype=WinEventLog:Security EventCode=4625 

| stats count by src\_ip 

| where count > 10





Example Searches

Failed Logons:

EventCode=4625


Privilege Escalation:

EventCode=4672 OR EventCode=4673


Account Lockout:

EventCode=4740


PowerShell Execution:

EventCode=4103 OR EventCode=4104


Sysmon Process Creation:

sourcetype=XmlWinEventLog:Microsoft-Windows-Sysmon/Operational EventCode=1





