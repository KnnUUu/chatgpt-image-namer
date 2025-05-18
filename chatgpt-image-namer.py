import os
import base64
import re
from openai import OpenAI
from PIL import Image
import io
from tqdm import tqdm

with open("openai_api_key", "r", encoding="utf-8") as f:
    OPENAI_API_KEY = f.read().strip()
IMAGE_FOLDER = 'D://Pictures//meme//Unnamed'
SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')

client = OpenAI(api_key=OPENAI_API_KEY)

def encode_image_to_base64(image_path, max_size=(800, 800)):
    with Image.open(image_path) as img:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail(max_size)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_image_filename_suggestion(base64_image, original_filename):
    prompt = (
        "You are an assistant for naming meme images. "
        "Your main task is to generate a filename that captures the meme's punchline, joke, or key point—the 'funny part' or 'meme meaning'—regardless of whether it comes from the image's text or the visual itself. "
        "First, analyze the meme and decide where the main joke or punchline comes from: the text, the visual, or both. "
        "Focus the filename on the main source of the meme's humor. "
        "If the filename is already a meaningful English description (words separated by underscores, no more than 10 words, describing the meme's punchline or joke), reply with 'SKIP'. "
        "If not, generate a new filename in English, using up to 6 words separated by underscores, that best summarizes the meme's punchline, joke, or key point. "
        "If you don't understand or cannot recognize, reply with 'SKIP'"
        "Do not include file extension. "
        f"Original filename: {original_filename}"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        max_tokens=50
    )
    suggestion = response.choices[0].message.content.strip()
    return suggestion

def sanitize_filename(name):
    name = re.sub(r'[\/:*?"<>|]', '', name)
    name = name.strip().replace(' ', '_')
    return name

def get_processed_files_from_log(log_path):
    processed = set()
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as log_file:
            for line in log_file:
                if "->" in line:
                    original = line.split("->")[1].strip()
                    processed.add(original)
    return processed

def rename_images_in_folder(folder_path):
    log_path = os.path.join(folder_path, "rename_log.txt")
    processed_files = get_processed_files_from_log(log_path)
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    with open(log_path, "a", encoding="utf-8") as log_file:
        for filename in tqdm(files, desc="Processing images"):
            if filename in processed_files:
                continue
            image_path = os.path.join(folder_path, filename)
            base64_image = encode_image_to_base64(image_path)
            suggestion = get_image_filename_suggestion(base64_image, os.path.splitext(filename)[0])
            if suggestion.upper() == "SKIP":
                continue
            if suggestion:
                base_new_filename = sanitize_filename(suggestion)
                ext = os.path.splitext(filename)[1]
                new_filename = base_new_filename + ext
                new_path = os.path.join(folder_path, new_filename)
                count = 1
                # 检查是否有重名文件，若有则加后缀
                while os.path.exists(new_path):
                    new_filename = f"{base_new_filename}_{count}{ext}"
                    new_path = os.path.join(folder_path, new_filename)
                    count += 1
                os.rename(image_path, new_path)
                print(f"{filename} -> {new_filename}")
                log_file.write(f"{filename} -> {new_filename}\n")

rename_images_in_folder(IMAGE_FOLDER)