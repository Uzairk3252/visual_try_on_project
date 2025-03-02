import os
import random
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import cv2
from pose_detection import detect_pose
from viton_warping import warp_clothing

app = Flask(__name__, static_folder='static')
app.secret_key = "your_secret_key"  # Change this to a secure key

# Dataset Paths
DATASET_PATH = "static/dataset"
UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/output"
MENS_PATH = os.path.join(DATASET_PATH, "mens")
WOMENS_PATH = os.path.join(DATASET_PATH, "womens")

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# ---------------------- USER AUTHENTICATION ROUTES ----------------------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Dummy authentication (Replace with DB logic)
        if username == "admin" and password == "password":
            session['user'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid Credentials"
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Save user to database logic
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# ---------------------- PASSWORD RESET ROUTES ----------------------

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # Implement password reset logic
        return redirect(url_for('reset_password'))
    
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        # Update password logic
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')

# ---------------------- CLOTHING SELECTION ROUTES ----------------------

@app.route('/get_clothes')
def get_clothes():
    category = request.args.get("category", "mens")  # Default to mens
    if category == "mens":
        path = MENS_PATH
    else:
        path = WOMENS_PATH

    if not os.path.exists(path):
        return jsonify({"error": "Category not found"}), 404

    clothes = [f for f in os.listdir(path) if f.endswith('.jpg') or f.endswith('.png')]
    return jsonify({"clothes": clothes})  # Return all clothes (not just 5)

# ---------------------- TRY-ON FUNCTIONALITY ROUTES ----------------------

@app.route('/mens')
def mens():
    return render_template('mens.html', get_clothes=get_clothes)

@app.route('/womens')
def womens():
    return render_template('womens.html', womens_clothes=womens_clothes)

@app.route('/kids')
def kids():
    return render_template('kids.html', kids_clothes=kids_clothes)

@app.route('/tryon')
def tryon():
    image_file = request.args.get('image')
    category = request.args.get('category')
    return render_template('tryon.html', image_file=image_file, category=category)

@app.route('/upload', methods=['POST'])
def upload():
    """Upload user image for virtual try-on."""
    if 'image' not in request.files:
        return "No file uploaded", 400

    file = request.files['image']
    if file.filename == '':
        return "No file selected", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    return redirect(url_for('result', filename=file.filename))

@app.route('/result/<filename>')
def result(filename):
    """Display the result of the try-on."""
    return render_template('result.html', filename=filename)

@app.route('/apply_tryon', methods=['POST'])
def apply_tryon():
    """Apply selected clothing onto the human using pose detection."""
    data = request.get_json()
    clothing_path = data.get("clothing")

    if not clothing_path:
        return jsonify({"success": False, "error": "No clothing selected"})

    user_image_path = os.path.join(UPLOAD_FOLDER, "user_image.jpg")  # Last uploaded image
    clothing_image = cv2.imread(clothing_path)
    frame = cv2.imread(user_image_path)

    user_pose = detect_pose(frame)
    if not user_pose:
        return jsonify({"success": False, "error": "Pose not detected"})

    warped_cloth = warp_clothing(clothing_image, user_pose)
    output_path = os.path.join(RESULT_FOLDER, "tryon_result.jpg")
    cv2.imwrite(output_path, warped_cloth)

    return jsonify({"success": True, "result": "tryon_result.jpg"})

# ---------------------- RUN FLASK APP ----------------------

if __name__ == '__main__':
    app.run(debug=True)
