import os
import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Running on {device}")

# Explicitly set weights_only=False
old_load = torch.load
torch.load = lambda *args, **kwargs: old_load(
    *args, **(kwargs | {"weights_only": False})
)

# Init TTS
model = "tts_models/multilingual/multi-dataset/xtts_v2"
# model = "tts_models/en/ljspeech/vits"
# model = "tts_models/en/vctk/vits"
tts = TTS(model)
tts.synthesizer.tts_model.to(device)

speakers = list(tts.synthesizer.tts_model.speaker_manager.name_to_id)

# Run TTS
# ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# Text to speech list of amplitude values as output
# wav = tts.tts(text="Hello world!", language="en", speaker=speakers[0])
# Text to speech to a file

long_text = """
    It was a quiet evening in the small town of Willow Creek. The sun was setting, casting a golden hue over the rooftops and the cobblestone streets. 
    Sarah, a young journalist, was walking home from the local library, her bag filled with books about the town's history. She had always been fascinated 
    by the legends surrounding the old mansion on the hill, a place the locals called "Ravenwood Manor." 

    As she passed by the town square, she noticed an elderly man sitting on a bench, feeding the pigeons. He looked up and smiled at her, his eyes twinkling 
    with a mix of wisdom and mischief. "Curious about Ravenwood, aren't you?" he asked, as if reading her mind. Sarah stopped in her tracks, surprised. 
    "How did you know?" she asked. The man chuckled. "Everyone who digs into the town's history eventually finds their way to that place. It's as if the manor 
    calls to them."

    Intrigued, Sarah sat down beside him. The man introduced himself as Mr. Whitaker, a retired historian who had spent decades researching the manor's past. 
    He told her stories of its former inhabitants, a wealthy family that mysteriously vanished one stormy night over a century ago. Some said the house was 
    cursed, while others believed it was haunted by the spirits of those who had lived there.

    That night, Sarah couldn't sleep. The stories Mr. Whitaker had shared played over and over in her mind. She decided she had to see the manor for herself. 
    The next morning, armed with her camera and notebook, she made her way up the hill. The path was overgrown with weeds, and the air grew colder as she 
    approached the towering gates of Ravenwood Manor.

    The mansion was even more imposing up close. Its windows were shattered, and ivy crept up its stone walls. Pushing open the creaky gate, Sarah stepped 
    onto the property. The air was thick with an eerie silence, broken only by the rustling of leaves in the wind. As she explored the grounds, she felt as 
    though she was being watched. Shadows seemed to move in the corners of her vision, but when she turned to look, there was nothing there.

    Inside the manor, the air was damp and musty. The grand staircase was covered in dust, and cobwebs hung from the chandeliers. Sarah's footsteps echoed 
    through the empty halls as she made her way from room to room, documenting everything she saw. In the library, she found a journal belonging to one of 
    the mansion's former residents. Its pages were filled with cryptic entries about strange occurrences and unexplainable phenomena.

    As the day turned to evening, Sarah realized she had lost track of time. The sun was setting, and the manor grew darker with each passing minute. Just 
    as she was about to leave, she heard a faint whisper. "Help us," it said. Her heart raced as she turned around, but no one was there. Gathering her 
    courage, she followed the sound to a hidden door behind a bookshelf. It led to a secret room filled with old photographs, letters, and artifacts.

    Among the items was a locket with a picture of a young woman who bore a striking resemblance to Sarah. She felt a chill run down her spine. Could it be 
    a coincidence, or was there a deeper connection between her and the manor's history? Determined to uncover the truth, Sarah vowed to return and continue 
    her investigation.

    Little did she know, her discovery would set off a chain of events that would change her life—and the fate of Willow Creek—forever.
"""

output_dir = os.path.abspath("output")
os.makedirs(output_dir, exist_ok=True)

for speaker in speakers:
    fp = os.path.join(output_dir, f"{speaker}.wav")

    tts.tts_to_file(
        text=long_text, file_path=fp, speaker=speaker, language="en"
    )
    break