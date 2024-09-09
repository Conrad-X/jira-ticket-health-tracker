import os
import boto3
from botocore.exceptions import NoCredentialsError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from utils.constants import EMAIL_SUBJECT, EMAIL_BODY_TEXT, NO_CREDENTIALS_ERROR, EMAIL_SENDING_FAILED , FILE_NOT_FOUND

# AWS SES Configuration
SES_REGION = os.getenv('SES_REGION')
SES_SENDER = os.getenv('SES_SENDER')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

def send_email(recipients):
    # Initialize the SES client
    ses_client = boto3.client('ses', region_name=SES_REGION,
                              aws_access_key_id=AWS_ACCESS_KEY,
                              aws_secret_access_key=AWS_SECRET_KEY)

    subject = EMAIL_SUBJECT
    body_text = EMAIL_BODY_TEXT
    # Files to attach
    files = ["sprint_report.xlsx", "backlog_report.xlsx"]
    
    # Create the multipart container for the email
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = SES_SENDER

    # Join recipient emails into a single string for the 'To' header
    msg['To'] = ", ".join(recipients)

    # Print email addresses to confirm they are correct
    print(f"Sending to: {msg['To']}")

    # Attach the body of the email as plain text
    msg.attach(MIMEText(body_text, 'plain'))

    # Attach files to the email
    for file in files:
        try:
            with open(file, "rb") as attachment_file:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(attachment_file.read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename={os.path.basename(file)}'
                )
                msg.attach(attachment)
        except FileNotFoundError:
            print(FILE_NOT_FOUND)
            continue

    # Send the email using SES
    try:
        response = ses_client.send_raw_email(
            Source=SES_SENDER,
            Destinations=recipients,  # Pass the list of recipients here
            RawMessage={
                'Data': msg.as_string(),
            }
        )
        print("Email sent! Message ID:", response['MessageId'])
    except NoCredentialsError:
        print(NO_CREDENTIALS_ERROR)
    except Exception as e:
       print(f"{EMAIL_SENDING_FAILED:}{e.text}")