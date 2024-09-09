import subprocess
from utils.email import send_email

def main():
    # Names of the scripts and output files
    script1 = 'ticket_scores.py'
    script2 = 'backlog.py'
    
    # Run the first and second scripts concurrently
    sprint_report = subprocess.Popen(['python', script1], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    backlog_report = subprocess.Popen(['python', script2], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for both scripts to complete
    print("Scripts are running")
    sprint_report.wait()
    backlog_report.wait()

    # Check if both scripts have completed successfully
    if sprint_report.returncode != 0:
        print(f"Script {script1} failed. Error: {sprint_report.stderr.read().decode()}")
        return
    if backlog_report.returncode != 0:
        print(f"Script {script2} failed. Error: {backlog_report.stderr.read().decode()}")
        return

    # Add emails of recepients
    recipients = ['maham.sheikh@conradlabs.com']

    # Files are present, proceed with email sending
    send_email(recipients)

if __name__ == "__main__":
    main()