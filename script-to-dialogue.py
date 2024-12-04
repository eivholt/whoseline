import os
import json
from pathlib import Path
import requests
import base64
from pydub import AudioSegment

API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
AUDIO_MODEL = "gpt-4o-audio-preview"
API_KEY = os.getenv("WHOSELINE_OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Please set the WHOSELINE_OPENAI_API_KEY environment variable.")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RED = '\033[31m'
GREEN = '\033[32m'
END = '\033[0m'

voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# Path to the JSON file containing the dialogue
DIALOG_FILE = Path(__file__).parent / "script.json"

# Directory to save temporary audio files
TEMP_DIR = Path(__file__).parent / "temp_audio"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Output file path
OUTPUT_FILE = Path(__file__).parent / "conversation.mp3"

def load_dialog_from_file(file_path):
    """
    Load dialog from a JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def merge_consecutive_lines(dialog):
    """
    Merge consecutive lines where the same actor speaks multiple times in a row.
    """
    merged_dialog = []
    for entry in dialog:
        if merged_dialog and merged_dialog[-1]["actor"] == entry["actor"]:
            # Merge lines if the actor is the same as the previous one
            merged_dialog[-1]["line"] += f" {entry['line']}"
        else:
            # Add a new entry if the actor changes
            merged_dialog.append(entry)
    return merged_dialog

def generate_audio(line, voice, file_path):
    data = {
        "model": AUDIO_MODEL,
        "modalities": ["text", "audio"],
        "audio": {"voice": voice, "format": "mp3"},
        "messages": [
            {
                "role": "user",
                "content": f"Følgende replikk er en del av en dialog. Les opp replikken på norsk slik at den kan kombineres med resten av dialogen. Ikke les opp noe annet enn følgende:{line}"
            }
        ]
    }

    response = requests.post(API_ENDPOINT, headers=HEADERS, json=data)
    response.raise_for_status()

    audio_data_base64 = response.json()["choices"][0]["message"]["audio"]["data"]

    with open(file_path, 'wb') as f:
        f.write(base64.b64decode(audio_data_base64))

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
        generate_audio(entry["line"], voices[entry['actor']], temp_file_path)
        
        # Load audio and append to combined_audio
        line_audio = AudioSegment.from_file(temp_file_path, format="mp3")
        combined_audio += line_audio

    # Export the combined audio
    combined_audio.export(OUTPUT_FILE, format="mp3")
    print(f"Conversation audio, duration {combined_audio.duration_seconds}s, saved as {OUTPUT_FILE}")

if __name__ == "__main__":
    # Load dialogue from file
    raw_script = load_dialog_from_file(DIALOG_FILE)
    # Merge consecutive lines for the same actor
    script = merge_consecutive_lines(raw_script)
    create_conversation(script)
