
# config.py

JIRA_CONFIG = {
    "server":  "",
    "username": "",
    "token": ""
}

Test = {
    "name": "hello"
}

OPENAI_CONFIG = {
    "api_key": "",
    "model": "gpt-4o"
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

PROMPTS = {
    "relevance": '''
        You are a helpful assistant. A Jira ticket has the following summary: "{summary}".
        The description provided is: "{description}". Please analyze it based on the provided template headings.
        Rate how well the description aligns with the summary on a scale of 1 to 10, where 1 means not aligned at all and 10 means perfectly aligned. Also, provide a brief explanation for the score.
        Print out your output. 
        Write Relevance Score as Relevance Score: 
    ''',
    "adherence": '''
        You are a helpful assistant. A Jira ticket has the following description under the Description heading: "{description}".
        The template requires the following sections: {headings}.
        Print out your output.
        Check how many of these sections are present and rate the adherence as a percentage. Write it as Adherence Score:
    '''
}

SCORING = {
    "weightage_of_relevance": 0.5,
    "weightage_of_adherence": 0.5
}

TEMPLATE_PLACEHOLDERS = {
    "bug": {
        "summary": "[A concise description of the issue or task.]",
        "steps_to_reproduce": "[Detailed steps that lead to the issue, including screenshots if possible.]",
        "technical_notes": "[Any technical information that might be helpful for the developer, such as dependencies, libraries, or code snippets.]",
        "testing_instructions": "[Instructions or considerations for testing the task or fix.]"
    },
    "task": {
        "summary": "[A concise description of the task.]",
        "steps_to_reproduce": "[Detailed steps to complete the task.]",
        "technical_notes": "[Technical information relevant to the task.]",
        "testing_instructions": "[Instructions for verifying the task's completion.]"
    }
}