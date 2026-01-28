from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class MemoryManager:
    def __init__(self):
        self.messages: List[BaseMessage] = []

    def add_user_message(self, message: str):
        self.messages.append(HumanMessage(content=message))

    def add_ai_message(self, message: str):
        self.messages.append(AIMessage(content=message))

    def get_messages(self) -> List[BaseMessage]:
        return self.messages

    def clear(self):
        self.messages = []
