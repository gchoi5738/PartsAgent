from typing import List, Dict
from langchain_core.prompts import PromptTemplate  # Updated import
from langchain_core.output_parsers import PydanticOutputParser  # Updated import
from pydantic import BaseModel, Field


class ProductQuery(BaseModel):
  search_terms: List[str] = Field(description="Key search terms from the user's query")
  appliance_type: str = Field(description="Type of appliance (refrigerator or dishwasher)")
  part_type: str = Field(description="Specific part being discussed")
  action_needed: str = Field(description="What the user wants to do (buy, install, troubleshoot)")


class QueryParser:
  def __init__(self):
    self.parser = PydanticOutputParser(pydantic_object=ProductQuery)
    self.prompt = PromptTemplate(
        template="Extract key information from this customer query.\n{format_instructions}\nQuery: {query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": self.parser.get_format_instructions()}
    )

  async def parse_query(self, query: str) -> ProductQuery:
    """Parse user query into structured format"""
    try:
      formatted_prompt = self.prompt.format(query=query)
      return self.parser.parse(formatted_prompt)
    except Exception as e:
      raise Exception(f"Error parsing query: {str(e)}")
