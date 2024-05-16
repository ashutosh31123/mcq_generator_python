import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file,get_table_data
import streamlit as st 
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

#loading json file
with open('C:\\Users\\31ash\\Desktop\\mcq_generator\\Response.json', 'r') as file:
    RESPONSE_JSON=json.load(file)

#creating a title for the app
st.title("MCQs creator application with langchain")

#Create a form using st.form 
with st.form("user_inputs"):
    #file upload
    uploaded_file=st.file_uploader("Upload a PDF or txt file")

    #input fields
    mcq_count=st.number_input("No.of MCQs",min_value=1,max_value=30)

    #Subject
    subject=st.text_input("Insert subject",max_chars=20)

    #Quiz tone
    tone=st.text_input("Complexity level of questions", max_chars=20,placeholder="Simple")

    #Add Button
    button=st.form_submit_button("Create MCQs")

    #Check if the button is clicked and all fields have input

    if button and uploaded_file is not None and mcq_count and subject and tone :
        with st.spinner("loading..."):
            try:
                text=read_file(uploaded_file)
                #Count tokens and the cost of API call
                #setting up Token usage tracking in langchain
                with get_openai_callback() as cb:
                    response=generate_evaluate_chain(
                        {
                        "text":text,
                        "number":mcq_count,
                        "subject":subject,
                        "tone":tone,
                        "response_json":json.dumps(RESPONSE_JSON)
                        }
                    )
            except Exception as e:
                traceback.print_exception(type(e),e,e.__traceback__)
                st.error("Error")
                 
            else :
                print(f"total tokens:{cb.total_tokens}")
                print(f"Prompt tokens:{cb.prompt_tokens}")
                print(f"Completion tokens:{cb.completion_tokens}")
                print(f"total cost:{cb.total_cost}")
                if isinstance(response,dict): 
                    #Extract the quiz data from the responses
                    quiz=response.get("quiz",None)
                    if quiz is not None:
                       table_data=get_table_data(quiz) 
                       if table_data is not None:
                           df=pd.DataFrame(table_data)
                           df.index=df.index+1
                           st.table(df)
                           #Display the review in a text box
                           st.text_area(label="Review",value=response["review"])
                       else:
                           st.error("Error in the table data")  
                    else:        
                        st.write(response)   
                            
                            
                            
