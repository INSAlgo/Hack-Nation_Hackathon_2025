import json
import sys

print(sys.version)

if sys.version.startswith("3.11"):
	import torch
	from TTS.api import TTS as TTS_API
else:
	import io
	import os
	import subprocess
	import tempfile

class TTS:
	def __init__(self):
		# Get device
		device = "cuda" if torch.cuda.is_available() else "cpu"

		# Explicitly set weights_only=False
		old_load = torch.load
		torch.load = lambda *args, **kwargs: old_load(
			*args, **(kwargs | {"weights_only": False})
		)

		# Init TTS
		model = "tts_models/multilingual/multi-dataset/xtts_v2"
		# model = "tts_models/en/ljspeech/vits"
		# model = "tts_models/en/vctk/vits"
		self.tts = TTS_API(model).to(device)

		# speakers = list(self.tts.synthesizer.tts_model.speaker_manager.name_to_id)
		self.speaker = "Dionisio Schuyler"

		print(f"TTS ready, running on {device}")

	def get_transcript(self, text, path):
		self.tts.tts_to_file(
			text=text, file_path=path, speaker=self.speaker, language="en"
		)

def get_speech_remote(text, *_):
	tmp_path = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)

	# Force venv usage
	cmd = [os.path.join(os.path.dirname(__file__), 'venv/Scripts/python.exe'), __file__]
	process = subprocess.run(cmd, input=json.dumps({"text": text, "path": tmp_path.name}), text=True, capture_output=True)
 
	if process.returncode != 0:
		print(process.stderr)
		raise Exception("TTS failed")

	# out = io.BytesIO()
	# tmp_path.seek(0)
	# out.write(tmp_path.read())
	# out.seek(0)
	tmp_path.close()
	# os.remove(tmp_path.name)
	return tmp_path.name


if __name__ == "__main__":
	tts = TTS()

	while True:
		try:
			data = input()
		except EOFError:
			break

		if data == "exit":
			break
		data = json.loads(data)

		tts.get_transcript(data['text'], data.get('path', 'output.wav'))
