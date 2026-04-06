import json

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.prompts.agent_prompts import preference_update_system_prompt, preference_update_user_prompt
from src.infrastructure.llm.llm_provider import get_chat_llm
from src.memory.semantic_memory_manager import SemanticMemoryManager


class PreferenceUpdateTool:
    def __init__(self):
        self.memory_manager = SemanticMemoryManager()
        self.llm = get_chat_llm()

    def update_semantic_memory(self, user_id, user_message):
        current_profile = self.memory_manager.get_profile(user_id)

        prompt = ChatPromptTemplate.from_messages([
            ("system", preference_update_system_prompt),
            ("user", preference_update_user_prompt)
        ])

        chain = prompt | self.llm | JsonOutputParser()

        updated_profile = chain.invoke({
            "current_profile": json.dumps(current_profile, indent=2),
            "user_message": user_message
        })

        self.memory_manager.save_profile(user_id, updated_profile)




