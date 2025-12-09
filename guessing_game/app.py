from flask import Flask, render_template, request, jsonify, session, send_from_directory
import torch
from torchvision.utils import save_image
import os
import random
import numpy as np
from PIL import Image, ImageFilter
import uuid 
import shutil 

from Generator import Generator

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Paths
MODEL_PATH = "generator.pth"
REAL_FOLDER = "real_flowers"
TEMP_IMG_FOLDER = "static/temp_images" 
os.makedirs(TEMP_IMG_FOLDER, exist_ok=True)

DISPLAY_SIZE = 400  

def upscale_for_display(img_path):
    """Take a 64x64 image and upscale it nicely for display"""
    img = Image.open(img_path).convert("RGB")
    img = img.resize((DISPLAY_SIZE, DISPLAY_SIZE), Image.LANCZOS)
    img.save(img_path) 

def degrade_real_image(img_path):
    """Make real images look as bad as early 2016 GANs"""
    img = Image.open(img_path).convert("RGB")
    
    img = img.resize((64, 64), Image.BICUBIC)
    
    arr = np.array(img).astype(np.float32)
    noise = np.random.normal(0, 8, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    
    img = img.filter(ImageFilter.GaussianBlur(radius=0.9))
    
    img = img.resize((DISPLAY_SIZE, DISPLAY_SIZE), Image.NEAREST)
    img = img.resize((DISPLAY_SIZE, DISPLAY_SIZE), Image.BICUBIC)
    
    img.save(img_path)


device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Using device: {device}")
gen = Generator(z_dim=100).to(device)
gen.load_state_dict(torch.load(MODEL_PATH, map_location=device))
gen.eval()

def preprocess_image_for_game(img_path):
    img = Image.open(img_path).convert("RGB")
    img = img.resize((64, 64), Image.BICUBIC)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    img.save(img_path) 

def get_real_flower():
    files = [f for f in os.listdir(REAL_FOLDER) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
    choice = random.choice(files)
    original_path = os.path.join(REAL_FOLDER, choice)
    
    unique_name = f"real_{uuid.uuid4().hex[:10]}.jpg"
    temp_path = os.path.join(TEMP_IMG_FOLDER, unique_name)
    shutil.copy(original_path, temp_path)
    
    degrade_real_image(temp_path) 
    return unique_name

def get_fake_flower():
    z = torch.randn(1, 100, 1, 1, device=device)
    with torch.no_grad():
        img_tensor = gen(z)
    
    unique_name = f"fake_{uuid.uuid4().hex[:10]}.jpg"
    temp_path = os.path.join(TEMP_IMG_FOLDER, unique_name)
    save_image(img_tensor, temp_path, normalize=True)
    
    #upscale_for_display(temp_path) 
    return unique_name

def cleanup_temp_images():
    for f in os.listdir(TEMP_IMG_FOLDER):
        os.remove(os.path.join(TEMP_IMG_FOLDER, f))

@app.route('/')
def index():
    session.clear()
    session['round'] = 0
    session['score'] = 0
    session['total_rounds'] = 10
    session['current_is_fake'] = None
    session['current_img'] = None
    return render_template('index.html')

@app.route('/next_round', methods=['GET'])
def next_round():
    if session['round'] >= session['total_rounds']:
        return jsonify({'game_over': True, 'score': session['score'], 'total': session['total_rounds']})
    
    session['round'] += 1
    is_fake = random.choice([True, False])
    session['current_is_fake'] = is_fake
    
    if is_fake:
        img_filename = get_fake_flower()
    else:
        img_filename = get_real_flower()
    
    session['current_img'] = img_filename
    img_url = f"/temp_images/{img_filename}"
    
    return jsonify({'round': session['round'], 'img_url': img_url})

@app.route('/guess', methods=['POST'])
def guess():
    user_guess = request.json.get('guess')
    is_fake = session['current_is_fake']
    correct = (is_fake and user_guess == 'fake') or (not is_fake and user_guess == 'real')
    
    if correct:
        session['score'] += 1
        result = 'Correct!'
    else:
        result = 'Wrong! It was ' + ('FAKE' if is_fake else 'REAL') + '.'
    
    if session['current_img']:
        try:
            os.remove(os.path.join(TEMP_IMG_FOLDER, session['current_img']))
        except:
            pass
        session['current_img'] = None
    
    return jsonify({'result': result, 'correct': correct, 'score': session['score']})

@app.route('/temp_images/<filename>')
def serve_temp_image(filename):
    return send_from_directory(TEMP_IMG_FOLDER, filename)

if __name__ == '__main__':
    cleanup_temp_images()
    app.run(debug=True)