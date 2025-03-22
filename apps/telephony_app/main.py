# Standard library imports
import os
import sys
from dotenv import load_dotenv

# Third-party imports
from fastapi import FastAPI
from loguru import logger

# Fixed absolute import
from apps.telephony_app.speller_agent import SpellerAgentFactory

# Vocode SDK imports
from vocode.logging import configure_pretty_logging
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig, PunctuationEndpointingConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager
from vocode.streaming.telephony.server.base import TelephonyServer, TwilioInboundCallConfig
from vocode.streaming.synthesizer.eleven_labs_synthesizer import ElevenLabsSynthesizer

# Load local .env
load_dotenv()
configure_pretty_logging()

# FastAPI app instance
app = FastAPI(docs_url=None)

# Redis config manager
config_manager = RedisConfigManager()

# Set BASE_URL automatically from Railway or pyngrok
BASE_URL = os.getenv("BASE_URL")

if not BASE_URL:
    # Try Railway-generated URL
    if os.environ.get("RAILWAY_STATIC_URL"):
        BASE_URL = os.environ["RAILWAY_STATIC_URL"].replace("https://", "")
        logger.info(f"Using Railway static URL: {BASE_URL}")
    else:
        # Fallback to local development with ngrok
        from pyngrok import ngrok
        ngrok_auth = os.environ.get("NGROK_AUTH_TOKEN")
        if ngrok_auth:
            ngrok.set_auth_token(ngrok_auth)
        port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 3000
        BASE_URL = ngrok.connect(port).public_url.replace("https://", "")
        logger.info(f'ngrok tunnel "{BASE_URL}" -> "http://127.0.0.1:{port}")

if not BASE_URL:
    raise ValueError("BASE_URL is required")

# Telephony server config
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

# Attach routes to app
app.include_router(telephony_server.get_router())

# Optional: for local execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.telephony_app.main:app", host="0.0.0.0", port=3000)
