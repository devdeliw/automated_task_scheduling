import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from google.cloud import speech
import io, os, subprocess

os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

def record(filename = 'output.wav', duration = 5, freq = 44100): 

    # record audio
    print('Recording...')
    recording = sd.rec(int(duration * freq), 
                       samplerate = freq, channels = 1
    )

    sd.wait()
    # store audio into 'output.wav'
    wav.write(filename, freq, recording)

def convert_audio(input_file = 'output.wav', output_file = 'output_16bit.wav'):

    # convert 'outpout.wav' into the necessary 16-bit PCM that google's LINEAR16
    # encoding mechanism requires. stores output as 'output_16bit.wav'
    command = [
        'ffmpeg',
        '-y',
        '-i', input_file,
        '-acodec', 'pcm_s16le',  # 16-bit PCM
        '-ar', '44100',          # sample rate
        '-ac', '1',              # # of audio channels
        output_file
    ]
    
    try:
        subprocess.run(command, check = True)
        print(f"Conversion successful: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
    except FileNotFoundError:
        print("ffmpeg is not installed or not found in the system path.")

def transcribe_speech(audio_file = 'output_16bit.wav'):

    # transcribe, code taken directly from API documentation
    client = speech.SpeechClient()

    with io.open(audio_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz = 44100,
        language_code = "en-US",
    )

    response = client.recognize(config=config, audio=audio)

    if not response.results:
        print("No transcription results.")
        return

    transcripts = []
    full_transcript = ""
    for result in response.results:
        best_alternative = result.alternatives[0]
        full_transcript += best_alternative.transcript + " "
        transcript = f"transcript: {best_alternative.transcript}"
        language_code = f"language_code:    {result.language_code}"
        confidence = f"confidence:    {best_alternative.confidence:.0%}"

        language_padding = len(transcript) - len(language_code)
        confidence_padding = len(transcript) - len(confidence)

        print("-" * len(transcript) + ' +')
        print(f"{language_code}" + ' ' * language_padding + ' +')
        print(f"{transcript}"  + ' +')
        print(f"{confidence}" + ' ' * confidence_padding + ' +')
        print("-" * len(transcript) + ' +')

    transcripts.append([full_transcript, int(round(response.results[0].alternatives[0].confidence * 100, 0))])

    return transcripts

def run(duration = 5): 
    # script to run whole process
    record(duration = duration)
    convert_audio()
    transcripts = transcribe_speech()

    return transcripts

if __name__ == "__main__": 
    run()
