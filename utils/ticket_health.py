from utils.config.open_ai import PROMPTS,OPENAI
from openai import OpenAI
import re
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl.drawing.image import Image
from io import BytesIO
import os
import boto3
from botocore.exceptions import NoCredentialsError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


# OpenAI setup
client = OpenAI(api_key=OPENAI['api_key'])
model = OPENAI['model']

#Relevance Score
def find_relevance_score(description_to_check, summary):
    prompt = PROMPTS['relevance'].format(description=description_to_check, summary=summary)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    ) 
    content = response.choices[0].message.content
    match = re.search(r"Relevance Score\s*:\s*(\d+)", content, re.IGNORECASE)
    if match:
        relevance_score = float(match.group(1))
    else:
        print("Relevance Score not found.")
        relevance_score = 0.0  # Default or error value if score not found
    return relevance_score * 10  # Convert to percentage

#Adherence Score
def find_adherence_score(description_to_check, headings, placeholders):

    joined_headings = ", ".join(headings)
    prompt = PROMPTS['adherence'].format(description=description_to_check, headings=joined_headings)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content
    match = re.search(r"Adherence Score:\s*(0(\.\d+)?|1(\.0+)?)", content)
    if match:
        adherence_score = float(match.group(1))
    else:
        print("Adherence Score not found.")
        adherence_score = 0.0  # Default or error value if score not found
    return adherence_score

#Generate New description for tickets which do not a 100% adherence score
def generate_perfect_adherence_description(description_to_check, headings):

    joined_headings = ", ".join(headings)
    prompt = PROMPTS['adherence_restructure'].format(description=description_to_check, headings=joined_headings)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content
    return content.strip()

#Generate backlog report with graph embedded
def generate_backlog_report(active_workbook,workbook, excel_file_path):
    # Convert the worksheet to a DataFrame for processing
    data = active_workbook.values
    columns = next(data)[0:]  # Get the header
    df = pd.DataFrame(data, columns=columns)

    # Convert 'Time in Backlog (days)' to numeric
    df['Time in Backlog (days)'] = pd.to_numeric(df['Time in Backlog (days)'])

    # Filter tasks that have been in the backlog for more than 20 days
    df_filtered = df[df['Time in Backlog (days)'] > 20]

    # Generate a graph from the filtered DataFrame
    plt.figure(figsize=(10, 6))
    plt.bar(df_filtered['Issue'], df_filtered['Time in Backlog (days)'], color='red')
    plt.title('Tasks in Backlog for More Than 20 Days')
    plt.xlabel('Issue')
    plt.ylabel('Time in Backlog (days)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the graph to a BytesIO object instead of a file
    backlog_graph_buffer = BytesIO()
    plt.savefig(backlog_graph_buffer, format="png")
    plt.close()
    backlog_graph_buffer.seek(0)

    # Generate a graph by Epic
    epic_counts = df['Epic'].value_counts()
    plt.figure(figsize=(10, 6))
    epic_counts.plot(kind='bar', color='skyblue')

    plt.title('Number of Issues per Epic')
    plt.xlabel('Epic')
    plt.ylabel('Number of Issues')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the graph to a BytesIO object instead of a file
    epic_graph_buffer = BytesIO()
    plt.savefig(epic_graph_buffer, format="png")
    plt.close()
    epic_graph_buffer.seek(0)

    # Generate a graph by Issue Type
    type_counts = df['Issue Type'].value_counts()
    plt.figure(figsize=(10, 6))
    type_counts.plot(kind='bar', color='skyblue')

    plt.title('Number of Issues by Type')
    plt.xlabel('Issue Type')
    plt.ylabel('Number of Issues')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the graph to a BytesIO object instead of a file
    type_graph_buffer = BytesIO()
    plt.savefig(type_graph_buffer, format="png")
    plt.close()
    type_graph_buffer.seek(0)

    # Load and add the images from the buffers to the Excel sheet
    active_workbook.add_image(Image(backlog_graph_buffer), 'E2')  # Position the backlog graph
    active_workbook.add_image(Image(epic_graph_buffer), 'E20')  # Position the epic graph
    active_workbook.add_image(Image(type_graph_buffer), 'E38')  # Position the issue type graph

    # Save the Excel file
    workbook.save(excel_file_path)


# Generate Sprint report with graph embedded 
def generate_sprint_report(active_workbook,workbook, excel_file_path):

    # Convert the worksheet to a DataFrame for plotting
    df = pd.DataFrame(active_workbook.values)

    if df.empty:
        print("DataFrame is empty. No data to plot.")
    else:
        df.columns = df.iloc[0]  # Set the first row as the header
        df = df[1:]  # Remove the first row from the data

        # Convert the score columns to numeric (float) data types
        df['Relevance Score (%)'] = pd.to_numeric(df['Relevance Score (%)'])
        df['Adherence Score (%)'] = pd.to_numeric(df['Adherence Score (%)'])
        df['Total Score (%)'] = pd.to_numeric(df['Total Score (%)'])

        # Generate a graph from the DataFrame
        plt.figure(figsize=(10, 6))
        df.plot(x='Issue', y=['Relevance Score (%)', 'Adherence Score (%)', 'Total Score (%)'], kind='bar')
        plt.title('Jira Ticket Scores')
        plt.xlabel('Issue')
        plt.ylabel('Scores')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the graph to a BytesIO object instead of a file
        graph_buffer = BytesIO()
        plt.savefig(graph_buffer, format="png")
        plt.close()
        graph_buffer.seek(0)

        # Load and add the image from the buffer to the Excel sheet
        img = Image(graph_buffer)
        active_workbook.add_image(img, 'M2')  # Position the image in the Excel sheet

    # Save the Excel file
    workbook.save(excel_file_path)

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

    subject = "Weekly Jira Script Reports"
    body_text = "Here are the weekly reports generated by the Jira scripts.\nPlease find the attached files."

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
            print(f"File {file} not found. Skipping attachment.")
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
        print("AWS credentials not available")
    except Exception as e:
        print(f"Failed to send email: {e}")
