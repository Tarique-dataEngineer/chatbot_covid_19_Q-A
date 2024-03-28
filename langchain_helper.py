import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.environ["GOOGLE_API_KEY"], temperature=0)

instructor_embeddings = HuggingFaceEmbeddings()
vector_db_file_path = "faiss_index"

def create_vector_db():
    loader = CSVLoader(file_path='covid_faq.csv', source_column='prompt', encoding='utf-8')
    data = loader.load()
    vectordb = FAISS.from_documents(documents=data, embedding=instructor_embeddings)
    vectordb.save_local(vector_db_file_path)


def get_qa_chain():
    # Load the vector database from the local folder
    vectordb = FAISS.load_local(vector_db_file_path, instructor_embeddings, allow_dangerous_deserialization=True)
    
    # Create a retriever for querying the vector database
    retriever = vectordb.as_retriever(score_threshold=0.7)  # Adjust threshold as needed

    prompt_template = """Given the following context and a question, generate an answer based on this context only.
        In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
        If the answer is not found in the context, kindly state "I don't know." Don't try to make up an answer.
        
    CONTEXT: {context}

    QUESTION: {question}"""


    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}

    chain = RetrievalQA.from_chain_type(llm=llm,
                                        chain_type="stuff",
                                        retriever=retriever,
                                        input_key="query",
                                        return_source_documents=True,
                                        chain_type_kwargs=chain_type_kwargs)
    
    return chain  # Return the chain object

if __name__=="__main__":
    create_vector_db()
    chain = get_qa_chain()
    print(chain.invoke("what is corona virus"))
 