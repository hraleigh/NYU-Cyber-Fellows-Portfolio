\# Splunk Home Lab – Setup Guide



\## 1. System Requirements

\- Windows 10 or 11 (physical machine or VM)

\- Minimum 8GB RAM (12GB+ recommended)

\- At least 50GB free disk space

\- Administrator access on the Windows machine



\## 2. Install Splunk Enterprise (Free)



1\. Go to \[https://www.splunk.com](https://www.splunk.com) → Free Splunk

2\. Download \*\*Splunk Enterprise\*\* (not Splunk Cloud)

3\. Install it on your main machine or a dedicated VM

4\. During installation, set:

&#x20;  - Username: `admin`

&#x20;  - Password: Choose a strong one

5\. Access Splunk at `http://localhost:8000`



\## 3. Install and Configure Sysmon (Recommended)



Sysmon gives much better visibility than native Windows logs.



1\. Download Sysmon from Microsoft Sysinternals

2\. Run the following command in an \*\*Administrator Command Prompt\*\*:



```powershell

sysmon.exe -i -n -l

