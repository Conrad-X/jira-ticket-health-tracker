from jira import JIRA
from openpyxl import Workbook
from datetime import datetime
from utils.config.jira import PARAMETERS,QUERIES,CUSTOMFIELD_IDS
from utils.config.others import TEMPLATE_PLACEHOLDERS
from utils.ticket_health import find_relevance_score,generate_backlog_report
from utils.jira_functions import get_time_in_backlog,get_epic,get_issue_type,get_priority,jira_instance


issue_type=PARAMETERS['issuetype']

# JQL Query
jql_query = QUERIES['backlog'].format(
    project=PARAMETERS['project']
)

# Fetch Bug Tickets
tickets = jira_instance.search_issues(jql_query, maxResults = 100)  

#Open workbook
workbook = Workbook()
active_workbook = workbook.active

# Set the column headers
fieldnames = ['Issue', 'Relevance Score (%)', 'Time in Backlog (days)', 'Priority', 'Epic', 'Issue Type']
active_workbook.append(fieldnames)

# Process tickets and write data to Excel
for issue in tickets:

    # Default to using description field
    task_template = getattr(issue.fields, CUSTOMFIELD_IDS['task_template_id'] , None) 
    bug_template = getattr(issue.fields, CUSTOMFIELD_IDS['bug_template_id'], None)  

    # Define mapping for issue types to template data
    issue_type_mapping = {
        "Task": {"template": task_template, "placeholders": list(TEMPLATE_PLACEHOLDERS['task'].values())},
        "Bug": {"template": bug_template, "placeholders": list(TEMPLATE_PLACEHOLDERS['bug'].values())}
        # Add issue type of your choice here
    }

    # Get description and placeholders based on issue type
    if issue_type in issue_type_mapping:
        description_to_check = issue_type_mapping[issue_type]["template"] or issue.fields.description
        placeholders = issue_type_mapping[issue_type]["placeholders"]
    
    if description_to_check is None: 
        relevance_score = 0 
        total_score = 0

    summary = issue.fields.summary or ""
    created_date = datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z")
    relevance_score = find_relevance_score(description_to_check, summary,placeholders)
    time_in_backlog = get_time_in_backlog(created_date)
    priority = get_priority(issue)
    epic = get_epic(issue)  
    issue_type = get_issue_type(issue) 

    active_workbook.append([
        issue.key,
        f"{relevance_score:.2f}",
        time_in_backlog,
        priority,
        epic,
        issue_type 
    ])

    print(f"Issue: {issue.key}, Relevance Score: {relevance_score:.2f}%, Time in Backlog: {time_in_backlog} days, Priority: {priority}, Issue Type : {issue_type}")

# Convert the worksheet to a DataFrame for processing
generate_backlog_report(active_workbook, workbook, excel_file_path="backlog_report.xlsx")