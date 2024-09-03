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