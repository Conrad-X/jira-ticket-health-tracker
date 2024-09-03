from jira import JIRA
from openpyxl import Workbook
from utils.config.jira import JIRA_CONFIG, PARAMETERS , QUERIES
from utils.config.others import SCORING , TEMPLATE_PLACEHOLDERS, TEMPLATE_HEADINGS
from utils.ticket_health import find_relevance_score,find_adherence_score, generate_perfect_adherence_description , generate_sprint_report

# Connect to Jira
jira_options = {'server': JIRA_CONFIG['server']}
jira = JIRA(options=jira_options, basic_auth=(JIRA_CONFIG['username'], JIRA_CONFIG['token']))

# Project Config
project = PARAMETERS['project']
issuetype = PARAMETERS['issuetype']
sprint = PARAMETERS['sprint']

#weightage relevance
weightage_of_relevance = SCORING['weightage_of_relevance']
weightage_of_adherence = SCORING['weightage_of_adherence']


# JQL Query
jql_query = QUERIES['ticket_scores'].format(
    project=project,
    issuetype=issuetype,
    sprint=sprint
)

# Fetch Bug Tickets
tickets = jira.search_issues(jql_query, maxResults=5)  # Limit to 5 tickets

wb = Workbook()
ws = wb.active

# Set the column headers
fieldnames = ['Issue', 'Relevance Score (%)', 'Adherence Score (%)', 'Total Score (%)' , 'Edited Description']
ws.append(fieldnames)

# Process tickets 
for issue in tickets:
    # Default to using description field
    description_to_check = issue.fields.description
    task_template = getattr(issue.fields, 'customfield_10806', None) #Add your own customfield id here if you have any template
    bug_template = getattr(issue.fields, 'customfield_10805', None) #Add your own customfield id here if you have any template 

    if issuetype == "Task" and task_template:
        placeholders = list(TEMPLATE_PLACEHOLDERS['task'].values())
        headings = TEMPLATE_HEADINGS['task_template_headings']
        description_to_check = task_template
    elif issuetype == "Bug" and bug_template:
        placeholders = list(TEMPLATE_PLACEHOLDERS['bug'].values())
        headings = TEMPLATE_HEADINGS['bug_template_headings']
        description_to_check = bug_template
    elif issuetype == "Task":
        headings = TEMPLATE_HEADINGS['task_template_headings']
        placeholders = list(TEMPLATE_PLACEHOLDERS['task'].values())
    elif issuetype == "Bug":
        headings = TEMPLATE_HEADINGS['bug_template_headings']
        placeholders = list(TEMPLATE_PLACEHOLDERS['task'].values())
    else:
        headings = []

    if description_to_check is None:
        adherence_score = 0
        relevance_score = 0 
        total_score = 0
    else:
        adherence_score = find_adherence_score(description_to_check, headings, placeholders)*100
        relevance_score = find_relevance_score(description_to_check, issue.fields.summary)
        total_score = (
            weightage_of_relevance * relevance_score +
            weightage_of_adherence * adherence_score
        )

    if adherence_score < 100 or adherence_score < 100.0 :
            new_description = generate_perfect_adherence_description(description_to_check, headings)
    else:
        new_description = "No Ammendment Required"

    # Write the row to the Excel sheet
    ws.append([
        issue.key,
        f"{relevance_score:.2f}",
        f"{adherence_score:.2f}",
        f"{total_score:.2f}",
        new_description
    ])

    print(f"Issue: {issue.key}, Relevance Score: {relevance_score:.2f}%, Adherence Score: {adherence_score:.2f}%, Total Score: {total_score:.2f}%")

generate_sprint_report(ws, wb, excel_file_path="sprint_report.xlsx")