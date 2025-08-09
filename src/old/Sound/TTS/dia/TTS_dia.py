import os
import subprocess
import tempfile
import sys

import numpy as np
import torchaudio

model = None

def get_speech(text):  # sourcery skip: assign-if-exp, use-fstring-for-concatenation
	if not sys.version.startswith("3.10.11"):
		# Most likely not running in the right venv
		venv_path = os.path.join(os.path.dirname(__file__), r'.venv\Scripts\python.exe')
		if not os.path.exists(venv_path):
			raise Exception("Venv not found, please run 'python -m venv .venv'")
		cmd = [venv_path, __file__, 'cli']
		process = subprocess.run(cmd, input=text, text=True, capture_output=True)
		if process.returncode != 0:
			print(process.stderr)
			raise Exception("TTS failed")

		return process.stdout.strip()

	global model
	from dia.model import Dia, DEFAULT_SAMPLE_RATE
	import soundfile as sf
	import torch


	if model is None:
		device = "cuda" if torch.cuda.is_available() else "cpu"
		model = Dia.from_pretrained("nari-labs/Dia-1.6B", compute_dtype="float16", device=device)
	
	chunks = []
	buf = ''
	chunk_size = 70
	# for i in range(0, len(text), chunk_size):
	# 	chunk = text[i:i + chunk_size]
	for chunk in text.split('.'):
		if not any(map(lambda c: c.isalpha(), chunk)):
			# Skip empty chunks
			continue

		buf += chunk.strip() + '. '
		if len(buf) > chunk_size:
			chunks.append(buf.strip())
			buf = ''

	if buf:
		chunks.append(buf.strip())

	tmp_output_path = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
	tmp_last_audio_path = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
	last_audio_path = None
	last_chunk_text = None
	output_writer = None
	for i, chunk in enumerate(chunks):

		if last_chunk_text is not None:
			# Reuse last chunk audio
			cur_text = last_chunk_text + ' ' + chunk
			if last_audio_path is None:
				last_audio_path = tmp_last_audio_path.name
		else:
			cur_text = chunk

		last_chunk_text = chunk


		formatted = '[S1] ' + cur_text + ' [S2]'
		output = model.generate(formatted, audio_prompt=last_audio_path, use_torch_compile=True, verbose=True)

		if i < len(chunks) - 1:
			model.save_audio(tmp_last_audio_path.name, output)

		data = np.asarray(output)
		if output_writer is None:
			if data.ndim == 1:
				channels = 1
			else:
				channels = data.shape[1]

			output_writer = sf.SoundFile(tmp_output_path.name, 'w', DEFAULT_SAMPLE_RATE, channels)

		output_writer.write(output)
  
		del output # Clear CUDA memory

		# audio = torch.from_numpy(data)
		# if audio.ndim == 1:  # If mono audio, add a channel dimension
		# 	audio = audio.unsqueeze(0)  # C, T
		# audio = audio.to(model.device).unsqueeze(0)  # 1, C, T
		# audio_data = model.dac_model.preprocess(audio, DEFAULT_SAMPLE_RATE)
		# _, encoded_frame, _, _, _ = model.dac_model.encode(audio_data)  # 1, C, T
		# last_chunk_audio = encoded_frame.squeeze(0).transpose(0, 1)


	if output_writer is not None: # Might happen if no text was passed
		output_writer.close()

	tmp_output_path.close()
	if tmp_last_audio_path is not None:
		tmp_last_audio_path.close()
		os.remove(tmp_last_audio_path.name)

	return tmp_output_path.name

if __name__ == "__main__":
	if len(sys.argv) > 1 and sys.argv[1] == 'cli':
		text = sys.stdin.read()
	else:
		text = """
			It was a quiet evening in the small town of Willow Creek. The sun was setting, casting a golden hue over the rooftops and the cobblestone streets. 
			Sarah, a young journalist, was walking home from the local library, her bag filled with books about the town's history. She had always been fascinated 
			by the legends surrounding the old mansion on the hill, a place the locals called "Ravenwood Manor." 
		""".replace('\n', '').replace('\t', '').strip()

	out = get_speech(text)

	print(out)
	exit(0)