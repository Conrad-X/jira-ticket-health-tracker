JIRA_CONFIG = {
    "server":  " ",
    "username": " ",
    "token": " "
}

PARAMETERS = {
    "project": " ",
    "issuetype": " ",
    "sprint": " "
}

QUERIES = {
    "ticket_scores": "project = {project} AND issuetype = {issuetype} AND Sprint = {sprint}",
    "backlog": "project = {project} AND Sprint IS EMPTY AND statusCategory != Done"
}

#Add your own customfield id here if you have any template or custom field you want to work with

CUSTOMFIELD_IDS = {
    "task_template_id" : "customfield_10806",
    "bug_template_id" : "customfield_10805"
}

