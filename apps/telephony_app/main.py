# Standard library imports
import os
import sys
from dotenv import load_dotenv

# Third-party imports
from fastapi import FastAPI
from loguru import logger

# Local imports
from .speller_agent import SpellerAgentFactory
from vocode.logging import configure_pretty_logging
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig, PunctuationEndpointingConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager
from vocode.streaming.telephony.server.base import TelephonyServer, TwilioInboundCallConfig
from vocode.streaming.synthesizer.eleven_labs_synthesizer import ElevenLabsSynthesizer

# Load local .env file if available
load_dotenv()
configure_pretty_logging()

app = FastAPI(docs_url=None)
config_manager = RedisConfigManager()
BASE_URL = os.getenv("BASE_URL")

# Launch ngrok locally if no BASE_URL is set
if not BASE_URL:
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        raise ValueError("BASE_URL must be set in Railway environment")

    from pyngrok import ngrok
    ngrok_auth = os.environ.get("NGROK_AUTH_TOKEN")
    if ngrok_auth:
        ngrok.set_auth_token(ngrok_auth)

    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 3000
    BASE_URL = ngrok.connect(port).public_url.replace("https://", "")
    logger.info(f'ngrok tunnel "{BASE_URL}" -> "http://127.0.0.1:{port}"')

if not BASE_URL:
    raise ValueError("BASE_URL is required")

# Setup TelephonyServer with ElevenLabs TTS
telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=config_manager,
    inbound_call_configs=[
        TwilioInboundCallConfig(
            url="/inbound_call",
            agent_config=ChatGPTAgentConfig(
                openai_api_key=os.environ["OPENAI_API_KEY"],
                initial_message=BaseMessage(text="Hey there, how can I help today?"),
                prompt_preamble="You are a helpful and friendly assistant. Keep your responses natural and polite.",
                generate_responses=True,
            ),
            twilio_config=TwilioConfig(
                account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                auth_token=os.environ["TWILIO_AUTH_TOKEN"],
            ),
            transcriber_config=DeepgramTranscriberConfig(
                api_key=os.environ["DEEPGRAM_API_KEY"],
                endpointing_config=PunctuationEndpointingConfig()
            ),
            synthesizer_config=ElevenLabsSynthesizerConfig(
                api_key=os.environ["ELEVEN_LABS_API_KEY"],
                voice_id=os.environ["ELEVEN_LABS_VOICE_ID"],
            )
        )
    ],
    agent_factory=SpellerAgentFactory(),
    synthesizer=ElevenLabsSynthesizer(
        ElevenLabsSynthesizerConfig(
            api_key=os.environ["ELEVEN_LABS_API_KEY"],
            voice_id=os.environ["ELEVEN_LABS_VOICE_ID"]
        )
    )
)

app.include_router(telephony_server.get_router())
