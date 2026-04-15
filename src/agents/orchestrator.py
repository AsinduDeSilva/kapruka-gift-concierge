import concurrent.futures

from loguru import logger

from src.agents.reflection_agent import ReflectionAgent
from src.agents.router import Router
from src.agents.tools.catalog_search_tool import CatalogSearchTool
from src.agents.tools.direct_chat_tool import DirectChatTool
from src.agents.tools.logistics_tool import LogisticsTool
from src.agents.tools.preference_update_tool import PreferenceUpdateTool
from src.infrastructure.llm.llm_provider import get_chat_llm
from src.memory.semantic_memory_manager import SemanticMemoryManager
from src.memory.short_term_memory_manager import ShortTermMemoryManager


class AgentOrchestrator:
    def __init__(
            self,
            llm,
            semantic_memory,
            router,
            preference_tool,
            catalog_tool,
            logistics_tool,
            direct_chat_tool,
            reflection_agent
    ):
        self.llm = llm
        self.semantic_memory = semantic_memory
        self.router = router
        self.preference_tool = preference_tool
        self.catalog_tool = catalog_tool
        self.logistics_tool = logistics_tool
        self.direct_chat_tool = direct_chat_tool
        self.reflection_agent = reflection_agent

    def chat(self, user_id: str, user_query: str, st_memory: ShortTermMemoryManager) -> str:
        logger.info(f"Processing query for user {user_id}: {user_query}")

        # Routing
        decision = self.router.route(user_query, st_memory, user_id)
        logger.info(f"Routing decision: {decision}")

        tool_results = {}
        direct_chat_response = ""

        with concurrent.futures.ThreadPoolExecutor() as executor:
            concurrent_tasks = {}

            # Profile Update
            if decision.update_profile:
                logger.info("Scheduling user profile update...")
                concurrent_tasks[executor.submit(self.preference_tool.update_semantic_memory, user_id,
                                               user_query)] = "preference_update"

            # Direct Chat
            if decision.direct_chat:
                logger.info("Scheduling direct chat...")
                concurrent_tasks[executor.submit(self.direct_chat_tool.chat, user_query, st_memory)] = "direct_chat"
            else:
                # Catalog Search
                if decision.search_catalog:
                    logger.info("Scheduling catalog search...")
                    concurrent_tasks[executor.submit(self.catalog_tool.search, decision.vector_query,
                                                   decision.keyword_query)] = "catalog_search"

                # Check Logistics Feasibility
                if decision.check_logistics:
                    logger.info("Scheduling logistics feasibility check...")
                    concurrent_tasks[
                        executor.submit(self.logistics_tool.check_delivery_feasibility, decision.target_location,
                                        decision.vector_query)] = "logistics_check"

            for future in concurrent.futures.as_completed(concurrent_tasks):
                task_name = concurrent_tasks[future]
                try:
                    result = future.result()
                    if task_name == "direct_chat":
                        direct_chat_response = result
                    elif task_name == "catalog_search":
                        tool_results["catalog_results"] = result
                    elif task_name == "logistics_check":
                        tool_results["logistics_results"] = result.model_dump()
                except Exception as e:
                    logger.error(f"Task '{task_name}' generated an exception: {e}")

        if decision.direct_chat:
            st_memory.add_message("user", user_query)
            st_memory.add_message("assistant", direct_chat_response)
            return direct_chat_response

        # Reflection Loop
        final_response = self.reflection_agent.run(
            user_query=user_query,
            tool_results=tool_results,
            user_id=user_id,
            st_memory=st_memory
        )
        st_memory.add_message("user", user_query)
        st_memory.add_message("assistant", final_response)

        return final_response


def build_orchestrator():
    llm = get_chat_llm()
    memory = SemanticMemoryManager()

    return AgentOrchestrator(
        llm=llm,
        semantic_memory=memory,
        router=Router(llm, memory),
        preference_tool=PreferenceUpdateTool(llm, memory),
        catalog_tool=CatalogSearchTool(),
        logistics_tool=LogisticsTool(llm),
        direct_chat_tool=DirectChatTool(llm),
        reflection_agent=ReflectionAgent(llm, memory),
    )