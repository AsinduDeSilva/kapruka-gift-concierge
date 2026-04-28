from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.infrastructure.observability import observe, get_langfuse_callbacks
from src.agents.prompts.agent_prompts import direct_chat_system_prompt, direct_chat_user_prompt
from src.memory.short_term_memory_manager import ShortTermMemoryManager


class DirectChatTool:
    def __init__(self, llm):
        self.llm = llm

    @observe(name="direct_chat")
    def chat(self, user_query: str, st_memory: ShortTermMemoryManager):
        prompt = ChatPromptTemplate.from_messages([
            ("system", direct_chat_system_prompt),
            ("user", direct_chat_user_prompt)
        ])

        chain = prompt | self.llm | StrOutputParser()

        return chain.invoke({
            "chat_history": st_memory.get_history(),
            "user_query": user_query
        }, config={"callbacks": get_langfuse_callbacks()})