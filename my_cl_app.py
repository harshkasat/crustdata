import chainlit as cl
from main import main

@cl.on_chat_start
def on_chat_start():
    cl.user_session.set('chat_history', [])

@cl.on_message
async def on_message(message: cl.Message):
    chat_history = cl.user_session.get('chat_history', [])
    llm_response = await main(user_input=message.content, chat_history=chat_history)
    await cl.Message(content=llm_response).send()
