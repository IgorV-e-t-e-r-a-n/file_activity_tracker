# File Activity Tracker

A Python-based tool to monitor and report changes in file or folder access permissions. It uses **AccessEnum** (from Sysinternals) to capture permission changes and logs them to a SQLite database. Unauthorized changes trigger email alerts.

## Features

- **Permission Monitoring**: Tracks changes in file/folder permissions.
- **Baseline Comparison**: Compares current permissions with a baseline snapshot.
- **Email Alerts**: Sends email notifications for unauthorized changes.
- **Logging**: Logs changes to a SQLite database and generates HTML reports.

## Prerequisites

- **Python 3.12+**
- **AccessEnum** (from Sysinternals)
- **aiosmtpd** (for local SMTP server testing)

## Installation

1. **Clone the Repository**:
   git clone https://github.com/IgorV-e-t-e-r-a-n/file_activity_tracker.git
   cd file_activity_tracker

2. **Install Dependencies**:
   Install the required Python packages:
   pip install aiosmtpd

3. **Download AccessEnum**:
   Download AccessEnum from the Sysinternals website.
   Place AccessEnum.exe in a directory (e.g., C:\Windows\Sysinternals).

4. **Configure config.ini**:
   Update the config.ini file with the correct paths and settings:
   [AccessEnum]
   path = C:\Windows\Sysinternals\AccessEnum.exe

   [Files]
   output_dir = C:\PermissionLogs

   [Email]
   host = 127.0.0.1
   port = 1025
   recipient = admin@example.com

## Usage

1. **Start the SMTP Server**:
   Run the local SMTP server to capture email alerts:
   python smtp_server.py
   The server will start on 127.0.0.1:1025 and print incoming emails to the terminal.

2. **Generate Baseline Permissions**:
   Run AccessEnum to create a baseline snapshot of permissions:
   AccessEnum.exe -accepteula C:\SensitiveData > baseline.txt

3. **Run the File Activity Tracker**:
   Execute the script to monitor permission changes:
   python file_activity_tracker.py --directory C:\SensitiveData
   The script will compare the current permissions with the baseline.
   If changes are detected, it will log them to the database, generate a report, and send an email alert.

4. **View Reports**:
   - Database Logs: Check the SQLite database (permissions.db) for detailed logs.
   - HTML Report: Open permission_changes_report.html in your browser.

## Configuration

- [AccessEnum]: Path to AccessEnum.exe.
- [Files]: Directory for output files (baseline.txt, current.txt, permissions.db, etc.).
- [Email]: SMTP server settings for email alerts.
