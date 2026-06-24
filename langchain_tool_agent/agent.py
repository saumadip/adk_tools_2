import os
import sys
sys.path.append("..")
import google.cloud.logging
from callback_logging import log_query_to_model, log_model_response

from google.adk import Agent
from google.adk.models import Gemini
from google.genai import types
from google.adk.tools.langchain_tool import LangchainTool # import
from google.adk.agents.callback_context import CallbackContext

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from dotenv import load_dotenv

RETRY_OPTIONS = types.HttpRetryOptions(initial_delay=1, max_delay=3, attempts=30)

load_dotenv()
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

root_agent = Agent(
    name="lanchgain_tool_agent",
    model=Gemini(model=os.getenv("MODEL"), retry_options=RETRY_OPTIONS),
    description="Answers questions using Wikipedia.",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    instruction="""Research the topic suggested by the user.
    Share the information you have found with the user.""",
    # Add the LangChain Wikipedia tool below
    tools = [
    # Use the LangchainTool wrapper...
    LangchainTool(
        # to pass in a LangChain tool.
        # In this case, the WikipediaQueryRun tool,
        # which requires the WikipediaAPIWrapper as
        # part of the tool.
        tool=WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(),
            handle_tool_error=True,
        )
    ),
    ]

)