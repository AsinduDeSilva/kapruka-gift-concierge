from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.prompts.agent_prompts import direct_chat_system_prompt, direct_chat_user_prompt
from src.infrastructure.llm.llm_provider import get_chat_llm
from src.memory.short_term_memory_manager import ShortTermMemoryManager


class DirectChatTool:
    def __init__(self):
        self.llm = get_chat_llm()

    def chat(self, user_query: str, st_memory: ShortTermMemoryManager):
        prompt = ChatPromptTemplate.from_messages([
            ("system", direct_chat_system_prompt),
            ("user", direct_chat_user_prompt)
        ])

        chain = prompt | self.llm | StrOutputParser()

        return chain.invoke({
            "chat_history": st_memory.get_history(),
            "user_query": user_query
        })