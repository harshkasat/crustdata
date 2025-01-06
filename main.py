from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from vectorstore import get_llm_model, get_history_aware
from langchain_core.messages import AIMessage, HumanMessage

async def rag_response():
    llm = get_llm_model()
    prompt = ChatPromptTemplate.from_template("""
    Answer the context in a formatted and detailed way.
    <context>
    {context}
    </context>

    Question: {input}
    """)
    document_chain = create_stuff_documents_chain(llm, prompt)
    history_aware_retriever = get_history_aware()
    return create_retrieval_chain(history_aware_retriever, document_chain)

async def main(user_input: str, chat_history: list) -> str:
    session = await rag_response()
    response = session.invoke({"input": user_input, "chat_history": chat_history})
    chat_history.extend([
        HumanMessage(content=user_input),
        AIMessage(content=response["answer"]),
    ])
    return response["answer"]
