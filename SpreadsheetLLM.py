import os
import transformers

from huggingface_hub import InferenceClient
from openai import AzureOpenAI
#Part 1 of CoS
STAGE_1_PROMPT = """INSTRUCTION:
- Below is a question about one certain table in this spreadsheet.
- Answer to the question based **strictly and only** based on the content fron the table.
- Respond with all relevant content to the question in detail and well explained manner.
- Present the response in a human redable format.
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
	      {"role": "user", "content": prompt}
	    ]
	  )
	    return completion.choices[0].message.content


    def question_answer(self, table, question):
	    return self.call(STAGE_1_PROMPT + str(table) + '\n QUESTION:' + question)
        #table_range = 
	
        #return self.call(STAGE_2_PROMPT + str(question + table_range + '\n QUESTION:' + question))
