import yaml
from jira import JIRA
from openai import OpenAI
import re
import csv
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.drawing.image import Image

# Load configuration from the config.yaml file
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

# Select configuration for Script 1
jql_query = config['queries']['ticket_scores']['jql']
output_file = config['output_files']['ticket_scores']
template_headings = config['template_headings']
weightage_of_relevance = config['scoring']['weightage_of_relevance']
weightage_of_adherence = config['scoring']['weightage_of_adherence']

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

#Output Results

with open(output_file, "w", newline='') as csvfile:
    fieldnames = ['Issue', 'Relevance Score (%)', 'Adherence Score (%)', 'Total Score (%)']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    for issue in tickets:
        description = issue.fields.description or ""
        summary = issue.fields.summary or ""
        relevance_score = check_relevance(description, summary)
        adherence_score = check_adherence(description, template_headings)
        
        total_score = (weightage_of_relevance * relevance_score + weightage_of_adherence * adherence_score)
        
        writer.writerow({
            'Issue': issue.key,
            'Relevance Score (%)': f"{relevance_score:.2f}",
            'Adherence Score (%)': f"{adherence_score:.2f}",
            'Total Score (%)': f"{total_score:.2f}"
        })

        print(f"Issue: {issue.key}, Relevance Score: {relevance_score:.2f}%, Adherence Score: {adherence_score:.2f}%, Total Score: {total_score:.2f}%")
    

# Load CSV data into DataFrame
df = pd.read_csv("jira_ticket_scores.csv", encoding='utf-8')

# Generate a graph from the DataFrame
plt.figure(figsize=(10, 6))
df.plot(x='Issue', y=['Relevance Score (%)', 'Adherence Score (%)', 'Total Score (%)'], kind='bar')
plt.title('Jira Ticket Scores')
plt.xlabel('Issue')
plt.ylabel('Scores')
plt.xticks(rotation=45)
plt.tight_layout()

# Save the graph as an image
graph_image_path = "graph_image.png"
plt.savefig(graph_image_path)
plt.close()

# Save DataFrame to Excel
excel_file_path = "output_with_graph.xlsx"
df.to_excel(excel_file_path, index=False)

# Open the Excel file and embed the graph
wb = Workbook()
ws = wb.active

# Add DataFrame data to the sheet
for r_idx, row in enumerate(pd.read_excel(excel_file_path).values.tolist(), 1):
    for c_idx, value in enumerate(row, 1):
        ws.cell(row=r_idx, column=c_idx, value=value)

# Load and add the image
img = Image(graph_image_path)
ws.add_image(img, 'E2')  # Position the image in the Excel sheet

# Save the Excel file
wb.save(excel_file_path)