from typing import Optional
from pydantic import BaseModel, Field

class RouterDecision(BaseModel):
    update_profile: bool = Field(description="true ONLY IF the user provides NEW preferences, allergies, or facts.")
    search_catalog: bool = Field(description="true IF the user wants to look for, buy, or get recommendations for gifts.")
    check_logistics: bool = Field(description="true IF the user asks about delivery availability to a specific area.")
    direct_chat: bool = Field(description="true IF the user is just saying hello, thank you, or making small talk that requires NO tools or catalog searches.")
    target_location: Optional[str] = Field(description="String (District/City) or null")
    optimized_search_query: Optional[str] = Field(description="String for hybrid vector search or null")

class LogisticsFeasibility(BaseModel):
    deliverable: bool = Field(description="Whether the product can be safely transported to the target district.")
    reason: str = Field(description="A brief, 1-sentence explanation of why it is or isn't feasible based on physics, distance, or climate.")
