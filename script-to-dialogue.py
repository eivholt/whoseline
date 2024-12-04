import os
from pathlib import Path
from openai import OpenAI
from pydub import AudioSegment

API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
AUDIO_MODEL = "gpt-4o-audio-preview"
API_KEY = os.getenv("WHOSELINE_OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Please set the WHOSELINE_OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=API_KEY)

BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RED = '\033[31m'
GREEN = '\033[32m'
END = '\033[0m'

voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# Conversation script
script = [
    {"actor": 4, "line": "Hei, takk for sist"},
    {"actor": 5, "line": "Takk for sist, ja."},
    {"actor": 4, "line": "Ja, i dag er det cøliakikontroll"},
    {"actor": 5, "line": "Ja.."},
    {"actor": 4, "line": "Så, hvordan går det?"},
    {"actor": 5, "line": "Jo, jeg synes det går greit. Det har vært litt mye å sette seg inn i, men det har blitt lettere etter hvert."}
]

# Directory to save temporary audio files
TEMP_DIR = Path(__file__).parent / "temp_audio"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Output file path
OUTPUT_FILE = Path(__file__).parent / "conversation.mp3"

def generate_audio(client, line, voice, file_path):
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=line,
        
    )

    response.with_streaming_response(file_path)

def create_conversation(script):
    """
    Process the script, generate audio for each line, and combine them into a conversation.
    """
    combined_audio = AudioSegment.empty()

    for idx, entry in enumerate(script):
        print(f"Processing line {idx + 1}/{len(script)}: {BOLD}{voices[entry['actor']]}{END} says: \"{GREEN}{entry['line']}{END}\"")
        
        # Temporary file for each line
        temp_file_path = TEMP_DIR / f"line_{idx + 1}.mp3"
        
        # Generate audio for the line
        generate_audio(client, entry["line"], voices[entry['actor']], temp_file_path)
        
        # Load audio and append to combined_audio
        line_audio = AudioSegment.from_file(temp_file_path, format="mp3")
        combined_audio += line_audio

    # Export the combined audio
    combined_audio.export(OUTPUT_FILE, format="mp3")
    print(f"Conversation audio, duration {combined_audio.duration_seconds}s, saved as {OUTPUT_FILE}")

if __name__ == "__main__":
    create_conversation(script)
