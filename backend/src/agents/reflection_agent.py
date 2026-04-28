import json
from loguru import logger
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.agents.prompts.agent_prompts import (
    draft_system_prompt,
    draft_user_prompt,
    reflection_system_prompt,
    reflection_user_prompt,
    revision_system_prompt,
    revision_user_prompt
)
from src.agents.schemas import ReflectionCritique
from src.infrastructure.observability import observe, get_langfuse_callbacks
from src.memory.semantic_memory_manager import SemanticMemoryManager
from src.memory.short_term_memory_manager import ShortTermMemoryManager


class ReflectionAgent:
    def __init__(self, llm, semantic_memory: SemanticMemoryManager):
        self.llm = llm
        self.semantic_memory = semantic_memory
        
        self.draft_prompt = ChatPromptTemplate.from_messages([
            ("system", draft_system_prompt),
            ("user", draft_user_prompt)
        ])
        
        self.reflection_prompt = ChatPromptTemplate.from_messages([
            ("system", reflection_system_prompt),
            ("user", reflection_user_prompt)
        ])
        
        self.revision_prompt = ChatPromptTemplate.from_messages([
            ("system", revision_system_prompt),
            ("user", revision_user_prompt)
        ])

    @observe(name="reflection_agent")
    def run(
        self,
        user_query: str,
        tool_results: dict,
        user_id: str,
        st_memory: ShortTermMemoryManager,
        max_iterations: int = 3
    ) -> str:

        logger.info("Starting reflection loop...")

        user_profile = self.semantic_memory.get_profile(user_id)

        draft_chain = self.draft_prompt | self.llm | StrOutputParser()
        current_draft = draft_chain.invoke({
            "user_query": user_query,
            "tool_results": json.dumps(tool_results, indent=2),
            "profile": user_profile,
            "memory": st_memory.get_history(),
        }, config={"callbacks": get_langfuse_callbacks()})

        for i in range(max_iterations):
            logger.info(f"Reflection iteration {i + 1} for draft...")
            reflect_chain = self.reflection_prompt | self.llm.with_structured_output(ReflectionCritique)
            critique = reflect_chain.invoke({
                "proposed_gifts": current_draft,
                "profile": user_profile
            }, config={"callbacks": get_langfuse_callbacks()})
            
            if critique.is_safe:
                logger.info("Draft is safe. Exiting reflection loop.")
                break
                
            logger.warning(f"Draft violates safety/preferences: {critique.violations}")
            
            logger.info("Revising draft to fix violations...")
            revise_chain = self.revision_prompt | self.llm | StrOutputParser()
            current_draft = revise_chain.invoke({
                "draft": current_draft,
                "critique": critique.violations
            }, config={"callbacks": get_langfuse_callbacks()})
            
        return current_draft
