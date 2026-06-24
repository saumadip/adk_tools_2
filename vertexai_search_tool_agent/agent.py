import os
import sys
sys.path.append("..")
import google.cloud.logging
from callback_logging import log_query_to_model, log_model_response
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.models import Gemini
from google.genai import types
from google.adk.tools import AgentTool
from google.adk.tools import VertexAiSearchTool

RETRY_OPTIONS = types.HttpRetryOptions(initial_delay=1, max_delay=3, attempts=30)

from .tools import get_date

# Add the VertexAiSearchTool import below


load_dotenv()
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

# Create your vertexai_search_tool and update its path below
vertexai_search_tool = VertexAiSearchTool(
    search_engine_id="projects/qwiklabs-gcp-04-ae323bc0e521/locations/global/collections/default_collection/engines/planet-search_1782296469020"
)
vertexai_search_agent = Agent(
    name="vertexai_search_agent",
    model=Gemini(model=os.getenv("MODEL"), retry_options=RETRY_OPTIONS),
    instruction="Use your search tool to look up facts.",
    tools=[vertexai_search_tool]
)


root_agent = Agent(
    # A unique name for the agent.
    name="root_agent",
    # The Large Language Model (LLM) that agent will use.
    model=Gemini(model=os.getenv("MODEL"), retry_options=RETRY_OPTIONS),
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Answer questions using your data store access.",
    # Instructions to set the agent's behavior.
    instruction="You analyze new planet discoveries and engage with the scientific community on them.",
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # Add the tools instructed below
    tools=[
        AgentTool(vertexai_search_agent, skip_summarization=False),
        get_date
    ]

)
