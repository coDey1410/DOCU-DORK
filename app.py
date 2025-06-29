import os
import uuid
import streamlit as st
import boto3
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

s3 = boto3.client("s3")
BUCKET = os.getenv("BUCKET_NAME")
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
embedder = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", client=bedrock_client)

def make_id(): return str(uuid.uuid4())

def split_docs(pages, size, overlap):
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
    return splitter.split_documents(pages)

def save_to_s3(req_id):
    base = f"/tmp/{req_id}"
    for ext in ("faiss","pkl"):
        fn = f"{base}.{ext}"
        key = f"{req_id}.{ext}"
        s3.upload_file(fn, BUCKET, key)

def load_from_s3(req_id):
    base = f"/tmp/{req_id}"
    for ext in ("faiss","pkl"):
        fn = f"{base}.{ext}"
        key = f"{req_id}.{ext}"
        s3.download_file(BUCKET, key, fn)

def build_index(req_id, docs):
    vs = FAISS.from_documents(docs, embedder)
    vs.save_local(index_name=f"/tmp/{req_id}", folder_path="/tmp")
    save_to_s3(req_id)
    return vs

def get_llm():
    return Bedrock(
        model_id="amazon.titan-text-lite-v1",
        client=bedrock_client,
        model_kwargs={"maxTokenCount":512,"temperature":0.7,"topP":0.9}
    )

st.title("Docu-Dork")

if "vs" not in st.session_state:
    st.session_state.vs = None
    st.session_state.req_id = None

uploaded = st.file_uploader("Upload a PDF", type="pdf")
if uploaded:
    rid = make_id()
    path = f"{rid}.pdf"
    with open(path,"wb") as f: f.write(uploaded.getvalue())
    pages = PyPDFLoader(path).load_and_split()
    chunks = split_docs(pages,1000,200)
    st.write(f"Loaded {len(pages)} pages → {len(chunks)} chunks")
    st.session_state.vs = build_index(rid, chunks)
    st.session_state.req_id = rid
    st.success("Index built and stored to S3")

if st.session_state.vs:
    q = st.text_input("Ask a question")
    if st.button("Submit"):
        llm = get_llm()
        prompt = PromptTemplate(
            template="""
Human: Use the context to answer concisely.
<context>
{context}
</context>
Question: {question}
Assistant:
""",
            input_variables=["context","question"]
        )
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=st.session_state.vs.as_retriever(search_type="similarity",search_kwargs={"k":5}),
            return_source_documents=False,
            chain_type_kwargs={"prompt":prompt}
        )
        with st.spinner("Thinking…"):
            ans = qa({"query":q})["result"]
        st.write(ans)
