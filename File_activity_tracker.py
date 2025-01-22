import os
import subprocess
import sqlite3
import smtplib
import argparse
import configparser
import logging
from email.mime.text import MIMEText
from datetime import datetime

# Set up logging
logging.basicConfig(filename="permission_tracker.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")

# Constants
ACCESSENUM_PATH = config.get("AccessEnum", "path", fallback="C:\\Windows\\Sysinternals\\AccessEnum.exe")
OUTPUT_DIR = config.get("Files", "output_dir", fallback=os.getcwd())
BASELINE_FILE = os.path.join(OUTPUT_DIR, "baseline.txt")
CURRENT_FILE = os.path.join(OUTPUT_DIR, "current.txt")
DB_FILE = os.path.join(OUTPUT_DIR, "permissions.db")

# Email settings (for alerts)
EMAIL_HOST = config.get("Email", "host", fallback="localhost")
EMAIL_PORT = config.getint("Email", "port", fallback=1025)
EMAIL_TO = config.get("Email", "recipient", fallback="admin@example.com")

def run_accessenum(directory, output_file):
    """Run AccessEnum and save output to a file."""
    command = f'{ACCESSENUM_PATH} -accepteula {directory} > {output_file}'
    subprocess.run(command, shell=True)
    logging.info(f"AccessEnum output saved to {output_file}")

def parse_accessenum_output(file_path):
    """Parse AccessEnum output file into a dictionary."""
    permissions = {}
    try:
        with open(file_path, "r") as file:
            for line in file:
                if "\\" in line:  # Check if it's a file/folder path
                    path, perm = line.strip().split(" ", 1)
                    permissions[path] = perm
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    return permissions

def compare_permissions(baseline, current):
    """Compare baseline and current permissions."""
    changes = {}
    for path, perm in current.items():
        if path not in baseline:
            changes[path] = ("New", None, perm)
        elif baseline[path] != perm:
            changes[path] = ("Modified", baseline[path], perm)
    return changes

def log_changes_to_db(changes):
    """Log changes to SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS permission_changes
                          (id INTEGER PRIMARY KEY, path TEXT, change_type TEXT, old_perm TEXT, new_perm TEXT, timestamp TEXT)''')
        for path, (change_type, old_perm, new_perm) in changes.items():
            cursor.execute("INSERT INTO permission_changes (path, change_type, old_perm, new_perm, timestamp) VALUES (?, ?, ?, ?, ?)",
                           (path, change_type, old_perm, new_perm, datetime.now().isoformat()))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        conn.close()

def send_alert(changes):
    """Send an email alert for unauthorized changes."""
    subject = "Unauthorized Permission Changes Detected"
    body = "The following permission changes were detected:\n\n"
    for path, (change_type, old_perm, new_perm) in changes.items():
        body += f"Path: {path}\nType: {change_type}\nOld Permissions: {old_perm}\nNew Permissions: {new_perm}\n\n"
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "file_activity_tracker@localhost"
    msg["To"] = EMAIL_TO

    try:
        logging.info("Attempting to send email...")
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            logging.info(f"Connected to SMTP server at {EMAIL_HOST}:{EMAIL_PORT}")
            server.sendmail("file_activity_tracker@localhost", EMAIL_TO, msg.as_string())
        logging.info("Alert email sent successfully.")
    except smtplib.SMTPException as e:
        logging.error(f"Failed to send email: {e}")

def generate_report(changes):
    """Generate an HTML report of permission changes."""
    report_file = os.path.join(OUTPUT_DIR, "permission_changes_report.html")
    with open(report_file, "w") as file:
        file.write("<html><body><h1>Permission Changes Report</h1>\n")
        file.write("<table border='1'><tr><th>Path</th><th>Change Type</th><th>Old Permissions</th><th>New Permissions</th></tr>\n")
        for path, (change_type, old_perm, new_perm) in changes.items():
            file.write(f"<tr><td>{path}</td><td>{change_type}</td><td>{old_perm}</td><td>{new_perm}</td></tr>\n")
        file.write("</table></body></html>")
    logging.info(f"Report generated: {report_file}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="File Activity Tracker Using AccessEnum")
    parser.add_argument("--directory", help="Directory to monitor", default="C:\\SensitiveData")
    args = parser.parse_args()

    # Step 1: Generate baseline and current permissions
    run_accessenum(args.directory, BASELINE_FILE)
    input("Modify permissions and press Enter to continue...")
    run_accessenum(args.directory, CURRENT_FILE)

    # Step 2: Parse and compare permissions
    baseline = parse_accessenum_output(BASELINE_FILE)
    current = parse_accessenum_output(CURRENT_FILE)
    changes = compare_permissions(baseline, current)

    if changes:
        # Step 3: Log changes to database
        log_changes_to_db(changes)

        # Step 4: Generate a report
        generate_report(changes)

        # Step 5: Send alert (optional)
        send_alert(changes)
        print("Unauthorized changes detected. Report generated and alert sent.")
    else:
        print("No changes detected.")

if __name__ == "__main__":
    main()