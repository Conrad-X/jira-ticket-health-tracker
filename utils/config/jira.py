JIRA_CONFIG = {
    "server":  "",
    "username": "",
    "token": ""
}

PARAMETERS = {
    "project": "",
    "issuetype": "",
    "sprint": ""
}

QUERIES = {
    "ticket_scores": "project = {project} AND issuetype = {issuetype} AND Sprint = {sprint}",
    "backlog": "project = {project} AND Sprint IS EMPTY AND statusCategory != Done"
}