import os
import streamlit as st

from main import SpreadsheetLLMWrapper
from tempfile import NamedTemporaryFile

class Arguments:
    def __init__(self, model, table, question):
        self.model = model
        self.table = table
        self.question = question

#Create temporary file to pull from
def process_sheet(wrapper):
    with NamedTemporaryFile(dir='.', suffix='.xls', delete=False) as f:
        f.write(file.getbuffer())
        wb = wrapper.read_spreadsheet(f.name)
        areas, compress_dict = wrapper.compress_spreadsheet(wb)   
    os.remove(f.name)  
    return areas, compress_dict

def identify_table(wrapper, model_name):
    if file:
        args.table = True
        args.model = model_name
        areas, compress_dict = process_sheet(wrapper)
        output = wrapper.llm(args, areas, compress_dict)
        st.session_state.messages.append({"role": "assistant", "content": output})
        args.table = False

args = Arguments('gpt-3.5', False, None)
wrapper = SpreadsheetLLMWrapper()


st.title("SpreadsheetGPT")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    st.write("File uploaded successfully.")

    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").markdown(message["content"])
        else:
            st.chat_message("assistant").markdown(message["content"])

    question = st.chat_input("Ask a question about the Excel file:")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})

        with st.spinner("Thinking..."):
            total_table = table_count_excel(uploaded_file)
            #answer = ask_question_about_excel(total_table, uploaded_file, question)
            try:
                df = pd.read_excel(uploaded_file)

                structural_anchors_df = identify_structural_anchors(df)
                inverted_index = create_inverted_index(structural_anchors_df)
                data_json = json.dumps(inverted_index)

                messages = [
                    {"role": "system", "content": """You are an AI assistant that helps people find information, based on the uploaded spreadsheet data."""},
                    {"role": "user", "content": f"""Here is some spreadsheet data:\n{data_json}\n\n 
                                                    Data about the tables: {total_table}\n\n 
                                                    Question: {question}"""}
                ]

                response_stream = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.2,
                    stream = True
                )

                bot_response = ""
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    for chunk in response_stream:
                        if chunk.choices:
                            bot_response += chunk.choices[0].delta.content or ""
                            response_placeholder.markdown(bot_response)

                st.session_state.messages.append({"role": "assistant", "content": bot_response})

            except Exception as e:
                st.error(f"An error occurred while processing the Excel file: {e}")

        st.rerun()
