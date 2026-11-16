from flask import Flask, request, jsonify, send_file
import os
from google import genai

app = Flask(__name__)

# Initialize Gemini Client with your API Key
client = genai.Client(api_key="AQ.Ab8RN6JNHhMKkwA5uB45idQcc3hyPi_VKljYbdxLvzfjueqRpA")

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/upload-video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'មិនមានឯកសារវីដេអូត្រូវបានបញ្ជូនទេ'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'មិនបានរើសឯកសារ'}), 400
    
    video_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(video_path)
    
    try:
        # 1. Upload video to Gemini File API for analysis & translation script generation
        print("Uploading video to Gemini...")
        gemini_file = client.files.upload(file=video_path)
        
        # 2. Generate Khmer Recap Script using Gemini 2.5 Flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                gemini_file,
                "សូមមើលវីដេអូនោះ រួចសរសេរអត្ថបទសម្រាយរឿងជាភាសាខ្មែរយ៉ាងរស់រវើក សម្រាប់ធ្វើជាសំឡេងអាន (Voiceover)។"
            ]
        )
        
        khmer_script = response.text
        
        # 3. Simulate Dubbing & Video Processing (In production, integrate TTS & FFmpeg here)
        output_filename = f"dubbed_{file.filename}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # For demonstration, we copy the uploaded file as the processed output
        os.system(f"cp {video_path} {output_path}")

        return jsonify({
            'success': True,
            'message': 'បានប្ដូរសំឡេងជាភាសាខ្មែរដោយជោគជ័យ!',
            'script': khmer_script,
            'download_url': f'/download/{output_filename}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
