# Jira Ticket Health Tracker

This repository contains a set of Python scripts designed to automate the analysis of Jira tickets. The scripts generate Excel reports that evaluate sprint health and backlog health through multiple metrics like adherence score, relevance score and duration in backlog etc. 

**Adherence Score:** The adherence score measures how closely the description of a Jira issue follows a predefined template or set of headings. It checks if all required sections and details are present and correctly structured within the issue description. 

**Relevance Score:** The relevance score evaluates how well the content of a Jira issue's description aligns with the issue's summary. It checks for the presence of meaningful and pertinent information that directly relates to the issue being addressed.

```bash
/project-root
│
├── main.py                 # Main script to trigger other scripts and send emails
├── ticket_scores.py        # Script to generate Sprint Report 
├── backlog.py              # Script to analyze Jira backlog and generate reports
│
├── utils/
│   ├── config/
│   │   ├── jira.py         # Jira-related configurations and helper functions
│   │   ├── open_ai.py      # OpenAI-related configurations and helper functions
│   │   ├── other.py        # Other configurations and utility functions
│   ├── graphs/
│   │   ├── graphs.py       # Functions to generate different graphs from Jira data
│   │   ├── constants.py    # Constants specifically related to graph generation
│   ├── constants.py        # Global constants used throughout the project (error messages, etc.)
│   ├── email.py            # Function to handle email sending using AWS SES
│   ├── jira_functions.py   # Jira-specific functions for ticket processing
│   ├── ticket_health.py    # Functions to assess the health of Jira tickets and general utility functions
│
├── image/                  # Folder to store generated images or graphs
├── .env                    # Environment variables for AWS SES and other configurations
├── .gitignore              # Ignore unnecessary files and folders
├── requirements.txt        # Python dependencies for the project              
└── README.md               # Project documentation
```

## Scripts

### main.py

This script orchestrates the execution of the two main scripts—ticket_scores.py and backlog.py. It runs these scripts sequentially, passing configuration files and parameters as needed. 

### ticket_scores.py

This script calculates the adherence and relevance scores of Jira tickets based on predefined templates and creates an improved ticket description if required. The script generates an Excel report containing the scores and plots relevant graphs for visualization.

### backlog.py
This script analyzes Jira backlog tickets on many different fields. It generates bar graphs for tasks in the backlog, issues by epic, and issues by type. These graphs are added to an Excel report.


## Utility Scripts (utils/)

### config/
- **`jira.py`**: Contains configurations related to Jira API interactions.
- **`open_ai.py`**: Manages OpenAI configurations and helper functions for processing Jira ticket descriptions.
- **`other.py`**: Contains any other necessary configurations and utility functions.

### jira_functions.py

Houses functions specifically related to processing Jira tickets, including fetching ticket details.

### ticket_health.py

Contains functions to assess the overall health of Jira tickets, including adherence and relevance scoring mechanisms.

### email.py

After the scripts are executed, the generated Excel reports are emailed to the specified recipients using AWS SES using functions in this script.

### graphs.py

Houses all the functions to generate all graphs included in the reports. Has a constants file in the same directory for all graph related fiels and titles. 

### constants.py 

Contains all the error messages and global constants used in the scripts. 

## Setup

### Clone the Repository

```
git clone <repository-url>
cd jira-ticket-health-tracker
```

### Python Installation

You will need python for this project. If not available please install python on your system. 
Those using `python3` are required to edit this in line 12-13 in `main.py` accordingly:

```python
    sprint_report = subprocess.Popen(['python3', script1], stdout=sys.stdout, stderr=sys.stderr)
    backlog_report = subprocess.Popen(['python3', script2], stdout=sys.stdout, stderr=sys.stderr)
```

### Install Dependencies 

Install the required Python packages using pip:

**For Python:**

```
pip install -r requirements.txt
```

**For Python3:**
```
pip3 install -r requirements.txt
```

### Set up Jira Configuration

```bash
JIRA_CONFIG = {
    "server":  " ",
    "username": " ",
    "token": " "
}
```

`Server:` Url you can see in the address bar. Example: https://cdccnet.atlassian.net

`Username:` Your email through which you have access to the Jira Project

`Token:` API token you need to authenticate the script. Here is how you can get it:

1. Log into Jira Software and click your profile image.
2. Click Manage Your Account.
3. Navigate to Security and click Create and manage API tokens.
4. Click Create and Manage API tokens.
5. Enter a Label and click Create.

For more help please click [here](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/). 

```bash
PARAMETERS = {
    "project": " ",
    "issuetype": " ",
    "sprint": " "
}
```

`project:` The project key for your Jira project. To find your project key follow these steps:

Your Project Key is the prefix of the issue number. In the example of CDCC-123, the “CDCC” portion of the issue number is the Project Key.

If you are still unsure, click on Project Settings for your Jira Project in the lower left corner and the key is displayed under project details.

    * Note: You must be a project administrator for the project or a Jira administrator in order to view the Project Settings page.
    
`issue_type:` Choose whatever issue type you want to generate a report for from Task, Bug , Epic , Story etc. (Ensure you pass it as "Task" not "task" etc. )

    * Note: If you use any other issue type other than task or bug, please configure it first as explained in the section below. Issue types can only be paas

`sprint:` Pass you sprint id here. Displayed right on top of your sprint board. 
Note: If your sprint id has spaces in the title for eg: Sprint 22 please pass it as "sprint": "'Sprint 22'"

```bash
QUERIES = {
    "ticket_scores": "project = {project} AND issue_type = {issuetype} AND Sprint = {sprint}",
    "backlog": "project = {project} AND Sprint IS EMPTY AND statusCategory != Done"
}
```

Will automatically pick the parameters you pass. You can alter this as per your need, for instance you can edit your sprint query to cater for all issue types like this:

```bash
"ticket_scores": "project = {project} AND Sprint = {sprint}"
```
Please not that if you edit your query here for `ticket_scores` to the one mentioned above you will have to edit your query in `ticket_scores.py` accordingly:
```bash
# JQL Query
jql_query = QUERIES['ticket_scores'].format(
    project=PARAMETERS['project'],
    sprint=PARAMETERS['sprint']
)
```
Similarly any change in 

```bash
"backlog": "project = {project} AND Sprint IS EMPTY AND statusCategory != Done"
```
will need a change in query in `backlog.py`:

```bash
# JQL Query
jql_query = QUERIES['backlog'].format(
    project=PARAMETERS['project']
)
```

### Limiting query results 

You are required to limit your backlog report to a total of 100 tickets. This has been done in `backlog.py` in this manner:

```bash
tickets = jira_instance.search_issues(jql_query, maxResults = 100)
```

Any change in number of tickets is supposed to be made here. This can be applied to `tickets.py` in the same manner.

### Set up OpenAI configuration

```bash
OPENAI = {
    "api_key": "",
    "model": "gpt-4o"
}
```

`api_key:` Please reach out to Maham Sheikh(maham.sheikh@conradlabs.com) or Awais Kamran(awais.kamran@conradlabs.com) for the api_key. 

Prompts mentioned in this config file can be customised to fit team needs.

### Set up other configuration 

```bash
SCORING = {
    "weightage_of_relevance": 0.5,
    "weightage_of_adherence": 0.5
}
```
This defines weightage for individual scores to generate the total score as: 

  total_score = (
            weightage_of_relevance * relevance_score +
            weightage_of_adherence * adherence_score
        )

You may tweak them as per your need. 

```TEMPLATE PLACEHOLDERS:```

If a default template is in place in the issue type description field for your project a placeholder check is necassary for finding out the correct adherence score.
A default template may look like this:


<div style="text-align: center;">
    <img src="/image/task_template.png" alt="Sample task description template" width="400"/>
</div>

You can add templates of your choice in this setion. 

```bash
TEMPLATE_HEADINGS = {
    "task_template_headings": [
        "Summary",
        "Acceptability Criteria",
        "Technical Notes",
        "Testing Instructions"
    ],
    "bug_template_headings": [
        "Summary",
        "Steps to Reproduce",
        "Technical Notes",
        "Testing Instructions"
    ]
    }
```

Headings against which the adherence score is checked. You may change them according to your project needs. 

### Adding more issue types 

In the backlog.py and main.py script edit this section for adding more issue types. Make sure you have the templates and placeholders in place depending on your need. 
```bash
for issue in tickets:
    task_template = getattr(issue.fields,CUSTOMFIELD_IDS['task_template_id'] , None) 
    bug_template = getattr(issue.fields, CUSTOMFIELD_IDS['bug_template_id'], None) 

    # Define mapping for issue types to template data
    
    issue_type_mapping = {
        "Task": {"placeholders": list(TEMPLATE_PLACEHOLDERS['task'].values()), "headings": TEMPLATE_HEADINGS['task_template_headings'], "template": task_template},
        "Bug": {"placeholders": list(TEMPLATE_PLACEHOLDERS['bug'].values()), "headings": TEMPLATE_HEADINGS['bug_template_headings'], "template": bug_template}  
        # Add issue type of your choice here 
    }
```

### Set up Environment Variables in .env

Make sure you name your file as .env.

Add your AWS SES credentials and other necessary environment variables as shown.

```bash
SES_REGION=<your-aws-region>
SES_SENDER=<your-sender-email>
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
SES_RECEPIENT_LIST=<your-email-recepients>
```
**Note:** You can pass multiple recepients in this form : 

```bash
SES_RECEPIENT_LIST=person1@conradlabs.com,person2@conradlabs.com 
```

Please contact Maham Sheikh at maham.sheikh@conradlabs.com to obtain these credentials.

This automation setup allows for seamless generation and analysis of Jira ticket reports, ensuring that stakeholders are informed about the state of the backlog and ticket descriptions.


