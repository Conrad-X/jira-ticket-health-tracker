import subprocess
from utils.ticket_health import send_email

def main():
    # Names of the scripts and output files
    script1 = 'ticket_scores.py'
    script2 = 'backlog.py'
    
    # Run the first and second scripts concurrently
    process1 = subprocess.Popen(['python', script1], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process2 = subprocess.Popen(['python', script2], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for both scripts to complete
    print("Scripts are running")
    process1.wait()
    process2.wait()

    # Check if both scripts have completed successfully
    if process1.returncode != 0:
        print(f"Script {script1} failed. Error: {process1.stderr.read().decode()}")
        return
    if process2.returncode != 0:
        print(f"Script {script2} failed. Error: {process2.stderr.read().decode()}")
        return

    # Add emails of recepients
    recipients = ['person1@conradlabs.com','person1@conradlabs.com']

    # Files are present, proceed with email sending
    send_email(recipients)

if __name__ == "__main__":
    main()