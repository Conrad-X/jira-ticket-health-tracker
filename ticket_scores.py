import config
from jira import JIRA
from openai import OpenAI
import re
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from io import BytesIO

# Accessing the configuration
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
jql_query = config.QUERIES['ticket_scores'].format(
    project=project,
    issuetype=issuetype,
    sprint=sprint
)

# Fetch Bug Tickets
tickets = jira.search_issues(jql_query, maxResults=5)  # Limit to 5 tickets

# OpenAI setup
client = OpenAI(api_key=config.OPENAI_CONFIG['api_key'])
model = config.OPENAI_CONFIG['model']

def is_placeholder_filled(description, placeholders):
    for placeholder in placeholders:
        if placeholder in description:
            return False
    return True

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

# Check adherence function
def check_adherence(description_to_check, headings, placeholders):
    if not is_placeholder_filled(description_to_check, placeholders):
        return 0.0

    joined_headings = ", ".join(headings)
    
    prompt = config.PROMPTS['adherence'].format(description=description_to_check, headings=joined_headings)
  
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

    return adherence_score

wb = Workbook()
ws = wb.active

# Set the column headers
fieldnames = ['Issue', 'Relevance Score (%)', 'Adherence Score (%)', 'Total Score (%)']
ws.append(fieldnames)

# Process tickets and write data to Excel
for issue in tickets:
    # Default to using description field
    description_to_check = issue.fields.description
    task_template = getattr(issue.fields, 'customfield_10806', None)
    bug_template = getattr(issue.fields, 'customfield_10805', None)

    if issuetype == "Task" and task_template:
        placeholders = list(config.TEMPLATE_PLACEHOLDERS['task'].values())
        headings = config.TEMPLATE_HEADINGS['task_template_headings']
    elif issuetype == "Bug" and bug_template:
        placeholders = list(config.TEMPLATE_PLACEHOLDERS['bug'].values())
        headings = config.TEMPLATE_HEADINGS['bug_template_headings']
    elif issuetype == "Task":
        headings = config.TEMPLATE_HEADINGS['task_template_headings']
        placeholders = list(config.TEMPLATE_PLACEHOLDERS['task'].values())
    elif issuetype == "Bug":
        headings = config.TEMPLATE_HEADINGS['bug_template_headings']
        placeholders = list(config.TEMPLATE_PLACEHOLDERS['task'].values())
    else:
        headings = []

    # Check if the Bug/Task template is filled out and contains the relevant sections
    if task_template:
        description_to_check = task_template
    if bug_template:
        description_to_check = bug_template

    if description_to_check is None:
        adherence_score = 0
        relevance_score = 0 
        total_score = 0
    else:
        adherence_score = check_adherence(description_to_check, headings, placeholders)
        relevance_score = check_relevance(description_to_check, issue.fields.summary)
        total_score = (
            weightage_of_relevance * relevance_score +
            weightage_of_adherence * adherence_score
        )

    # Write the row to the Excel sheet
    ws.append([
        issue.key,
        f"{relevance_score:.2f}",
        f"{adherence_score:.2f}",
        f"{total_score:.2f}"
    ])

    print(f"Issue: {issue.key}, Relevance Score: {relevance_score:.2f}%, Adherence Score: {adherence_score:.2f}%, Total Score: {total_score:.2f}%")

# Convert the worksheet to a DataFrame for plotting
df = pd.DataFrame(ws.values)

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
    ws.add_image(img, 'M2')  # Position the image in the Excel sheet

# Save the Excel file
excel_file_path = "ticket_scores.xlsx"
wb.save(excel_file_path)