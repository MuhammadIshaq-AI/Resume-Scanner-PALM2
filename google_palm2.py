# -*- coding: utf-8 -*-
"""google-palm2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1U1U-wuu4Qhji_G4740IXrazdnopb7eMS
"""

!pip install langchain
!pip install pinecone-client
!pip install pypdf
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import GooglePalmEmbeddings
from langchain.llms import GooglePalm
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import pinecone
import os
import sys

loader = PyPDFDirectoryLoader("/content/area")
data = loader.load()

data[0]

text_splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
text_chunks = text_splitter.split_documents(data)

len(text_chunks)

!pip install --upgrade google-api-python-client

os.environ['GOOGLE_API_KEY'] = ''

!pip install google.generativeai

embeddings=GooglePalmEmbeddings()
query_result = embeddings.embed_query("Hello World")

embeddings

print("Length",len(query_result))

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY', '')
PINECONE_API_ENV = os.environ.get('PINECONE_API_ENV', '')

# initialize pinecone
pinecone.init(
    api_key=PINECONE_API_KEY,  # find at app.pinecone.io
    environment=PINECONE_API_ENV  # next to api key in console
)
index_name = "lama2" # put in the name of your pinecone index here

docsearch = Pinecone.from_texts([t.page_content for t in text_chunks], embeddings, index_name=index_name)

docsearch=Pinecone.from_existing_index(index_name,embeddings)

query="Hi"

docs = docsearch.similarity_search(query, k=3)

llm = GooglePalm(temperature=0.1)

qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())

prompt_template="""Act as AI resume shortlisting agent.\
You are provided a pdf resume\
Scan the resume and extract the main keywords from it.\
Give summary of the resume whether the person is talented or not.

{context}

Question: {question}
Helpful answer in markdown:"""

prompt=PromptTemplate(template=prompt_template,input_variables=["context","question"])

query = "What is work experience"

qa.run(query)

!pip install gradio

import sys
import gradio as gr
conversation_history = []

custom_css = """
    .gr-textbox input {
        height: 200px;
    }
"""
def answer_question(user_input):
    if user_input == 'exit':
        print('Exiting')
        sys.exit()
    if user_input == '':
        return 'Please enter a question.'

    result = qa.run(user_input)
    answer = result  # Since result is assumed to be a string in this code
    return answer


iface = gr.Interface(
    fn=answer_question,
    inputs=gr.inputs.Textbox(type="text", label="Input Question"),
    outputs=gr.outputs.Textbox(type="text", label="Answer"),
    title="ResuMate: Smart Resume Analysis and Candidate Evaluation",
    description="Ask a question and get an answer. Type 'exit' to quit.",
    theme="huggingface",
    layout="vertical",
    css=custom_css,  # Apply the custom CSS styles
)

iface.launch(share=True)

