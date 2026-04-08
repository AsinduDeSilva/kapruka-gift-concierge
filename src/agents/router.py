import json

from langchain_core.prompts import ChatPromptTemplate

from src.agents.prompts.agent_prompts import router_user_prompt, router_system_prompt
from src.agents.schemas import RouterDecision
from src.infrastructure.llm.llm_provider import get_chat_llm
from src.memory.semantic_memory_manager import SemanticMemoryManager


class Router:
    def __init__(self):
        self.llm = get_chat_llm()
        self.memory_manager = SemanticMemoryManager()

    def route(self, user_query, st_memory, user_id) -> RouterDecision:
        current_profile = self.memory_manager.get_profile(user_id)

        prompt = ChatPromptTemplate.from_messages([
            ("system", router_system_prompt),
            ("user", router_user_prompt),
        ])

        chain = prompt | self.llm.with_structured_output(RouterDecision)

        return chain.invoke({
            "current_profile": json.dumps(current_profile, indent=2),
            "st_memory": st_memory,
            "user_query": user_query
        })

