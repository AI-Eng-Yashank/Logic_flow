from typing import List, Union
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from config import GROQ_API_KEY


def call_groq(model: str, system_prompt: str, messages: Union[str, List[BaseMessage]]) -> str:
    chat = ChatGroq(temperature=0, model_name=model, groq_api_key=GROQ_API_KEY)
    
    formatted_messages = []
    if system_prompt:
        formatted_messages.append(SystemMessage(content=system_prompt))
    
    if isinstance(messages, str):
        formatted_messages.append(HumanMessage(content=messages))
    else:
        # Extend with history/context
        formatted_messages.extend(messages)
        
    response = chat.invoke(formatted_messages)
    return response.content
