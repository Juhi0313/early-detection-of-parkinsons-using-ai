"""
Audio preprocessing utilities: resample, normalize, trim silence.
"""

import numpy as np
import librosa
import soundfile as sf
import warnings
warnings.filterwarnings('ignore')


def resample_audio(audio, original_sr, target_sr=22050):
    """Resample audio to target sample rate."""
    try:
        if original_sr != target_sr:
            audio = librosa.resample(audio, orig_sr=original_sr, target_sr=target_sr)
        return audio, target_sr
    except:
        return audio, original_sr


def normalize_audio(audio):
    """Normalize audio to [-1, 1] range."""
    try:
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        return audio
    except:
        return audio


def trim_silence(audio, sr, top_db=20):
    """Trim silence from the beginning and end of audio."""
    try:
        audio_trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
        return audio_trimmed
    except:
        return audio


def preprocess_audio(audio, sr, target_sr=22050):
    """
    Complete preprocessing pipeline:
    1. Resample to target sample rate
    2. Normalize
    3. Trim silence
    """
    try:
        # Resample
        audio, sr = resample_audio(audio, sr, target_sr)
        
        # Normalize
        audio = normalize_audio(audio)
        
        # Trim silence
        audio = trim_silence(audio, sr)
        
        # Ensure minimum length (pad if too short)
        min_length = int(target_sr * 0.5)  # 0.5 seconds minimum
        if len(audio) < min_length:
            audio = np.pad(audio, (0, min_length - len(audio)), mode='constant')
        
        return audio, sr
    
    except Exception as e:
        print(f"Error preprocessing audio: {e}")
        return audio, sr


def load_and_preprocess_audio(file_path, target_sr=22050):
    """Load audio file and preprocess it."""
    try:
        audio, sr = librosa.load(file_path, sr=None)
        audio, sr = preprocess_audio(audio, sr, target_sr)
        return audio, sr
    except Exception as e:
        print(f"Error loading audio: {e}")
        return None, None

