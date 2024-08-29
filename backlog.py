from jira import JIRA
from openai import OpenAI
import re
from datetime import datetime, timezone
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from io import BytesIO
import config  # Import the config.py module

# Select configuration for Script 1
weightage_of_relevance = config.SCORING['weightage_of_relevance']
weightage_of_adherence = config.SCORING['weightage_of_adherence']

# Connect to Jira
jira_options = {'server': config.JIRA_CONFIG['server']}
jira = JIRA(options=jira_options, basic_auth=(config.JIRA_CONFIG['username'], config.JIRA_CONFIG['token']))

# Project Config
project = config.PARAMETERS['project']
issuetype = config.PARAMETERS['issuetype']
sprint = config.PARAMETERS['sprint']

# JQL Query
jql_query = config.QUERIES['backlog'].format(
    project=project
)

# Fetch Bug Tickets
tickets = jira.search_issues(jql_query, maxResults=5)  # Limit to 5 tickets

# OpenAI setup
client = OpenAI(api_key=config.OPENAI_CONFIG['api_key'])
model = config.OPENAI_CONFIG['model']

def check_relevance(description_to_check, summary):
    prompt = config.PROMPTS['relevance'].format(description=description_to_check, summary=summary)
    
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

def get_time_in_backlog(created_date):
    current_date = datetime.now(timezone.utc)
    backlog_duration = (current_date - created_date).days
    return backlog_duration

def get_priority(issue):
    return issue.fields.priority.name if issue.fields.priority else "No Priority"

def get_epic(issue):
    # Check if the issue is an Epic
    if issue.fields.issuetype.name == "Epic":
        return issue.fields.summary  # Or return just the Epic name

    # Check if the issue has a parent (this is typically the case for sub-tasks)
    parent_issue = getattr(issue.fields, 'parent', None)
    
    if parent_issue:
        # Get the parent issue
        parent = jira.issue(parent_issue.key)
        # Check if the parent is an Epic
        if parent.fields.issuetype.name == "Epic":
            return f"Parent Epic: {parent.fields.summary}"  # Return the Epic name
        else:
            return f"Parent Issue: {parent.fields.summary}"  # Return the parent issue name
    else:
        return "No Parent"

def get_issue_type(issue):
    # Return the issue type name
    return issue.fields.issuetype.name

wb = Workbook()
ws = wb.active

# Set the column headers
fieldnames = ['Issue', 'Relevance Score (%)', 'Time in Backlog (days)', 'Priority', 'Epic', 'Issue Type']
ws.append(fieldnames)

# Process tickets and write data to Excel
for issue in tickets:

    # Default to using description field
    description_to_check = issue.fields.description
    task_template = getattr(issue.fields, 'customfield_10806', None)
    bug_template = getattr(issue.fields, 'customfield_10805', None)

    # Check if the Bug/Task template is filled out and contains the relevant sections
    if task_template:
        description_to_check = task_template
    if bug_template:
        description_to_check = bug_template

    if description_to_check is None:
        relevance_score = 0 
        total_score = 0

    else:
        relevance_score = check_relevance(description_to_check, issue.fields.summary)

    summary = issue.fields.summary or ""
    created_date = datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z")

    relevance_score = check_relevance(description_to_check, summary)
    time_in_backlog = get_time_in_backlog(created_date)
    priority = get_priority(issue)
    epic = get_epic(issue)  
    issue_type = get_issue_type(issue) 

    ws.append([
        issue.key,
        f"{relevance_score:.2f}",
        time_in_backlog,
        priority,
        epic,
        issue_type 
    ])

    print(f"Issue: {issue.key}, Relevance Score: {relevance_score:.2f}%, Time in Backlog: {time_in_backlog} days, Priority: {priority}")

# Convert the worksheet to a DataFrame for processing
data = ws.values
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
ws.add_image(Image(backlog_graph_buffer), 'E2')  # Position the backlog graph
ws.add_image(Image(epic_graph_buffer), 'E20')  # Position the epic graph
ws.add_image(Image(type_graph_buffer), 'E38')  # Position the issue type graph

# Save the Excel file
excel_file_path = "backlog_report.xlsx"
wb.save(excel_file_path)
