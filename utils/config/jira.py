JIRA_CONFIG = {
    "server":  "",
    "username": "",
    "token": ""
}

PARAMETERS = {
    "project": "",
    "issue_type": "",
    "sprint": ""
}

QUERIES = {
    "ticket_scores": "project = {project} AND issue_type = {issue_type} AND Sprint = {sprint}",
    "backlog": "project = {project} AND Sprint IS EMPTY AND statusCategory != Done"
}