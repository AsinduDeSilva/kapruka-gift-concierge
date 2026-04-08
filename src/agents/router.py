import json

from langchain_core.prompts import ChatPromptTemplate

from src.agents.prompts.agent_prompts import router_user_prompt, router_system_prompt
from src.agents.schemas import RouterDecision
from src.memory.short_term_memory_manager import ShortTermMemoryManager


class Router:
    def __init__(self, llm, semantic_memory):
        self.llm = llm
        self.semantic_memory = semantic_memory

    def route(self, user_query: str, st_memory: ShortTermMemoryManager, user_id: str) -> RouterDecision:
        current_profile = self.semantic_memory.get_profile(user_id)

        prompt = ChatPromptTemplate.from_messages([
            ("system", router_system_prompt),
            ("user", router_user_prompt),
        ])

        chain = prompt | self.llm.with_structured_output(RouterDecision)

        return chain.invoke({
            "current_profile": json.dumps(current_profile, indent=2),
            "st_memory": st_memory.get_history(),
            "user_query": user_query
        })

