from base64 import b64encode
from collections import defaultdict
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import wave

cur_path = os.path.dirname(os.path.realpath(__file__))
root = os.path.abspath(os.path.join(cur_path, ".."))
for path in ("Reddit/YARS", "Sound/STT", "Sound/TTS"):
	sys.path.append(os.path.join(root, path))

import scraper  # type: ignore
import STT  # type: ignore
import TTS  # type: ignore


FFMPEG_PATH = r"C:\Users\William\ffmpeg\bin\ffmpeg.exe"


def create_reel():

	# TODO: Img posts with https://www.reddit.com/r/AskReddit/

	download_background_videos()

	posts = find_posts()

	for post in posts:

		if not generate_post(post, check=True):
			try:
				yn = input(f"Create a reel for: {post['title']}? (y/n) ")
			except KeyboardInterrupt:
				print("\nExiting...")
				break
			if yn.lower() == "y":
				generate_post(post)

def find_posts():
	# Get the latest posts from Reddit
	# subreddit_name = "AskReddit"
	subreddit_name = "AITAH"

	for post in scraper.scrape_subreddit_data(subreddit_name):
		if post['selftext'] == '':
			continue
		yield post


def generate_post(post, check=False):
	post_id = b64encode(post["title"].encode()).decode()

	root = os.path.join(cur_path, "reels", post_id)
	if check and not os.path.exists(root):
		return False

	os.makedirs(root, exist_ok=True)

	meta_path = os.path.join(root, "meta.json")
	metadata = json.load(open(meta_path)) if os.path.exists(meta_path) else {}

	if check:
		return check_post(metadata, root)

	print("1. Generating transcript")
	transcript_path, title, text = generate_transcript(post, root)

	print("2. Generating audio")
	audio_path = generate_audio(root, title, text)

	print("3. Generating title preview image")
	title_image_path = generate_title_img(root, post)

	print("4. Generating subtitles")
	subs_type, chunks, length = generate_subtitles(
		root, meta_path, metadata, transcript_path, audio_path
	)

	print("5. Generating video")
	video = create_video(root, length, audio_path, chunks, subs_type)


def check_post(metadata, root):
	if "lengths" not in metadata:
		return False

	length = len(metadata["lengths"])
	seen = set()
	pat = r"output_(\d+)\.mp4"
	for f in os.listdir(root):
		if m := re.match(pat, f):
			seen.add(int(m[1]))

	return all(i in seen for i in range(length))


# Video
def create_video(root, length, audio, chunks, subs_type):

	def format_path(path, rel=False, quotes=None):
		if not quotes:
			quotes = ""
		if rel:
			path = os.path.relpath(path, os.path.abspath(root))

		return quotes + path.replace(os.sep, "/") + quotes

	def filter_vids(file):
		return file.endswith(".mp4")

	video_root = os.path.join(cur_path, "reels/templates")
	random.seed(os.path.basename(root))  # seed for reproducibility
	choosen = random.choice(list(filter(filter_vids, os.listdir(video_root))))
	path = os.path.join(video_root, choosen)

	video_length = get_media_length(path)

	title_audio_path = os.path.join(root, "title.wav")
	title_image_path = os.path.join(root, "title.png")
	title_audio_length = get_media_length(title_audio_path)

	start_time = random.uniform(0, video_length - length)

	offset_time = 0
	out_paths = []
	for i, (length, subs) in enumerate(chunks):
		subs_path = os.path.join(root, f"subs_{i}{subs_type}")

		fn = f"output_{i}.mp4"
		print(f"Generating {fn} ({i + 1}/{len(chunks)})")

		fullaudio_path = os.path.join(root, f"audio_{i}.wav")
		if not os.path.exists(fullaudio_path):
			# Merge title and main audio using ffmpeg
			cmd = [
				FFMPEG_PATH,
				"-y",
				"-i",
				format_path(title_audio_path),
				"-ss",
				str(offset_time),
				"-t",
				str(length - title_audio_length),
				"-i",
				format_path(audio),
				"-filter_complex",
				"[0:a:0][1:a:0]concat=n=2:v=0:a=1[out]",
				"-map",
				"[out]",
				format_path(fullaudio_path),
			]

			try:
				subprocess.run(cmd, check=True, cwd=root)
			except subprocess.CalledProcessError as e:
				print(f"Error while merging audio with ffmpeg: {e}")
				return None

		out_path = os.path.join(root, fn)
		if not os.path.exists(out_path):

			out_paths.append(out_path)

			cmd = [FFMPEG_PATH, "-y"]

			cmd.extend(
				["-ss", str(start_time + offset_time), "-t", str(length)]
			)  # crop video duration
			cmd.extend(
				["-probesize", "100M", "-analyzeduration", "100M"]
			)  # force find the input pixel format
			cmd.extend(["-i", format_path(path)])  # background video

			cmd.extend(["-i", format_path(fullaudio_path)])  # main audio

			cmd.extend(["-i", format_path(title_image_path)])  # title image

			subs_path = (
				format_path(subs_path).replace("/", r"\\").replace(":", r"\:")
			)  # ffmpeg bug: https://superuser.com/questions/1247197/ffmpeg-absolute-path-error
			# subs_path = format_path(subs_path)

			cmd.extend(
				[
					"-filter_complex",
					(
						f"[0:v:0][2:v:0]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(t,0,{title_audio_length})',"
						f"subtitles='{subs_path}',"
						"crop='min(iw,ih*9/16)':ih,format=yuv420p[v]"
					),
				]
			)  # combine overlay, subtitles, and crop into a single filter_complex
			cmd.extend(["-c:s", "copy", "-c:v", "libx264", "-c:a", "aac"])  # codecs
			cmd.extend(["-pix_fmt", "yuv420p"])  # Explicitly set pixel format
			cmd.extend(["-ac", "2"])  # Force stereo audio
			cmd.extend(["-map", "[v]", "-map", "1:a:0"])  # map video and audio streams
			cmd.extend([format_path(out_path)])  # output path

			# cmd = ' '.join(cmd)

			try:
				subprocess.run(
					cmd,
					check=True,
					cwd=root,
					# stdout=subprocess.PIPE,
					# stderr=subprocess.PIPE
				)
			except subprocess.CalledProcessError as e:
				print(f"Error while running ffmpeg: {e}")
				return None

		offset_time += length - title_audio_length


def get_media_length(path):
	try:
		result = subprocess.run(
			[
				"ffprobe",
				"-v",
				"error",
				"-show_entries",
				"format=duration",
				"-of",
				"default=noprint_wrappers=1:nokey=1",
				path,
			],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True,
			check=True,
		)
		video_length = float(result.stdout.strip())
	except subprocess.CalledProcessError as e:
		print(f"Error while running ffprobe: {e.stderr}")
		raise

	return video_length


def download_background_videos():
	template_folder = os.path.join(cur_path, "reels/templates")
	if not os.path.exists(template_folder):
		os.makedirs(template_folder)
	urls_path = os.path.join(template_folder, "urls.txt")
	if not os.path.exists(urls_path):
		raise FileNotFoundError(f"URLs file not found: {urls_path}")

	with open(urls_path, "r") as f:
		urls = f.readlines()

	for line_i, url in enumerate(urls):
		if url.startswith("#"):
			continue

		j = 0
		video_path = os.path.join(template_folder, f"video_{j}.mp4")
		while os.path.exists(video_path):
			j += 1
			video_path = os.path.join(template_folder, f"video_{j}.mp4")

		try:
			download_video(url, video_path)
		except subprocess.CalledProcessError as e:
			pass
		else:
			print(f"Downloaded video: {video_path}")
			with open(urls_path, "w") as f:
				urls[line_i] = f"# {url}"
				f.writelines(urls)


def download_video(url, video_path):
	from yt_dlp import YoutubeDL

	# Download video using yt-dlp
	ydl_opts = {
		"format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
		"outtmpl": video_path,
		"quiet": True,
	}

	with YoutubeDL(ydl_opts) as ydl:
		ydl.download([url])

	return video_path


# Title
def generate_title_img(root, post):

	title_path = os.path.join(root, "title.png")
	template_path = os.path.join(cur_path, "reels/templates", "title_template.html")
	if not os.path.exists(title_path):
		# Convert HTML string to image
		with open(template_path, "r") as f:
			template = f.read()

		data = {
			"subreddit": post["subreddit"],
			"title": post["title"],
			"author": post["author"],
			"upvotes": random.randint(100, 500),
			# 'upvotes': post['upvotes'], # Will seem strange if too many upvotes
			"comments": post["num_comments"],
			"delay": random.randint(1, 8),
		}

		for k, v in data.items():
			template = template.replace("{" + k + "}", str(v))

		# return generate_title_img_imgkit(template, title_path)
		return generate_title_img_selenium(template, title_path)


def generate_title_img_selenium(template, title_path):
	from selenium import webdriver
	from selenium.webdriver.common.by import By
	from selenium.webdriver.chrome.service import Service
	from selenium.webdriver.chrome.options import Options
	from webdriver_manager.chrome import ChromeDriverManager

	options = Options()
	options.add_argument("--headless")
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")

	service = Service(ChromeDriverManager().install())
	driver = webdriver.Chrome(service=service, options=options)

	tmp_path = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
	try:
		tmp_path.write(template.encode())
		tmp_path.close()

		driver.get(
			"file://" + os.path.abspath(tmp_path.name)
		)  # sourcery skip: use-fstring-for-concatenation
		driver.maximize_window()
		element = driver.find_element(
			By.CLASS_NAME, "post-card"
		)  # Adjust the class name to target the desired element
		element.screenshot(title_path)
	finally:
		os.remove(tmp_path.name)

	driver.quit()


def generate_title_img_imgkit(template, title_path):
	import imgkit

	options = {
		"format": "png",
		"width": 1080,
		"height": 1920,
		"quality": 100,
		"encoding": "utf-8",
	}

	config = imgkit.api.Config(
		wkhtmltoimage=os.path.join(cur_path, "wkhtmltox/bin/wkhtmltoimage.exe")
	)

	rtn = imgkit.IMGKit(template, "string", options=options, config=config)
	rtn.to_img(title_path)


# Subtitles
def convert_subs(subs, filetype, **kwargs):
	if filetype == ".srt":
		return convert_subs_srt(subs)

	elif filetype == ".ass":
		return convert_subs_ass(subs, **kwargs)


def convert_subs_srt(subs):
	# generate .srt subtitles, not used
	def format_time(t):
		return time.strftime("%H:%M:%S", time.gmtime(t)) + f",{int((t % 1) * 1000):03d}"

	out = []
	stop = 0
	for i, sub in enumerate(subs):
		out.append(str(i))
		start = sub["start_time"]
		stop = start + sub["duration"]

		out.append(f"{format_time(start)} --> {format_time(stop)}")
		out.append(sub["word"])
		out.append("")

	return stop, "\n".join(out)


def convert_subs_ass(subs, root, length):
	# generate .ass subtitles
	def format_time(t):
		hours = int(max(t, 0) // 3600)
		time_format = "0:%M:%S" if hours == 0 else "%H:%M:%S"
		return f"{time.strftime(time_format, time.gmtime(t))}.{int(t % 1 * 100):02d}"

	template_path = os.path.join(cur_path, "reels/templates", "subs_template.ass")

	with open(template_path, "r") as f:
		template = f.read().splitlines()

	*header, template = template

	chunks = []
	out = []

	title_length = get_media_length(os.path.join(root, "title.wav"))

	# title = open(os.path.join(root, 'title.txt')).read()

	# kwargs = {
	# 	'start': format_time(0),
	# 	'stop': format_time(title_length),
	# 	'text': title
	# }

	# title_sub = str(template) # make a copy
	# for k, v in kwargs.items():
	# 	title_sub = title_sub.replace('{' + k + '}', v)

	group_length = 15

	group = ''
	group_start = None
	group_stop = None
	stop = 0
	cur_start = 0
	for i, sub in enumerate(subs):
		start = sub["start_time"]
		stop = start + sub["duration"]

		if len(sub["word"]) + len(group) < group_length:
			if group_start is None:
				group_start = start

			group += sub["word"].strip() + " "
			group_stop = stop
			continue

		# kwargs = {
		# 	"start": format_time(start - cur_start + (len(chunks) + 1) * title_length),
		# 	"stop": format_time(stop - cur_start + (len(chunks) + 1) * title_length),
		# 	"text": sub["word"],
		# }

		kwargs = {
			"start": format_time(group_start - cur_start + (len(chunks) + 1) * title_length),
			"stop": format_time(group_stop - cur_start + (len(chunks) + 1) * title_length),
			"text": group.strip(),
		}

		line = str(template)  # make a copy
		for k, v in kwargs.items():
			line = line.replace("{" + k + "}", v)

		out.append(line)

		if stop - cur_start >= length - (len(chunks) + 1) * title_length:
			# chunks.append((length, "\n".join(header + out)))
			chunks.append((length, out))
			out = []
			cur_start += length

		group = sub["word"] + " "
		group_start = start
		group_stop = stop

	if group:
		kwargs = {
			"start": format_time(group_start - cur_start + (len(chunks) + 1) * title_length),
			"stop": format_time(group_stop - cur_start + (len(chunks) + 1) * title_length),
			"text": group,
		}

		line = str(template)  # make a copy
		for k, v in kwargs.items():
			line = line.replace("{" + k + "}", v)

		out.append(line)

	# chunks.append((length, "\n".join(header + out)))
	chunks.append((length, out))

	subs_out = []
	for i, (length, chunk) in enumerate(chunks):
		# Add part number
		kwargs = {
			"start": format_time(0),
			"stop": format_time(title_length),
			"text": f"Part {i + 1}/{len(chunks)}",
		}

		line = str(template)  # make a copy
		for k, v in kwargs.items():
			line = line.replace("{" + k + "}", v)

		line = line.replace("MidScreen", "TopScreen")

		subs_out.append((length, '\n'.join(header + [line] + chunk)))

	return subs_out


def generate_subtitles(root, meta_path, metadata, transcript_path, audio_path):
	subs_type = ".ass"
	subs_path = os.path.join(root, "subs_{}" + subs_type)

	vid_length = 60  # TODO

	if "lengths" not in metadata or any(
		not os.path.exists(subs_path.format(i)) for i in range(len(metadata["lengths"]))
	):
		# Convert speech to text (subtitles)
		subs_raw = STT.STT(audio_path, transcript_path)

		def norm_filter(word):
			return "".join(char.lower() for char in word if char.isalnum()).strip()

		with open(transcript_path, "r") as f:
			transcript = f.read().replace('\n', ' ').split(' ')

		i = 0
		last_stop = 0
		subs = []
		for sub in subs_raw:
			if sub["word"] == "<unk>":
				continue
			if sub["word"] == "<eps>":
				continue

			que = []
			while i < len(transcript):
				if transcript[i].strip():
					que.append(transcript[i].strip())

					if norm_filter(transcript[i]) == norm_filter(sub["word"]):
						if len(que) > 1:
							for j, word in enumerate(que[:-1]):
								off = (sub["start_time"]-last_stop) * (j/len(que))
								length = (sub["start_time"]-last_stop) / len(que)
								subs.append(
									{
										"start_time": last_stop + off,
										"duration": length,
										"word": word,
									}
								)

						subs.append(
								{
									"start_time": sub["start_time"],
									"duration": sub["duration"],
									"word": que[-1],
								}
							)

						que = []
						last_stop = sub["start_time"] + sub["duration"]
						break

				i += 1
			i += 1

		while i < len(transcript):
			subs.append(
				{
					"start_time": sub["start_time"],
					"duration": sub["duration"],
					"word": transcript[i].strip(),
				}
			)
			i += 1

		chunks = convert_subs(subs, subs_type, root=root, length=vid_length)

		metadata["lengths"] = []

		for i, (length, subs) in enumerate(chunks):
			with open(subs_path.format(i), "w") as f:
				f.write(subs)

			metadata["lengths"].append(length)

		with open(meta_path, "w") as f:
			json.dump(metadata, f, indent=2)
	else:
		chunks = []
		for i, length in enumerate(metadata["lengths"]):
			subs = open(subs_path.format(i)).read()
			chunks.append((length, subs))
	return subs_type, chunks, length


# Audio
def convert_audio(audio):
	if isinstance(audio, str):
		return audio

	outf = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)

	outf.write(audio.read())
	outf.close()

	return outf.name


def format_audio_text(text):
	# Update the text to be more readable
	text = text.replace("\n", " ")
	text = re.sub(r"\s{2,}", " ", text)  # Remove extra spaces

	def replace_gender(match):
		# Replace '20F' with '20 years old female'
		age = match.group(1)
		sex = match.group(2)
		if not age:
			age = match.group(4)
			sex = match.group(3)
		out = f"{age} years old "
		sex = sex.lower()
		if sex == "f":
			out += "female"
		elif sex == "m":
			out += "male"
		return out

	# text = re.sub(r"(\d{1,2})([FMfm])|([FMfm])(\d{1,2})", replace_gender, text)  # Replace 12F with 12F
	return text


def generate_audio(root, title, main_text):
	files = {title: "title.wav", main_text: "text.wav"}

	for text, fn in files.items():
		audio_path = os.path.join(root, fn)
		if os.path.exists(audio_path):
			continue

		text = format_audio_text(text)

		# Convert text to speech
		# audio = TTS.get_speech_remote(text, 'standard')
		audio = TTS.get_speech_remote(text, "standard")

		if audio is None:
			print("Failed to generate audio")
			raise Exception("Failed to generate audio")

		audio = convert_audio(audio)

		with open(audio_path, "wb") as f:
			with open(audio, "rb") as audio_f:
				f.write(audio_f.read())

		# Delete temp audio file
		try:
			os.remove(audio)
		except PermissionError:
			print(f"Failed to delete temp audio file: {audio}")

	return audio_path


# Transcription
def generate_transcript(post, root):
	transcript_path = os.path.join(root, "transcript.txt")
	title_path = os.path.join(root, "title.txt")

	if not os.path.exists(transcript_path):
		# text = f"{post['title']}\n{post['selftext']}"
		text = post["selftext"]

		with open(transcript_path, "w") as f:
			f.write(text)

	else:
		text = open(transcript_path).read()

	if not os.path.exists(title_path):
		title = post["title"]

		with open(title_path, "w") as f:
			f.write(title)

	else:
		title = open(title_path).read()

	return transcript_path, title, text


if __name__ == "__main__":
	create_reel()
