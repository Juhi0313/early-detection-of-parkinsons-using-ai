"""
Flask web application for Parkinson's disease detection from voice.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import numpy as np
import librosa
import soundfile as sf
import joblib
import os
import base64
import io
from audio_preprocessor import preprocess_audio
from feature_extractor import extract_all_features
from pydub import AudioSegment
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Load model and scaler
model = None
scaler = None

def load_model():
    """Load the trained model and scaler."""
    global model, scaler
    try:
        if os.path.exists('parkinsons_model.pkl') and os.path.exists('scaler.pkl'):
            model = joblib.load('parkinsons_model.pkl')
            scaler = joblib.load('scaler.pkl')
            print("Model and scaler loaded successfully!")
            return True
        else:
            print("Model files not found. Please train the model first.")
            return False
    except Exception as e:
        print(f"Error loading model: {e}")
        return False


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """Handle audio prediction request."""
    temp_path = None
    wav_path = None
    try:
        if model is None or scaler is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Please train the model first.'
            }), 500
        
        # Get audio file from request
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        
        # Get file extension
        filename = audio_file.filename or 'recording.webm'
        file_ext = filename.split('.')[-1].lower() if '.' in filename else 'webm'
        
        # Save temporary audio file with original extension
        temp_path = f'temp_audio.{file_ext}'
        audio_file.save(temp_path)
        
        print(f"Saved audio file: {temp_path}, size: {os.path.getsize(temp_path)} bytes")
        
        # Audio should already be WAV format from browser, but handle other formats if needed
        wav_path = None
        if file_ext not in ['wav', 'wave']:
            try:
                print(f"Converting {file_ext} to WAV format...")
                audio_segment = AudioSegment.from_file(temp_path, format=file_ext)
                wav_path = 'temp_audio_converted.wav'
                audio_segment.export(wav_path, format="wav")
                print(f"Converted to WAV: {wav_path}")
                temp_path = wav_path  # Use converted file
            except Exception as conv_error:
                print(f"Warning: Could not convert audio format: {conv_error}")
                # Try to load original format anyway - librosa might handle it
                pass
        
        # Load and preprocess audio
        try:
            audio, sr = librosa.load(temp_path, sr=None, duration=10.0)
            print(f"Loaded audio: {len(audio)} samples at {sr} Hz")
        except Exception as load_error:
            print(f"Error loading with librosa: {load_error}")
            # Try with soundfile as fallback
            try:
                audio, sr = sf.read(temp_path)
                # Convert to mono if stereo
                if len(audio.shape) > 1:
                    audio = np.mean(audio, axis=1)
                print(f"Loaded audio with soundfile: {len(audio)} samples at {sr} Hz")
            except Exception as sf_error:
                print(f"Error loading with soundfile: {sf_error}")
                raise Exception(f"Could not load audio file. Format: {file_ext}. Please ensure ffmpeg is installed or try recording again.")
        
        # Check if audio is valid
        if len(audio) == 0:
            raise Exception("Audio file is empty or invalid")
        
        # Preprocess audio
        audio, sr = preprocess_audio(audio, sr, target_sr=22050)
        print(f"Preprocessed audio: {len(audio)} samples at {sr} Hz")
        
        # Check minimum length
        if len(audio) < sr * 0.5:  # Less than 0.5 seconds
            raise Exception("Audio recording is too short. Please record for at least 1-2 seconds.")
        
        # Extract features
        features = extract_all_features(audio, sr)
        print(f"Extracted features: {features.shape}")
        
        if len(features) == 0 or np.all(features == 0):
            raise Exception("Could not extract valid features from audio")
        
        features = features.reshape(1, -1)
        
        # Check feature count matches model
        if features.shape[1] != scaler.n_features_in_:
            raise Exception(f"Feature count mismatch: got {features.shape[1]}, expected {scaler.n_features_in_}")
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Predict
        prediction = model.predict(features_scaled)[0]
        probability = model.predict_proba(features_scaled)[0]
        
        # Get risk score (probability of Parkinson's)
        risk_score = probability[1] * 100
        
        # Clean up
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        if wav_path and os.path.exists(wav_path) and wav_path != temp_path:
            try:
                os.remove(wav_path)
            except:
                pass
        
        return jsonify({
            'success': True,
            'prediction': int(prediction),
            'risk_score': round(risk_score, 2),
            'probability_healthy': round(probability[0] * 100, 2),
            'probability_parkinsons': round(probability[1] * 100, 2),
            'message': 'High risk detected' if prediction == 1 else 'Low risk detected'
        })
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error in prediction: {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Clean up on error
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        if 'wav_path' in locals() and wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except:
                pass
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None and scaler is not None
    })


if __name__ == '__main__':
    # Load model on startup
    if not load_model():
        print("Warning: Model not loaded. Please run train_model.py first.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

