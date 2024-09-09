from jira import JIRA

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

#Modify your queries as per your need 

QUERIES = {
    "ticket_scores": "project = {project} AND issue_type = {issue_type} AND Sprint = {sprint}",
    "backlog": "project = {project} AND Sprint IS EMPTY AND statusCategory != Done"
}


