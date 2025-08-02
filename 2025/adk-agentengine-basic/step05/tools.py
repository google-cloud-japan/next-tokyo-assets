import io
import logging
import wave

from google import genai
from google.adk.tools import ToolContext
from google.genai import types

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MODEL_GEMINI_2_5_FLASH_PREVIEW_TTS="gemini-2.5-flash-preview-tts"

client = genai.Client()

async def podcast_speaker(script: str, tool_context: "ToolContext") -> dict[str, str]:
    """
    スクリプトに基づいてポッドキャストの音声を生成します。
    Args:
      script: 音声化するスクリプト。
      tool_context: 現在のツール呼び出しのコンテキスト。
    Returns:
      生成された音声への参照を持つディクショナリ。
    """
    response = client.models.generate_content(
        model=MODEL_GEMINI_2_5_FLASH_PREVIEW_TTS,
        contents=f"""明るくハキハキとしたトーンで2人で会話をしてください。
{script}""",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker='Speaker 1',
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name='Puck',
                                ),
                            )
                        ),
                        types.SpeakerVoiceConfig(
                            speaker='Speaker 2',
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name='Zephyr',
                                ),
                            )
                        ),
                    ]
                )
            )
        )
    )

    audio_content = None
    if response and response.candidates:
        candidate = response.candidates[0]
        # candidate.contentが存在するか確認
        if candidate.content and candidate.content.parts:
            part = candidate.content.parts[0]
            # part.inline_dataが存在するか確認
            if part.inline_data:
                audio_content = part.inline_data.data

    if audio_content is None:
        return {
            "status": "failure",
            "detail": "failed to generate podcast audio"
        }

    logger.info(f"Audio length: {len(audio_content)}")

    wav_on_memory = io.BytesIO()
    with wave.open(wav_on_memory, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_content)

    await tool_context.save_artifact(
        filename="podcast.wav",
        artifact=types.Part.from_bytes(data=wav_on_memory.getvalue(), mime_type="audio/wav"),
    )
    return {
        "status": "success",
        "detail": "Audio generated successfully and stored in artifacts.",
        "filename": "podcast.wav",
    }
