import os
import transformers

from huggingface_hub import InferenceClient
from openai import AzureOpenAI

#If you only want to check how many tables
PROMPT_TABLE = """
You are an expert in analyzing spreadsheet data. Analyze the given table content and respond to the question asked by the user.
INSTRUCTION:
Given an input that is a string denoting data of cells in a table.
The input table contains many tuples, describing the cells with content in the spreadsheet.
Each tuple consists of two elements separated by a '|': the cell content and the cell address/region, like (Year|A1), ( |A1) or (IntNum|A1:B3).
The content in some cells such as '#,##0'/'d-mmm-yy'/'H:mm:ss',etc., represents the CELL DATA FORMATS of Excel.
The content in some cells such as 'IntNum'/'DateData'/'EmailData',etc., represents a category of data with the same format and similar semantics.
For example, 'IntNum' represents integer type data, and 'ScientificNum' represents scientific notation type data.
'A1:B3' represents a region in a spreadsheet, from the first row to the third row and from column A to column B.
Some cells with empty content in the spreadsheet are not entered.
"""

#Part 1 of CoS
STAGE_1_PROMPT = """INSTRUCTION:
Below is a question about one certain table in this spreadsheet.
I need you to determine in which table the answer to the following question can be found, and return the RANGE of the ONE table you choose, LIKE ['range':'A1:F9'].
DON'T ADD OTHER WORDS OR EXPLANATION.
INPUT: """

#Part 2 of CoS (after filtering out table)
STAGE_2_PROMPT = """INSTRUCTION:
Given an input that is a string denoting data of cells in a table and a question about this table.
The answer to the question can be found in the table.
The input table includes many pairs, and each pair consists of a cell address and the text in that cell with a ',' in between, like 'A1,Year'.
Cells are separated by '|' like 'A1,Year|A2,Profit'.
The text can be empty so the cell data is like 'A1, |A2,Profit'.
The cells are organized in row-major order.
The answer to the input question based on the content in the table and present in a human redable format."
INPUT: """

MODEL_DICT = {'mistral': 'mistralai/Mistral-7B-Instruct-v0.2',
              'llama-2': 'meta-llama/Llama-2-7b-chat-hf',
              'llama-3': 'meta-llama/Meta-Llama-3-8B-Instruct',
              'phi-3': 'microsoft/Phi-3-mini-128k-instruct',
              'gpt-3.5': 'gpt-3.5-turbo',
              'gpt-4': 'gpt-4'}

class SpreadsheetLLM():
    def __init__(self, model):
        self.model = model
    
    def call(self, prompt):
	    client = AzureOpenAI(
	    azure_endpoint=os.getenv('ENDPOINT'),
	    api_key=os.getenv('OPENAI_API_KEY'),
	    api_version="2024-10-01-preview",
	)
	    completion = client.chat.completions.create(
	    model="gpt-4o",
	    messages=[
		{"role" : "system", "content" : PROMPT_TABLE},
	      {"role": "user", "content": prompt}
	    ],
	    temperature = 0.0
	  )
	    return completion.choices[0].message.content    
    def identify_table(self, table):
        global PROMPT_TABLE
        return self.call(PROMPT_TABLE + str(table))

    def question_answer(self, table, question):
        global STAGE_1_PROMPT
        global STAGE_2_PROMPT

        #table_range = self.call(STAGE_1_PROMPT + str(table) + '\n QUESTION:' + question)
        return self.call(STAGE_2_PROMPT + str(table) + '\n QUESTION:' + question), str(table)
