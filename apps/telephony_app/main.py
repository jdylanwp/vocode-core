# Standard library imports
import os
import sys
from dotenv import load_dotenv

# Third-party imports
from fastapi import FastAPI
from loguru import logger

# Local application/library specific imports
from .speller_agent import SpellerAgentFactory
from vocode.logging import configure_pretty_logging
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager
from vocode.streaming.telephony.server.base import TelephonyServer, TwilioInboundCallConfig

# Load local .env file if running locally
load_dotenv()
configure_pretty_logging()

app = FastAPI(docs_url=None)
config_manager = RedisConfigManager()

# Get BASE_URL from environment
BASE_URL = os.getenv("BASE_URL")

# ⛔ If BASE_URL not set, either fail (Railway) or launch ngrok (Local)
if not BASE_URL:
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        raise ValueError("BASE_URL must be set in Railway environment")

    # ✅ Only import pyngrok locally
    from pyngrok import ngrok

    ngrok_auth = os.environ.get("NGROK_AUTH_TOKEN")
    if ngrok_auth:
        ngrok.set_auth_token(ngrok_auth)

    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 3000
    BASE_URL = ngrok.connect(port).public_url.replace("https://", "")
    logger.info(f'ngrok tunnel "{BASE_URL}" -> "http://127.0.0.1:{port}"')

# If still missing, fail safely
if not BASE_URL:
    raise ValueError("BASE_URL is required")

# Build the telephony server
telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=config_manager,
    inbound_call_configs=[
        TwilioInboundCallConfig(
            url="/inbound_call",
            agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text="What up"),
                prompt_preamble="Have a pleasant conversation about life",
                generate_responses=True,
            ),
            twilio_config=TwilioConfig(
                account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                auth_token=os.environ["TWILIO_AUTH_TOKEN"],
            ),
        )
    ],
    agent_factory=SpellerAgentFactory(),
)

# Register the API routes
app.include_router(telephony_server.get_router())
