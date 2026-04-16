from langchain_core.prompts import ChatPromptTemplate

from src.agents.prompts.agent_prompts import logistics_system_prompt, logistics_user_prompt
from src.agents.schemas import LogisticsFeasibility


class LogisticsTool:
    def __init__(self, llm):
        self.llm = llm

    def check_delivery_feasibility(self, target_location: str, optimized_search_query: str) -> LogisticsFeasibility:
        prompt = ChatPromptTemplate.from_messages([
            ("system", logistics_system_prompt),
            ("user", logistics_user_prompt)
        ])

        chain = prompt | self.llm.with_structured_output(LogisticsFeasibility)

        return chain.invoke({
            "target_location": target_location,
            "optimized_search_query": optimized_search_query
        })
