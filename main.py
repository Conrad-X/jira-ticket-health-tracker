import subprocess
from utils.email import send_email
import sys
from utils.constants import SCRIPTS_RUNNING,SCRIPTS_RAN_SUCCESSFULLY

def main():
    # Names of the scripts and output files
    script1 = 'ticket_scores.py'
    script2 = 'backlog.py'
    
    # Run the first and second scripts concurrently
    sprint_report = subprocess.Popen(['python', script1], stdout=sys.stdout, stderr=sys.stderr)
    backlog_report = subprocess.Popen(['python', script2], stdout=sys.stdout, stderr=sys.stderr)

    # Wait for both scripts to complete
    print(SCRIPTS_RUNNING)
    sprint_report.wait()
    backlog_report.wait()
    print(SCRIPTS_RAN_SUCCESSFULLY)


    if sprint_report.returncode != 0:
        print(f"Script {script1} failed. Error: {sprint_report.stderr.read().decode()}")
        return
    if backlog_report.returncode != 0:
        print(f"Script {script2} failed. Error: {backlog_report.stderr.read().decode()}")
        return

    # Files are present, proceed with email sending
    send_email()

if __name__ == "__main__":
    main()