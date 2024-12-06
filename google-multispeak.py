"""Synthesizes speech for multiple speakers.
Make sure to be working in a virtual environment.
"""
import os
import json
from pathlib import Path
from google.cloud import texttospeech_v1beta1 as texttospeech

DIALOG_FILE = Path(__file__).parent / "script.json"

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

# Define actor to speaker mapping
actor_to_speaker = {
    2: "U",
    3: "T",
    4: "R",
    5: "S"
}
parent = "projects/iothealthcare-269209/locations/global"
output_gcs_uri = "gs://whoseline-audio/Cøliaki_multispeaker.mp3"

# Instantiates a client
client = texttospeech.TextToSpeechLongAudioSynthesizeClient() #TextToSpeechClient()

# Load dialogue from file
raw_script = load_dialog_from_file(DIALOG_FILE)
# Merge consecutive lines for the same actor
script = merge_consecutive_lines(raw_script)


# Build turns for multi_speaker_markup
turns = [
    texttospeech.MultiSpeakerMarkup.Turn(
        text=entry["line"],
        speaker=actor_to_speaker[entry["actor"]]
    )
    for entry in script[:10]
]

multi_speaker_markup = texttospeech.MultiSpeakerMarkup(turns=turns)

# Set the text input to be synthesized
synthesis_input = texttospeech.SynthesisInput(
    multi_speaker_markup=multi_speaker_markup
)

# Build the voice request, select the language code ('en-US') and the voice
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US", name="en-US-Studio-MultiSpeaker"#language_code="nb-NO", name="en-US-Studio-MultiSpeaker"
)

# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16
)

#Perform the text-to-speech request on the text input with the selected
#voice parameters and audio file type
# response = client.synthesize_speech(
#     input=synthesis_input, voice=voice, audio_config=audio_config
# )

request = texttospeech.SynthesizeLongAudioRequest(
        parent=parent,
        input=synthesis_input,
        audio_config=audio_config,
        voice=voice,
        output_gcs_uri=output_gcs_uri,
    )

operation = client.synthesize_long_audio(request=request)
# Set a deadline for your LRO to finish. 300 seconds is reasonable, but can be adjusted depending on the length of the input.
# If the operation times out, that likely means there was an error. In that case, inspect the error, and try again.
result = operation.result(timeout=300)
print(
    "\nFinished processing, check your GCS bucket to find your audio file! Printing what should be an empty result: ",
    result,
)

# The response's audio_content is binary.
# with open("Cøliaki_multispeaker.mp3", "wb") as out:
#     # Write the response to the output file.
#     out.write(response.audio_content)
#     print('Audio content written to file.')