"""
Audio format converter that works without FFmpeg
Uses pure Python and existing audio libraries
"""

import os
import numpy as np
import librosa
import soundfile as sf
from scipy.io import wavfile as scipy_wavfile

def convert_webm_to_wav(webm_path):
    """
    Convert WebM to WAV without FFmpeg
    WebM is just Matroska container with Vorbis audio
    """
    try:
        # Try using scipy and librosa which may support it
        audio, sr = librosa.load(webm_path, sr=None)
        wav_path = webm_path.replace('.webm', '.wav')
        sf.write(wav_path, audio, sr)
        return wav_path
    except Exception as e:
        print(f"WebM conversion failed: {e}")
        return None

def convert_to_wav(input_path, output_path=None):
    """
    Convert any audio format to WAV using available libraries
    Returns path to WAV file
    """
    if output_path is None:
        output_path = input_path.rsplit('.', 1)[0] + '.wav'
    
    try:
        # Load with librosa (supports many formats)
        audio, sr = librosa.load(input_path, sr=None)
        # Save as WAV
        sf.write(output_path, audio, sr)
        print(f"✓ Converted to WAV: {output_path}")
        return output_path
    except Exception as e:
        print(f"✗ Conversion failed: {e}")
        return None

def load_audio_safe(file_path, sr=None, duration=None):
    """
    Load audio file using multiple fallback methods
    Returns (audio, sr) tuple
    """
    
    file_size = os.path.getsize(file_path)
    print(f"Loading audio file: {file_path} ({file_size} bytes)")
    
    # Try librosa first
    try:
        print(f"Attempting to load with librosa...")
        audio, sample_rate = librosa.load(file_path, sr=sr, duration=duration)
        print(f"✓ Loaded with librosa ({len(audio)} samples)")
        return audio, sample_rate
    except Exception as e:
        print(f"Librosa failed: {e}")
    
    # Try soundfile
    try:
        print(f"Attempting to load with soundfile...")
        audio, sample_rate = sf.read(file_path)
        
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            print(f"Converting from stereo to mono...")
            audio = np.mean(audio, axis=1)
        
        # Ensure float32
        if audio.dtype != np.float32 and audio.dtype != np.float64:
            audio = audio.astype(np.float32) / (np.iinfo(audio.dtype).max + 1)
        
        print(f"✓ Loaded with soundfile ({len(audio)} samples)")
        return audio, sample_rate
    except Exception as e:
        print(f"Soundfile failed: {e}")
    
    # Try scipy wavfile (for WAV files)
    try:
        print(f"Attempting to load with scipy.wavfile...")
        sample_rate, audio = scipy_wavfile.read(file_path)
        
        # Handle integer audio data
        if audio.dtype in [np.int16, np.int32, np.uint8]:
            # Convert to float and normalize
            max_val = np.iinfo(audio.dtype).max
            audio = audio.astype(np.float32) / max_val
        elif audio.dtype not in [np.float32, np.float64]:
            audio = audio.astype(np.float32)
        
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            print(f"Converting from {audio.shape[1]} channels to mono...")
            audio = np.mean(audio, axis=1)
        
        print(f"✓ Loaded with scipy ({len(audio)} samples)")
        return audio, sample_rate
    except Exception as e:
        print(f"Scipy failed: {e}")
    
    # Last resort: try using numpy to read raw data
    try:
        print(f"Attempting to parse WAV manually...")
        with open(file_path, 'rb') as f:
            # Read WAV header
            riff = f.read(4)
            if riff != b'RIFF':
                raise ValueError("Not a WAV file")
            
            file_size_header = np.frombuffer(f.read(4), dtype=np.uint32)[0]
            wave = f.read(4)
            if wave != b'WAVE':
                raise ValueError("Invalid WAV file")
            
            # Skip to fmt chunk
            num_channels = 1
            sample_rate = 16000
            while True:
                chunk_id = f.read(4)
                if not chunk_id or len(chunk_id) < 4:
                    raise ValueError("Truncated WAV file")
                
                chunk_size = np.frombuffer(f.read(4), dtype=np.uint32)[0]
                
                if chunk_id == b'fmt ':
                    fmt_data = f.read(chunk_size)
                    num_channels = np.frombuffer(fmt_data[2:4], dtype=np.uint16)[0]
                    sample_rate = np.frombuffer(fmt_data[4:8], dtype=np.uint32)[0]
                    print(f"WAV format: {num_channels} channels, {sample_rate} Hz")
                
                elif chunk_id == b'data':
                    audio_data = f.read(chunk_size)
                    # Assume 16-bit PCM
                    audio = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # Convert to mono if needed
                    if num_channels > 1:
                        audio = audio.reshape(-1, num_channels)
                        audio = np.mean(audio, axis=1)
                    
                    print(f"✓ Loaded manually ({len(audio)} samples)")
                    return audio, sample_rate
                else:
                    # Skip unknown chunk
                    f.seek(chunk_size, 1)
    except Exception as e:
        print(f"Manual parsing failed: {e}")
    
    raise Exception(f"Could not load audio from {file_path}. Supported formats: WAV, MP3, FLAC, OGG. File size: {file_size} bytes.")
