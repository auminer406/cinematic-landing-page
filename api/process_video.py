import os
from flask import Flask, request, jsonify
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Vercel requires the Flask app to be named 'app'
app = Flask(__name__)

# This is the main API route that will be triggered
@app.route('/api/process_video', methods=['POST'])
def handle_processing():
    # --- 1. Securely load Cloudinary credentials from Vercel Environment Variables ---
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not all([cloud_name, api_key, api_secret]):
        return jsonify({"error": "Server configuration error: Cloudinary credentials missing."}), 500

    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret, secure=True)

    # --- 2. Get the uploaded file and user data from the request ---
    # This part will be refined in the next step. We expect the frontend
    # to send a 'public_id' of a video already uploaded to Cloudinary.
    data = request.get_json()
    public_id = data.get('public_id')
    user_email = data.get('email')
    project_name = data.get('project_name')

    if not public_id:
        return jsonify({"error": "No 'public_id' provided in the request."}), 400

    # --- 3. For now, just check if we can get info about the uploaded video ---
    try:
        # This line verifies we can connect to Cloudinary and access the file
        asset_info = cloudinary.api.resource(public_id, resource_type="video")
        
        return jsonify({
            "message": "Success! Connection to Cloudinary established and video found.",
            "received_public_id": public_id,
            "video_original_url": asset_info.get('secure_url'),
            "status": "Ready for Step 2: Transformation"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Could not access video with public_id '{public_id}'. Error: {str(e)}"}), 404


# A simple health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Vercel Python backend is running."})


