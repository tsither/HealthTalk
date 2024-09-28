import os
import time
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import AnyscaleEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone as PineconeStore
from langchain_community.chat_models import ChatAnyscale
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import pinecone

# Set API keys and environment variables
os.environ["ANYSCALE_API_KEY"] = ""
os.environ["PINECONE_API_KEY"] = ""
os.environ["HUGGINGFACEHUB_API_TOKEN"] = ""
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Connect to the SQLite database
engine = create_engine('sqlite:///Users/mymac/LLM/Personal-Medical-Assistant/database/SQL_medical_assistant.sql', echo=True)
Base = declarative_base()

# Define the report_type table
class ReportType(Base):
    __tablename__ = 'report_type'
    report_type_id = Column(Integer, primary_key=True, autoincrement=True)
    report_type_name = Column(String, nullable=False)

Session = sessionmaker(bind=engine)
session = Session()

# Load data 
pdf_loader = PyMuPDFLoader('Blood report.pdf')
Blood_reports = pdf_loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
pdf_doc = text_splitter.split_documents(Blood_reports)

# Initialize a LangChain embedding object
api_key = os.getenv("ANYSCALE_API_KEY")
embeddings = AnyscaleEmbeddings(
    anyscale_api_key=api_key, model="thenlper/gte-large"
)

# Initialize Pinecone
pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create index if it doesn't exist
index_name = "pp"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1024,
        metric="cosine",
        spec=pinecone.ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

# Initialize Pinecone index
index = pc.Index(index_name)

# Embed each chunk and upsert the embeddings into a distinct namespace
namespace = "pp1"
pineconeVector = PineconeStore.from_documents(
    documents=pdf_doc,
    index_name=index_name,
    embedding=embeddings,
    namespace=namespace
)

time.sleep(1)

# Initialize the language model with Anyscale
llm = ChatAnyscale(anyscale_api_key=os.getenv('ANYSCALE_API_KEY'), model='meta-llama/Meta-Llama-3-8B-Instruct')

# Initialize the Pinecone retriever
retriever = pineconeVector.as_retriever()
docs = retriever.invoke("what information is contained in the document")

# Define the system prompt
system_prompt = (
    "Use the given context to answer the question. "
    "If you don't know the answer, say you don't know. "
    "Use three sentences maximum and keep the answer concise. "
    "Context: {context}"
)

# Create the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)
# Create the question-answer chain
question_answer_chain = create_stuff_documents_chain(llm, prompt)
# Create the retrieval chain
chain = create_retrieval_chain(retriever, question_answer_chain)

#Query input
query = "What kind of report is this? Blood, urine, or other type?"

# Invoke the chain with the query
response = chain.invoke({"input": query})

# Extract the answer from the response
answer = response['answer']

print(answer)

# Extract the report type from the answer
if "blood" in answer.lower():
    report_type = "Blood report"
elif "urine" in answer.lower():
    report_type = "Urinalysis"
else:
    report_type = "Other report"

# Perform the query and update the database
query_vector = embeddings.embed_query(query)
results = index.query(vector=query_vector, top_k=10, namespace=namespace)  

for match in results['matches']:
    matched_id = match['id']

    # Check if the record already exists
    existing_record = session.query(ReportType).filter_by(report_type_name=report_type).first()
    if existing_record:
        print(f"Record with report_type_name '{report_type}' already exists.")
    else:
        # Insert a new record
        new_report_type = ReportType(
            report_type_name=report_type
        )
        session.add(new_report_type)

# Commit changes to the database
session.commit()
session.close()
