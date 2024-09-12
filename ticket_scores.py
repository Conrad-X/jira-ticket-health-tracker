from jira import JIRA
from openpyxl import Workbook
from utils.config.jira import PARAMETERS , QUERIES , CUSTOMFIELD_IDS
from utils.config.others import SCORING , TEMPLATE_PLACEHOLDERS, TEMPLATE_HEADINGS
from utils.ticket_health import find_relevance_score,find_adherence_score, generate_perfect_adherence_description , generate_sprint_report
from utils.jira_functions import jira_instance
from utils.constants import NO_AMMENDMENTS_REQUIRED


issue_type=PARAMETERS['issuetype']

# JQL Query
jql_query = QUERIES['ticket_scores'].format(
    project=PARAMETERS['project'],
    issuetype = PARAMETERS['issuetype'],
    sprint=PARAMETERS['sprint']
)

# Fetch Bug Tickets
tickets = jira_instance.search_issues(jql_query)  # Limit to 5 tickets

# Open workbook
workbook = Workbook()
active_workbook = workbook.active

# Set the column headers
fieldnames = ['Issue', 'Relevance Score (%)', 'Adherence Score (%)', 'Total Score (%)' , 'Edited Description']
active_workbook.append(fieldnames)

# Process tickets 
for issue in tickets:
    task_template = getattr(issue.fields,CUSTOMFIELD_IDS['task_template_id'] , None) 
    bug_template = getattr(issue.fields, CUSTOMFIELD_IDS['bug_template_id'], None) 

    # Define mapping for issue types to template data
    
    issue_type_mapping = {
        "Task": {"placeholders": list(TEMPLATE_PLACEHOLDERS['task'].values()), "headings": TEMPLATE_HEADINGS['task_template_headings'], "template": task_template},
        "Bug": {"placeholders": list(TEMPLATE_PLACEHOLDERS['bug'].values()), "headings": TEMPLATE_HEADINGS['bug_template_headings'], "template": bug_template}  
        # Add issue type of your choice here 
    }

    # Get placeholders and headings based on issue type
    if issue_type in issue_type_mapping:
        placeholders = issue_type_mapping[issue_type]["placeholders"]
        headings = issue_type_mapping[issue_type]["headings"]
        
        # Check if description is in custom field or fallback to Jira description
        description_to_check = issue_type_mapping[issue_type]["template"] or issue.fields.description

    if description_to_check is None:
        adherence_score = 0
        relevance_score = 0 
        total_score = 0
    else:
        adherence_score = find_adherence_score(description_to_check, headings, placeholders)*100
        relevance_score = find_relevance_score(description_to_check, issue.fields.summary, placeholders)
        total_score = (
            SCORING['weightage_of_relevance'] * relevance_score +
            SCORING['weightage_of_adherence'] * adherence_score
        )

    if adherence_score < 100 or adherence_score < 100.0 :
            new_description = generate_perfect_adherence_description(description_to_check, headings)
    else:
        new_description = NO_AMMENDMENTS_REQUIRED

    # Write the row to the Excel sheet
    active_workbook.append([
        issue.key,
        f"{relevance_score:.2f}",
        f"{adherence_score:.2f}",
        f"{total_score:.2f}",
        new_description
    ])

    print(f"Issue: {issue.key}, Relevance Score: {relevance_score:.2f}%, Adherence Score: {adherence_score:.2f}%, Total Score: {total_score:.2f}%")

generate_sprint_report(active_workbook, workbook, excel_file_path="sprint_report.xlsx")