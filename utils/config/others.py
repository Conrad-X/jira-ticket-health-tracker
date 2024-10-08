SCORING = {
    "weightage_of_relevance": 0.5,
    "weightage_of_adherence": 0.5
}

TEMPLATE_PLACEHOLDERS = {
    "bug": {
        "summary": "[A concise description of the issue or task.]",
        "steps_to_reproduce": "[Detailed steps that lead to the issue, including screenshots if possible.]",
        "technical_notes": "[Any technical information that might be helpful for the developer, such as dependencies, libraries, or code snippets].",
        "testing_instructions": "[Instructions or considerations for testing the task or fix.]"
    },
    "task": {
        "summary": "[A concise description of the issue or task.]",
        "accebtability_criteria": "[List the conditions that must be met for the task to be considered complete.]",
        "technical_notes": "[Any technical information that might be helpful for the developer, such as dependencies, libraries, or code snippets].",
        "testing_instructions": "[Instructions or considerations for testing the task or fix.]"
    },
    "story":{
        # Add if you require
    },
    "epic":{
        # Add if you require
    }
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
    ],
    "story_template_headings":[
        # Add if you require
    ],
    "epic_template_headings":[
        # Add if you require
    ]
}