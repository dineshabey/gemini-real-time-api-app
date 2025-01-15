import asyncio
import sounddevice as sd
import numpy as np
import wave
from google import genai
from io import BytesIO

# Initialize the GenAI client
client = genai.Client(api_key="AIzaSyDrEPsbhE52NHAh0NHmeNtjhfyfVSkjZcM", http_options={'api_version': 'v1alpha'})
model_id = "gemini-2.0-flash-exp"

# Configuration for the API
config = {
    "response_modalities": ["TEXT", "AUDIO"],
    "speech_config": {
        "voice_config": {
            "prebuilt_voice_config": {
                "voice_name": "Aoede"
            }
        },
        "language_code": "en-US"
    }
}

# Parameters for recording
sample_rate = 16000  # 16 kHz
duration = 5  # Record duration in seconds


def record_audio():
    """Record audio from the microphone."""
    print("Recording... Speak into the microphone.")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()  # Wait until recording is finished
    print("Recording complete.")
    return audio_data


def save_audio(audio_data, file_name="input.wav"):
    """Save the recorded audio to a file."""
    with wave.open(file_name, "wb") as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())


async def main():
    """Main function for interaction."""
    async with client.aio.live.connect(model=model_id, config=config) as session:
        print("Start speaking... (Press Ctrl+C to stop)")

        while True:
            try:
                # Record and save audio
                audio_data = record_audio()
                save_audio(audio_data)  # Optional: Save the audio for debugging
                
                # Convert the audio data to bytes
                audio_bytes = audio_data.tobytes()
                print("Sending audio to the API...")

                # Send the recorded audio to the API
                await session.send({"audio": {"content": audio_bytes}})

                # Process the response from the API
                async for response in session.receive():
                    if response.text:
                        print(f"AI> {response.text}")
                    if response.audio:
                        print("AI> Received audio response. Playing it...")
                        with wave.open(BytesIO(response.audio)) as wf:
                            data = wf.readframes(wf.getnframes())
                            sd.play(data, samplerate=wf.getframerate())
                            sd.wait()

            except KeyboardInterrupt:
                print("Exiting the application.")
                break
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()  # Allows asyncio.run() in environments like Jupyter
    asyncio.run(main())
