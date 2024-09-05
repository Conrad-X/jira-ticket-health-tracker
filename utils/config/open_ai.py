OPENAI = {
    "api_key": "",
    "model": "gpt-4o"
}

PROMPTS = {
    "relevance": '''
        You are a helpful assistant. A Jira ticket has the following summary: "{summary}".
        The description provided is: "{description}". Please analyze it based on the provided template headings.
        Rate how well the description aligns with the summary on a scale of 1 to 10, where 1 means not aligned at all and 10 means perfectly aligned. Also, provide a brief explanation for the score.
        Write Relevance Score clearly as "Relevance Score: <score>".
        Also keep in mind that the headings should not have placeholder values under them. If such a case occurs adjust relevance score accordingly. If the entire description consists of basically the template values that means relevance score is 0. If description is left empty it also means 0.
    ''',
    "adherence": '''
        You are a helpful assistant. A Jira ticket has the following description: "{description}".
        The template requires the following sections: {headings}.
        
        Check how many of these sections are present and calculate the adherence score as a decimal between 0 and 1. 
        The score should be calculated by dividing the number of present sections by the total number of sections in the headings only. 
        Do not take anything else as a heading. STRICTLY ADHERE to the headings you are provided with. If they are not present, the adherence score should be 0. 
        
        For example:
        - If 3 out of 5 sections are present, the adherence score should be 0.6.
        - If 3 out of 4 sections are present, the adherence score should be 0.75.

        Also keep in mind that the headings should not have placeholder values under them. If such a case occurs adjust adherence score accordingly. 
        
        Print the adherence score clearly as "Adherence Score: <score>".
    ''',
    "adherence_restructure": '''
        The current Jira ticket description is: "{description}".
        It is required to match the following headings: {headings}.
        Please restructure and rephrase the description to fit perfectly under each heading with 100 percent adherence.
        Provide the revised description with sections clearly separated by headings.
    '''
}