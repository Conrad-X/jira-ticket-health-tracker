import yaml
from jira import JIRA
from openai import OpenAI
import re
from datetime import datetime, timezone
import csv
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.drawing.image import Image


# Load configuration from the config.yaml file
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Select configuration for backlog
jql_query = config['queries']['backlog']['jql']
output_file = config['output_files']['backlog']
weightage_of_relevance = config['scoring']['weightage_of_relevance']
weightage_of_adherence = config['scoring']['weightage_of_adherence']
template_headings = config['template_headings']


# Connect to Jira
jira_options = {'server': config['jira']['server']}
jira = JIRA(options=jira_options, basic_auth=(config['jira']['username'], config['jira']['token']))

# Fetch Bug Tickets
tickets = jira.search_issues(jql_query, maxResults=10)  # Limit to 10 tickets

# OpenAI setup
client = OpenAI(api_key=config['openai']['api_key'])
model = config['openai']['model']

def check_relevance(description, summary):
    prompt = config['prompts']['relevance'].format(description=description, summary=summary)
    
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

def check_adherence(description, headings):
    prompt = config['prompts']['adherence'].format(description=description)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    content = response.choices[0].message.content
    match = re.search(r"Adherence Score\s*:\s*(\d+)", content, re.IGNORECASE)
    
    if match:
        adherence_score = float(match.group(1))
    else:
        print("Adherence Score not found.")
        adherence_score = 0.0  # Default or error value if score not found

    return adherence_score * 10  # Convert to percentage

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

with open(output_file, "w", newline='') as csvfile:
    fieldnames = ['Issue', 'Relevance Score (%)', 'Time in Backlog (days)', 'Priority' , 'Epic', 'Issue Type']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    for issue in tickets:
        description = issue.fields.description or ""
        summary = issue.fields.summary or ""
        created_date = datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z")

        relevance_score = check_relevance(description, summary)
        time_in_backlog = get_time_in_backlog(created_date)
        priority = get_priority(issue)
        epic = get_epic(issue)  
        issue_type = get_issue_type(issue) 

        writer.writerow({
            'Issue': issue.key,
            'Relevance Score (%)': f"{relevance_score:.2f}",
            'Time in Backlog (days)': time_in_backlog,
            'Priority': priority,
            'Epic': epic,
            'Issue Type': issue_type  
        })

print(f"Issue: {issue.key}, Relevance Score: {relevance_score:.2f}%, Time in Backlog: {time_in_backlog} days, Priority: {priority}")

#>20 days 

df = pd.read_csv("backlog.csv", encoding='utf-8')

# Filter tasks that have been in the backlog for more than 20 days
df_filtered = df[df['Time in Backlog (days)'] > 20]

# Generate a graph from the filtered DataFrame
plt.figure(figsize=(12, 8))
plt.bar(df_filtered['Issue'], df_filtered['Time in Backlog (days)'], color='red')
plt.title('Tasks in Backlog for More Than 20 Days')
plt.xlabel('Issue')
plt.ylabel('Time in Backlog (days)')
plt.xticks(rotation=45)
plt.tight_layout()

# Save the graph as an image
graph_image_path = "backlog_graph.png"
plt.savefig(graph_image_path)
plt.close()

## Graphy by epic
# Load CSV data into DataFrame
#df = pd.read_csv("backlog.csv", encoding='utf-8')

# Generate a graph by Epic
epic_counts = df['Epic'].value_counts()
plt.figure(figsize=(12, 8))
epic_counts.plot(kind='bar', color='skyblue')

plt.title('Number of Issues per Epic')
plt.xlabel('Epic')
plt.ylabel('Number of Issues')
plt.xticks(rotation=45)
plt.tight_layout()

# Save the graph as an image
epic_graph_image_path = "epic_graph.png"
plt.savefig(epic_graph_image_path)
plt.close()


# Generate a graph by Issue Type
type_counts = df['Issue Type'].value_counts()
plt.figure(figsize=(12, 8))
type_counts.plot(kind='bar', color='skyblue')

plt.title('Number of Issues by Type')
plt.xlabel('Issue Type')
plt.ylabel('Number of Issues')
plt.xticks(rotation=45)
plt.tight_layout()

# Save the graph as an image
type_graph_image_path = "type_graph.png"
plt.savefig(type_graph_image_path)
plt.close()


# Save DataFrame to Excel
excel_file_path = "backlog_report.xlsx"
df.to_excel(excel_file_path, index=False)

# Open the Excel file and embed the graphs
wb = Workbook()
ws = wb.active

# Add DataFrame data to the sheet
for r_idx, row in enumerate(pd.read_excel(excel_file_path).values.tolist(), 1):
    for c_idx, value in enumerate(row, 1):
        ws.cell(row=r_idx, column=c_idx, value=value)

# Load and add the images
graph_images = {
    "Backlog Graph": "backlog_graph.png",
    "Epic Graph": "epic_graph.png",
    "Type Graph": "type_graph.png",
}

positions = ['E2', 'E20', 'E38']  # Adjust positions if necessary

for position, (title, img_path) in zip(positions, graph_images.items()):
    img = Image(img_path)
    ws.add_image(img, position)  # Position the image in the Excel sheet

# Save the Excel file
wb.save(excel_file_path)
