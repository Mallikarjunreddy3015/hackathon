from transformers import pipeline
import torch
from transformers.pipelines.audio_utils import ffmpeg_microphone_live
import sys
import re
import time
# ----------------------------------------------------------------------
# Wake Word Detection
# ----------------------------------------------------------------------

device = "cuda:0" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if torch.cuda.is_available() else torch.float32

classifier = pipeline(
    "audio-classification",
    model="MIT/ast-finetuned-speech-commands-v2",
    device=device,
    torch_dtype=dtype
)


def launch_fn(
    wake_word="arjun",
    prob_threshold=0.40,
    chunk_length_s=0.75,
    stream_chunk_s=0.25,
    debug=False,
):
    if wake_word not in classifier.model.config.label2id.keys():
        raise ValueError(
            f"Wake word {wake_word} not in set of valid class labels, pick a wake word in the set {classifier.model.config.label2id.keys()}."
        )

    sampling_rate = classifier.feature_extractor.sampling_rate

    mic = ffmpeg_microphone_live(
        sampling_rate=sampling_rate,
        chunk_length_s=chunk_length_s,
        stream_chunk_s=stream_chunk_s,
    )

    print("Listening for wake word...")
    for prediction in classifier(mic):
        prediction = prediction[0]
        if debug:
            print(prediction)
        if prediction["label"] == wake_word:
            if prediction["score"] > prob_threshold:
                return True


# ----------------------------------------------------------------------
# Speech Transcription
# ----------------------------------------------------------------------

transcriber = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny.en",
    device=device,
    torch_dtype=dtype
)


def transcribe(chunk_length_s=3, stream_chunk_s=1):
    sampling_rate = transcriber.feature_extractor.sampling_rate

    mic = ffmpeg_microphone_live(
        sampling_rate=sampling_rate,
        chunk_length_s=chunk_length_s,
        stream_chunk_s=stream_chunk_s,
    )

    print("Start speaking...")
    for item in transcriber(mic, generate_kwargs={"max_new_tokens": 128}):
        sys.stdout.write("\033[K")
        print(item["text"], end="\r")
        if not item["partial"][0]:
            break

    return item["text"]

# ----------------------------------------------------------------------
#  Command Parsing (using Regex)
# ----------------------------------------------------------------------

def parse_command(text):
    text = text.lower().strip()

    # New JS-style regex checks
    if re.search(r"\b(clear|reset|reload|refresh)\b", text):
        return {"command": "reset", "locations": []}

    satellite_match = re.search(r"\bsatellite\b(?:\s*(on|off))?", text)
    if satellite_match:
        status = satellite_match.group(1) if satellite_match.group(1) else "on"
        return {"command": "satellite", "locations": [status]}

    highways_match = re.search(r"\bhighways\b(?:\s*(on|off))?", text)
    if highways_match:
        status = highways_match.group(1) if highways_match.group(1) else "on"
        return {"command": "highways", "locations": [status]}

    route_match = re.search(
        r"\b(?:distance|shortest path|route|navigate|navigation|spath)\b.*?\b(?:from|between)\b\s+([\w\s]+?)\s+(?:to|and)\s+([\w\s]+)",
        text,
    )
    if route_match:
        loc1 = route_match.group(1).strip()
        loc2 = route_match.group(2).strip()
        return {"command": "route", "locations": [loc1, loc2]}

    # Updated zoom regex to include the "zoom" keyword
    zoom_match = re.search(
        r"\b(?:show|go to|open|search|explore|zoom)\b(?:\s+(?:in|at|the|into))?\s+([\w\s]+)", text
    )
    if zoom_match:
        location = zoom_match.group(1).strip()
        return {"command": "zoom", "locations": [location]}

    marker_match = re.search(
        r"\b(?:add\s+marker|marker|mark|pin|ping)\b(?:\s+(?:in|on|to))?\s+([\w\s,]+)", text
    )
    if marker_match:
        locations_text = marker_match.group(1)
        locations = [loc.strip() for loc in re.split(r',|and', locations_text) if loc.strip()]
        return {"command": "marker", "locations": locations}

    # Fallback to the original regex patterns
    patterns = {
        "zoom": r"(?:show|go to|open|search|explore|zoom(?: in| out)?(?: to| on| at)?|display|find|search for|take me to|navigate to|zom(?: in| out)?(?: to| on| at)?|show me(?: the)?|zomm(?: in)?(?: to)?|zoooom|showw|zooom|shw|gt|serch|show meee|zooooom|zo0m|shoooow|zo0m|zom|showw location|zooo00om)(?:\s+the)?\s+(.+)",
        "marker": r"(?:add marker(?: in| on)?|mark(?: on)?|pin|ping|add a mark at|drop pin on|set markr to|place marker in|create marker|mark\s+)(.+)",
        "route": r"(?:get me route|show me route|route|navigate(?: me)?|distance between|what is the shortest path between|show me path between|plan route|directions|find route|gt route betwen|navigae|how to get|best route|shw rout|show rout|plan a trip|route planning|travel route|best way|how to reach|gt directions|find a route|how to go|i want go|navigate to|rout|find shortest route|give me the route|find best route|show rout|get route)(?:\s+(?:from|between))?\s+(.+)",
        "reset": r"(?:clear|reset|reload|refresh|clrscrn|clear all markers|start over|clear the map|reset view|clear markers and routes|back to default|clear all please|reset all|clear everything|clear the map data|clear map view|clearr screen|clear all data on map)",
        "satellite": r"(?:satellite|switch on satellite mode|show me satellite view|turn on satelite|satelite view please|disable satellite|satellite mode off|activate satellite mode|deactivate satellite mode|sat view on|sat view off|turn on satellite image|on satellite|sat on|sat off|satellite view on|turn on the satelite view|turn of the satelite)",
        "highways": r"(?:highways|highways on|highways off|show highways|turn off highways|hide highways|highway display on|enable highways|disable highway view|highway layer on|highway layer off|remove highways|highwayss on|highwas off|highwaysss on please|on highways|highways of now)",
    }

    for command, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            if command == "reset":
                return {"command": "reset", "locations": []}

            # The original satellite and highways logic fallback
            if command == "satellite":
                locations = ["on"] if "on" in text or "activate" in text or ("sat" in text and "view" in text and "on" in text) else ["off"]
                return {"command": "satellite", "locations": locations}

            if command == "highways":
                locations = ["on"] if any(phrase in text for phrase in ["highways on", "show highways", "enable highways", "highway layer on", "highwaysss on", "on highways", "highway display on", "highways on now"]) else ["off"]
                return {"command": "highways", "locations": locations}

            locations_str = match.group(1).strip() if match.groups() else ""
            locations = []
            if command == "route":
                if " to " in locations_str:
                    locations = [loc.strip() for loc in locations_str.split(" to ")]
                elif " and " in locations_str:
                    locations = [loc.strip() for loc in locations_str.split(" and ")]
                elif " between " in locations_str:
                    locations = [loc.strip() for loc in locations_str.split(" between ")]
                elif " from " in locations_str:
                    temp_locations = locations_str.split(" from ")
                    to_locs = []
                    if len(temp_locations) > 1:
                        if " to " in temp_locations[1]:
                            to_locs = [loc.strip() for loc in temp_locations[1].split(" to ")]
                            locations = [loc.strip() for loc in re.split(r',\s*|\s+and\s+', temp_locations[0])]
                            locations.extend(to_locs)
                        else:
                            locations = [loc.strip() for loc in re.split(r',\s*|\s+and\s+', locations_str)]
                    else:
                        locations = [loc.strip() for loc in re.split(r',\s*|\s+and\s+', locations_str)]
                else:
                    locations = [loc.strip() for loc in re.split(r',\s*|\s+and\s+', locations_str)]
            elif command == "marker":
                locations = [loc.strip() for loc in re.split(r',\s*|\s+and\s+', locations_str)]
            else:
                locations = [locations_str]
            return {"command": command, "locations": locations}

    return {"command": "unknown", "locations": []}

# # ----------------------------------------------------------------------
# # Main Voice Assistant Logic
# # ----------------------------------------------------------------------


# def run_voice_assistant():
#     while True:  #  <--  THE KEY CHANGE:  Infinite loop
#         if launch_fn():  # Wait for the wake word
#             start_time=time.time()
#             transcription = transcribe()  # Transcribe the user's command
#             print("time took for transcrible : ", time.time()-start_time, transcription)
#             start_time=time.time()
#             command_data = parse_command(transcription)  # Parse the command

#             print("time took : ", time.time()-start_time, command_data)  # Output the parsed command


# if __name__ == "__main__":
#     run_voice_assistant()