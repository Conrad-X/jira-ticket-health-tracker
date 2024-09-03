from datetime import datetime,timezone
from jira import JIRA
from utils.config.jira import JIRA_CONFIG

# Jira Configuration Settings
jira_options = {'server':JIRA_CONFIG['server']}
jira = JIRA(options=jira_options, basic_auth=(JIRA_CONFIG['username'], JIRA_CONFIG['token']))

# Get Ticket Epic
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

# Get Priority
def get_priority(issue):
    return issue.fields.priority.name if issue.fields.priority else "No Priority"

# Get Ticket Issue Type
def get_issue_type(issue):
    # Return the issue type name
    return issue.fields.issuetype.name

# Get Time in Backlog
def get_time_in_backlog(created_date):
    current_date = datetime.now(timezone.utc)
    backlog_duration = (current_date - created_date).days
    return backlog_duration




