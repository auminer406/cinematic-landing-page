import os
from flask import Flask, request, jsonify
import cloudinary
import cloudinary.api

# Vercel requires the Flask app to be named 'app'
app = Flask(__name__)

# --- Helper function to generate the HTML/CSS embed code ---
def generate_embed_code(mp4_url, webm_url, poster_url):
    css_code = """
<style>
  .cinematic-video-container { position: relative; width: 100%; height: 100vh; overflow: hidden; }
  .cinematic-video-container video { position: absolute; top: 50%; left: 50%; width: 100%; height: 100%; object-fit: cover; transform: translate(-50%, -50%); z-index: -1; }
</style>
"""
    html_code = f"""
<div class="cinematic-video-container">
  <video playsinline autoplay muted loop poster="{poster_url}">
    <source src="{webm_url}" type="video/webm">
    <source src="{mp4_url}" type="video/mp4">
    Your browser does not support the video tag.
  </video>
</div>
"""
    return f"{css_code}\n{html_code}"

# --- Main API Route ---
@app.route('/api/process_video', methods=['POST'])
def handle_processing():
    try:
        cloudinary.config(
            cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key = os.getenv("CLOUDINARY_API_KEY"),
            api_secret = os.getenv("CLOUDINARY_API_SECRET"),
            secure=True
        )
    except Exception as e:
        return jsonify({"error": "Server configuration error: Could not initialize Cloudinary."}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request: No JSON body provided."}), 400
        
    public_id = data.get('public_id')
    if not public_id:
        return jsonify({"error": "Request body must include the 'public_id' of the uploaded video."}), 400

    try:
        # Optimized MP4 URL
        mp4_url = cloudinary.CloudinaryVideo(public_id).build_url(
            transformation=[{'fetch_format': 'mp4', 'video_codec': 'auto', 'quality': 'auto:good'}]
        )
        # Optimized WebM URL
        webm_url = cloudinary.CloudinaryVideo(public_id).build_url(
            transformation=[{'fetch_format': 'webm', 'video_codec': 'auto', 'quality': 'auto:good'}]
        )
        # Poster Image URL
        poster_url = cloudinary.CloudinaryVideo(public_id).build_url(
            transformation=[{'fetch_format': 'jpg', 'quality': 'auto'}]
        )

        embed_code = generate_embed_code(mp4_url, webm_url, poster_url)

        return jsonify({
            "message": "Video processed successfully!",
            "assets": {
                "optimized_mp4_url": mp4_url,
                "optimized_webm_url": webm_url,
                "poster_image_url": poster_url
            },
            "embed_code": embed_code
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred during video processing: {str(e)}"}), 500

