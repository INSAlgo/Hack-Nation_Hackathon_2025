import json
import subprocess
import tempfile


def STT(audio_path, transcript_path):
	dictionnary = 'english_mfa'
	model = 'english_mfa'
	output_path = tempfile.NamedTemporaryFile(delete=False).name
	
	try:
		subprocess.run(['mfa', 'align_one', audio_path, transcript_path, dictionnary, model, output_path, '--output_format', 'json', '--use_mp'], check=True)

	except subprocess.CalledProcessError as e:
		raise RuntimeError('MFA returned non-zero status: {}'.format(e.stderr))

	with open(output_path, 'r') as f:
		data = json.load(f)
	
	subs = []
	with open(transcript_path, 'r') as f:
		transcript = f.read()

	def filter_format(word):
		return ''.join(char.lower() for char in word if char.isalnum()).strip()

	# words = iter(transcript.split())
	# cur_word = next(words)
	for start, stop, word in data['tiers']['words']['entries']:
		if word == '<eps>':
			# Silence word
			continue

		if word == '<unk>':
			# Unknown word
			# word = cur_word
			continue

		# if filter_format(word) == filter_format(cur_word):
		# 	try:
		# 		cur_word = next(words)
		# 	except StopIteration:
		# 		break


		subs.append({
			'start_time': start,
			'duration': stop-start,
			'word': word
		})

	return subs