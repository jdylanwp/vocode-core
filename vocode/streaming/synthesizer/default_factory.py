from typing import Type

from vocode.streaming.models.synthesizer import (
    ElevenLabsSynthesizerConfig,
    SynthesizerConfig,
)
from vocode.streaming.synthesizer.abstract_factory import AbstractSynthesizerFactory
from vocode.streaming.synthesizer.base_synthesizer import BaseSynthesizer
from vocode.streaming.synthesizer.eleven_labs_synthesizer import ElevenLabsSynthesizer
from vocode.streaming.synthesizer.eleven_labs_websocket_synthesizer import ElevenLabsWSSynthesizer


class DefaultSynthesizerFactory(AbstractSynthesizerFactory):
    def create_synthesizer(
        self,
        synthesizer_config: SynthesizerConfig,
    ):
        if isinstance(synthesizer_config, ElevenLabsSynthesizerConfig):
            eleven_labs_synthesizer_class_type: Type[BaseSynthesizer] = ElevenLabsSynthesizer
            if synthesizer_config.experimental_websocket:
                eleven_labs_synthesizer_class_type = ElevenLabsWSSynthesizer
            return eleven_labs_synthesizer_class_type(synthesizer_config)
        else:
            raise Exception("Invalid synthesizer config")
