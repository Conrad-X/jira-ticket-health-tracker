from utils.config.open_ai import PROMPTS,OPENAI
from openai import OpenAI
import re
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl.drawing.image import Image
from io import BytesIO

# OpenAI setup
client = OpenAI(api_key=OPENAI['api_key'])
model = OPENAI['model']

#Relevance Score
def find_relevance_score(description_to_check, summary):
    prompt = PROMPTS['relevance'].format(description=description_to_check, summary=summary)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    ) 
    content = response.choices[0].message.content
    match = re.search(r"Relevance Score\s*:\s*(\d+)", content, re.IGNORECASE)
    
    if match:
        relevance_score = float(match.group(1))
    else:
        print("Relevance Score not found.")
        relevance_score = 0.0  # Default or error value if score not found

    return relevance_score * 10  # Convert to percentage

#Is Placeholder Filled 
def is_placeholder_filled(description, placeholders):
    for placeholder in placeholders:
        if placeholder in description:
            return False
    return True

#Adherence Score
def find_adherence_score(description_to_check, headings, placeholders):
    if not is_placeholder_filled(description_to_check, placeholders):
        return 0.0

    joined_headings = ", ".join(headings)
    
    prompt = PROMPTS['adherence'].format(description=description_to_check, headings=joined_headings)
  
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    content = response.choices[0].message.content
    match = re.search(r"Adherence Score:\s*(0(\.\d+)?|1(\.0+)?)", content)
    
    if match:
        adherence_score = float(match.group(1))
    else:
        print("Adherence Score not found.")
        adherence_score = 0.0  # Default or error value if score not found

    return adherence_score

#Generate New description for tickets which do not a 100% adherence score
def generate_perfect_adherence_description(description_to_check, headings):

    joined_headings = ", ".join(headings)

    prompt = PROMPTS['adherence_restructure'].format(description=description_to_check, headings=joined_headings)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    content = response.choices[0].message.content
    return content.strip()

#Generate backlog report with graph embedded
def generate_backlog_report(ws,wb, excel_file_path):
    # Convert the worksheet to a DataFrame for processing
    data = ws.values
    columns = next(data)[0:]  # Get the header
    df = pd.DataFrame(data, columns=columns)

    # Convert 'Time in Backlog (days)' to numeric
    df['Time in Backlog (days)'] = pd.to_numeric(df['Time in Backlog (days)'])

    # Filter tasks that have been in the backlog for more than 20 days
    df_filtered = df[df['Time in Backlog (days)'] > 20]

    # Generate a graph from the filtered DataFrame
    plt.figure(figsize=(10, 6))
    plt.bar(df_filtered['Issue'], df_filtered['Time in Backlog (days)'], color='red')
    plt.title('Tasks in Backlog for More Than 20 Days')
    plt.xlabel('Issue')
    plt.ylabel('Time in Backlog (days)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the graph to a BytesIO object instead of a file
    backlog_graph_buffer = BytesIO()
    plt.savefig(backlog_graph_buffer, format="png")
    plt.close()
    backlog_graph_buffer.seek(0)

    # Generate a graph by Epic
    epic_counts = df['Epic'].value_counts()
    plt.figure(figsize=(12, 8))
    epic_counts.plot(kind='bar', color='skyblue')

    plt.title('Number of Issues per Epic')
    plt.xlabel('Epic')
    plt.ylabel('Number of Issues')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the graph to a BytesIO object instead of a file
    epic_graph_buffer = BytesIO()
    plt.savefig(epic_graph_buffer, format="png")
    plt.close()
    epic_graph_buffer.seek(0)

    # Generate a graph by Issue Type
    type_counts = df['Issue Type'].value_counts()
    plt.figure(figsize=(12, 8))
    type_counts.plot(kind='bar', color='skyblue')

    plt.title('Number of Issues by Type')
    plt.xlabel('Issue Type')
    plt.ylabel('Number of Issues')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the graph to a BytesIO object instead of a file
    type_graph_buffer = BytesIO()
    plt.savefig(type_graph_buffer, format="png")
    plt.close()
    type_graph_buffer.seek(0)

    # Load and add the images from the buffers to the Excel sheet
    ws.add_image(Image(backlog_graph_buffer), 'E2')  # Position the backlog graph
    ws.add_image(Image(epic_graph_buffer), 'E20')  # Position the epic graph
    ws.add_image(Image(type_graph_buffer), 'E38')  # Position the issue type graph

    # Save the Excel file
    wb.save(excel_file_path)


# Generate Sprint report with graph embedded 
def generate_sprint_report(ws,wb, excel_file_path):

    # Convert the worksheet to a DataFrame for plotting
    df = pd.DataFrame(ws.values)

    if df.empty:
        print("DataFrame is empty. No data to plot.")
    else:
        df.columns = df.iloc[0]  # Set the first row as the header
        df = df[1:]  # Remove the first row from the data

        # Convert the score columns to numeric (float) data types
        df['Relevance Score (%)'] = pd.to_numeric(df['Relevance Score (%)'])
        df['Adherence Score (%)'] = pd.to_numeric(df['Adherence Score (%)'])
        df['Total Score (%)'] = pd.to_numeric(df['Total Score (%)'])

        # Generate a graph from the DataFrame
        plt.figure(figsize=(10, 6))
        df.plot(x='Issue', y=['Relevance Score (%)', 'Adherence Score (%)', 'Total Score (%)'], kind='bar')
        plt.title('Jira Ticket Scores')
        plt.xlabel('Issue')
        plt.ylabel('Scores')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the graph to a BytesIO object instead of a file
        graph_buffer = BytesIO()
        plt.savefig(graph_buffer, format="png")
        plt.close()
        graph_buffer.seek(0)

        # Load and add the image from the buffer to the Excel sheet
        img = Image(graph_buffer)
        ws.add_image(img, 'M2')  # Position the image in the Excel sheet

    # Save the Excel file
    wb.save(excel_file_path)
