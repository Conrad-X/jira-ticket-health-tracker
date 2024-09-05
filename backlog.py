from jira import JIRA
from openpyxl import Workbook
from datetime import datetime
from utils.config.jira import JIRA_CONFIG, PARAMETERS , QUERIES
from utils.config.others import SCORING 
from utils.ticket_health import find_relevance_score, generate_backlog_report
from utils.jira_functions import get_time_in_backlog, get_epic , get_issue_type, get_priority

# Project Config
project = PARAMETERS['project']
issuetype = PARAMETERS['issuetype']
sprint = PARAMETERS['sprint']

# JQL Query
jql_query = QUERIES['backlog'].format(
    project=project
)

# Connect to Jira
jira_options = {'server':JIRA_CONFIG['server']}
jira = JIRA(options=jira_options, basic_auth=(JIRA_CONFIG['username'], JIRA_CONFIG['token']))

# Fetch Bug Tickets
tickets = jira.search_issues(jql_query) 

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
        relevance_score = find_relevance_score(description_to_check, issue.fields.summary)

    summary = issue.fields.summary or ""
    created_date = datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z")
    relevance_score = find_relevance_score(description_to_check, summary)
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

    print(f"Issue: {issue.key}, Relevance Score: {relevance_score:.2f}%, Time in Backlog: {time_in_backlog} days, Priority: {priority}, Issue Type : {issue_type}")

# Convert the worksheet to a DataFrame for processing
generate_backlog_report(ws, wb, excel_file_path="backlog_report.xlsx")