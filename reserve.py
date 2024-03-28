api_key="AIzaSyBdRm6uYCOXILtiKQm6Vosv0CnZ439xraE"
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA


llm = ChatGoogleGenerativeAI(model="gemini-pro",google_api_key=api_key, temperature=0.7)
love=llm.invoke("explain love in 4 sentence")
#print(love)


loader = CSVLoader(file_path='covid_faq.csv', source_column='prompt', encoding='utf-8')
data = loader.load()
#print(data)

instructor_embeddings = HuggingFaceEmbeddings()
text = "This is a test document."
query_result = instructor_embeddings.embed_query("This is a test document.")
print(query_result[:3])
print(len(query_result))
vectordb = FAISS.from_documents(documents=data,embedding=instructor_embeddings)
retriever = vectordb.as_retriever()
rdocs = retriever.get_relevant_documents("what time it take to get corona virus")



prompt_template = """Given the following context and a question, generate an answer based on this context only.
In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
If the answer is not found in the context, kindly state "I don't know." Don't try to make up an answer.

CONTEXT: {context}

QUESTION: {question}"""


PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
chain_type_kwargs = {"prompt": PROMPT}


from langchain.chains import RetrievalQA

chain = RetrievalQA.from_chain_type(llm=llm,
                            chain_type="stuff",
                            retriever=retriever,
                            input_key="query",
                            return_source_documents=True,
                            chain_type_kwargs=chain_type_kwargs)


print(chain("what is corona virus and how it effect human"))


