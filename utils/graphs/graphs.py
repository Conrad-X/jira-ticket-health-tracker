import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from graphs.constants import *

# Graphs for backlog report 

# Generates a bar graph for tasks in the backlog for more than the specified number of days.

def generate_backlog_duration_graph(df, days_threshold=20):
    # Convert 'Time in Backlog (days)' to numeric
    df['Time in Backlog (days)'] = pd.to_numeric(df['Time in Backlog (days)'])

    # Filter tasks that have been in the backlog for more than 'days_threshold' days
    df_filtered = df[df['Time in Backlog (days)'] > days_threshold]

    # Generate a graph from the filtered DataFrame
    plt.figure(figsize=(10, 6))
    plt.bar(df_filtered['Issue'], df_filtered['Time in Backlog (days)'], color='red')
    plt.title(f'Tasks in Backlog for More Than {days_threshold} Days')
    plt.xlabel('Issue')
    plt.ylabel('Time in Backlog (days)')
    plt.title(BACKLOG_DURATION_GRAPH_TITLE)
    plt.xlabel(BACKLOG_DURATION_X_LABEL)
    plt.ylabel(BACKLOG_DURATION_Y_LABEL)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the graph to a BytesIO object instead of a file
    backlog_graph_buffer = BytesIO()
    plt.savefig(backlog_graph_buffer, format=IMAGE_FORMAT)
    plt.close()
    
    # Move the buffer pointer to the start
    backlog_graph_buffer.seek(0)

    return backlog_graph_buffer

# Generates a bar graph for the number of issues by Issue Type.

def generate_issue_type_graph(df):
  
    type_counts = df['Issue Type'].value_counts()
    
    plt.figure(figsize=(10, 6))
    type_counts.plot(kind='bar', color='skyblue')

    plt.title(ISSUE_TYPE_GRAPH_TITLE)
    plt.xlabel(ISSUE_TYPE_X_LABEL)
    plt.ylabel(ISSUE_TYPE_Y_LABEL)
    plt.title('Number of Issues by Type')
    plt.xlabel('Issue Type')
    plt.ylabel('Number of Issues')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the graph to a BytesIO object instead of a file
    type_graph_buffer = BytesIO()
    plt.savefig(type_graph_buffer, format=IMAGE_FORMAT)
    plt.close()
    
    # Move the buffer pointer to the start
    type_graph_buffer.seek(0)

    return type_graph_buffer


# Generates a bar graph for the number of issues per Epic.
def generate_epic_graph(df):
   
    epic_counts = df['Epic'].value_counts()
    
    plt.figure(figsize=(10, 6))
    epic_counts.plot(kind='bar', color='skyblue')
    
    plt.title(EPIC_TYPE_GRAPH_TITLE)
    plt.xlabel(EPIC_TYPE_X_LABEL)
    plt.ylabel(EPIC_TYPE_Y_LABEL)
    plt.title('Number of Issues per Epic')
    plt.xlabel('Epic')
    plt.ylabel('Number of Issues')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the graph to a BytesIO object instead of a file
    epic_graph_buffer = BytesIO()
    plt.savefig(epic_graph_buffer, format=IMAGE_FORMAT)
    plt.close()
    
    # Move the buffer pointer to the start
    epic_graph_buffer.seek(0)

    return epic_graph_buffer


# Graph for sprint report 

# Generates a bar graph for Jira ticket scores, including relevance, adherence, and total scores.

def generate_ticket_scores_graph(df):    
    
    # Generate a graph from the DataFrame
    plt.figure(figsize=(10, 6))
    df.plot(x='Issue', y=['Relevance Score (%)', 'Adherence Score (%)', 'Total Score (%)'], kind='bar')

    plt.title(TICKET_SCORES_GRAPH_TITLE)
    plt.xlabel(TICKET_SCORES_X_LABEL)
    plt.ylabel(TICKET_SCORES_Y_LABEL)
    plt.title('Jira Ticket Scores')
    plt.xlabel('Issue')
    plt.ylabel('Scores')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the graph to a BytesIO object instead of a file
    sprint_graph_buffer = BytesIO()
    plt.savefig(sprint_graph_buffer, format=IMAGE_FORMAT)
    plt.close()
    
    # Move the buffer pointer to the start
    sprint_graph_buffer.seek(0)

    return sprint_graph_buffer
