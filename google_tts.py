import os
from google.cloud import texttospeech

def speak(text):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name = "en-US-Studio-O",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open("/Users/devaldeliwala/calendar_AI/output.mp3", "wb") as out:
        out.write(response.audio_content)

    os.system("afplay /Users/devaldeliwala/calendar_AI/output.mp3")  




