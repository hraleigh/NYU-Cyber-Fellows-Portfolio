\# Splunk Home Lab – Windows Security Monitoring



\## Overview

This project is a personal Security Information and Event Management (SIEM) lab built using Splunk. The goal was to gain hands-on experience ingesting Windows logs, creating dashboards, building alerts, and performing basic security monitoring and detection.



\## Project Goals

\- Set up a functional Splunk environment at home

\- Ingest and analyze Windows security logs

\- Build useful dashboards for a SOC analyst workflow

\- Create detection rules and alerts for common threats

\- Document the process for learning and portfolio purposes



\## Skills Demonstrated

\- Splunk administration and data ingestion

\- SPL (Search Processing Language) query writing

\- Dashboard and visualization creation

\- Alert configuration and tuning

\- Log analysis and security monitoring

\- Basic detection engineering



\## Lab Architecture

\- \*\*Splunk Instance\*\*: Splunk Enterprise (Free license)

\- \*\*Data Source\*\*: Windows 10/11 workstation + Sysmon

\- \*\*Log Types\*\*: Windows Security Event Logs, Sysmon logs

\- \*\*Key Detections\*\*:

&#x20; - Failed logon brute force attempts

&#x20; - Privilege escalation events

&#x20; - Unusual authentication activity

&#x20; - Account lockouts



\## Key Features Built

\- Custom dashboards for authentication and security monitoring

\- Real-time and scheduled alerts for suspicious activity

\- Correlation searches combining multiple data sources

\- Basic alert tuning to reduce false positives



\## Screenshots

\*(Add screenshots here of your dashboards, alerts, and search results)\*



\## How to Replicate This Lab



\### Prerequisites

\- Windows machine or VM (for log source)

\- At least 8GB RAM recommended for Splunk

\- Splunk Enterprise (Free license)



\### Setup Steps

1\. Install Splunk Enterprise

2\. Install and configure Sysmon on the Windows machine

3\. Configure log forwarding to Splunk (Universal Forwarder or local monitoring)

4\. Create indexes and data inputs

5\. Build dashboards and alerts



See the detailed setup guide in the `setup-guide.md` file.



\## Lessons Learned

\- Importance of proper log parsing and field extraction

\- How to balance alert sensitivity vs. false positives

\- Value of Sysmon for deeper visibility beyond native Windows logs

\- How to structure effective SPL queries for detection



\## Future Improvements

\- Add more data sources (PowerShell logs, firewall logs, etc.)

\- Implement more advanced correlation searches

\- Add MITRE ATT\&CK mapping to detections

\- Explore Splunk ES or build custom SOAR-style playbooks



\## References

\- Splunk Documentation: https://docs.splunk.com

\- Sysmon Documentation: https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon

\- MITRE ATT\&CK Framework



\---



\*\*Author\*\*: Heather Raleigh  

\*\*Date\*\*: July 2026

