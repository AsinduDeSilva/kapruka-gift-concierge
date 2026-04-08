from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.prompts.agent_prompts import logistics_system_prompt, logistics_user_prompt
from src.infrastructure.llm.llm_provider import get_chat_llm


class LogisticsTool:
    def __init__(self):
        self.llm = get_chat_llm()

    def check_delivery_feasibility(self, target_location, optimized_search_query):
        prompt = ChatPromptTemplate.from_messages([
            ("system", logistics_system_prompt),
            ("user", logistics_user_prompt)
        ])

        chain = prompt | self.llm | JsonOutputParser()

        return chain.invoke({
            "target_location": target_location,
            "optimized_search_query": optimized_search_query
        })