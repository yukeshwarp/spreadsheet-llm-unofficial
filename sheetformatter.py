import pandas as pd
from openai import AzureOpenAI
import json
import os
import logging

client = AzureOpenAI(
    azure_endpoint=os.getenv("ENDPOINT"),
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2024-10-01-preview",
)

def ask_question_about_excel(total_table, file, question):
    try:
        df = pd.read_excel(file)

        structural_anchors_df = identify_structural_anchors(df)
        inverted_index = create_inverted_index(structural_anchors_df)
        data_json = json.dumps(inverted_index)

        messages = [
            {"role": "system", "content": """You are an AI assistant that helps people find information, based on the uploaded spreadsheet data."""},
            {"role": "user", "content": f"""Here is some spreadsheet data:\n{data_json}\n\n 
                                            Data about the tables: {total_table}\n\n 
                                            Question: {question}"""}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.2
        )

        if response.choices:
            content = response.choices[0].message.content.strip()
            return content
        else:
            logging.error("Failed to get an answer: No response choices available.")
            return None
    except Exception as e:
        logging.error(f"An error occurred while processing the Excel file: {e}")
        return None


def identify_structural_anchors(df):
    homogeneous_rows = df.apply(lambda row: len(set(row)) == 1, axis=1)
    homogeneous_cols = df.apply(lambda col: len(set(col)) == 1, axis=0)
    heterogeneous_rows = ~homogeneous_rows
    heterogeneous_cols = ~homogeneous_cols

    structural_anchors_df = df.loc[heterogeneous_rows, heterogeneous_cols]

    return structural_anchors_df

def create_inverted_index(df):
    inverted_index = {}
    for row_idx, row in df.iterrows():
        for col_idx, value in row.items():
            if pd.notna(value):
                if value not in inverted_index:
                    inverted_index[value] = []
                inverted_index[value].append(f"{row_idx},{col_idx}")
    return inverted_index

def table_count_excel(file):
    try:
        df = pd.read_excel(file)

        structural_anchors_df = identify_structural_anchors(df)

        inverted_index = create_inverted_index(structural_anchors_df)
        data_json = json.dumps(inverted_index)

        messages = [
            {"role": "system", "content": """You are a helpful assistant tasked with counting the total number of tables (Only Tables not cells) and providing only short descriptions of the tables based on the given spreadsheets."""},
            {"role": "user", "content": f"Here is some spreadsheet data:\n{data_json}"}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.1,
        )

        if response.choices:
            content = response.choices[0].message.content.strip()
            return content
        else:
            logging.error("Failed to get an answer: No response choices available.")
            return None
    except Exception as e:
        logging.error(f"An error occurred while processing the Excel file: {e}")
        return None
