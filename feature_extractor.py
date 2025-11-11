"""
Feature extraction utilities for Parkinson's disease detection from voice.
Extracts acoustic features: pitch, jitter, shimmer, MFCCs, HNR, etc.
"""

import numpy as np
import librosa
import scipy.stats as stats
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')


def _extract_f0_cached(audio, sr):
    """Extract F0 once and cache results for multiple use."""
    try:
        # Use faster method: autocorrelation with Fourier transform
        # Instead of pyin which is very slow
        frame_length = 2048
        hop_length = 512
        
        # Compute short-time autocorrelation
        frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
        f0_values = []
        
        for frame in frames.T:
            # Quick autocorrelation
            autocorr = np.correlate(frame, frame, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            # Find peaks to estimate F0
            try:
                peaks, _ = find_peaks(autocorr[int(sr/400):int(sr/50)], height=0)
                if len(peaks) > 0:
                    # Convert sample lag to frequency
                    f0 = sr / (peaks[0] + int(sr/400))
                    if 50 < f0 < 400:  # Voice range
                        f0_values.append(f0)
            except:
                pass
        
        return np.array(f0_values) if f0_values else np.array([0.0])
    except:
        return np.array([0.0])


def extract_pitch(audio, sr):
    """Extract fundamental frequency (F0) - optimized version."""
    try:
        f0_values = _extract_f0_cached(audio, sr)
        return float(np.mean(f0_values)) if len(f0_values) > 0 else 0.0
    except:
        return 0.0


def extract_jitter(audio, sr):
    """Extract jitter (pitch period variation) - optimized."""
    try:
        f0_values = _extract_f0_cached(audio, sr)
        if len(f0_values) < 2:
            return 0.0
        
        # Calculate period variations
        periods = 1.0 / (f0_values + 1e-8)  # Avoid division by zero
        period_diffs = np.abs(np.diff(periods))
        jitter = np.mean(period_diffs) / (np.mean(periods) + 1e-8)
        return float(jitter)
    except:
        return 0.0


def extract_shimmer(audio, sr):
    """Extract shimmer (amplitude variation) - optimized."""
    try:
        # Use faster peak detection
        # Find peaks with larger minimum distance for speed
        peaks, _ = find_peaks(np.abs(audio), distance=int(sr * 0.005), height=np.max(np.abs(audio)) * 0.1)
        
        if len(peaks) < 2:
            return 0.0
        
        amplitudes = np.abs(audio[peaks])
        amp_diffs = np.abs(np.diff(amplitudes))
        shimmer = np.mean(amp_diffs) / (np.mean(amplitudes) + 1e-8)
        return float(shimmer)
    except:
        return 0.0


def extract_hnr(audio, sr):
    """Extract Harmonics-to-Noise Ratio - simplified fast version."""
    try:
        # Simplified approach: use energy ratio instead of expensive autocorrelation
        frame_length = 1024
        hop_length = 256
        
        frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
        hnr_values = []
        
        for frame in frames.T:
            # Quick FFT-based analysis
            mag = np.abs(np.fft.rfft(frame))
            
            # Find dominant frequency
            if len(mag) > 1:
                peak_idx = np.argmax(mag[:len(mag)//2])
                
                # Estimate harmonic energy (peak and harmonics)
                harmonic_energy = np.sum(mag[peak_idx::peak_idx]) if peak_idx > 0 else np.sum(mag)
                noise_energy = np.sum(mag) - harmonic_energy
                
                if noise_energy > 0:
                    hnr = 10 * np.log10(harmonic_energy / noise_energy)
                    hnr_values.append(hnr)
        
        return float(np.mean(hnr_values)) if hnr_values else 0.0
    except:
        return 0.0


def extract_mfcc_features(audio, sr, n_mfcc=13):
    """Extract MFCC features."""
    try:
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
        return np.mean(mfccs, axis=1).tolist()
    except:
        return [0.0] * n_mfcc


def extract_spectral_features(audio, sr):
    """Extract spectral features."""
    try:
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
        
        return {
            'spectral_centroid_mean': np.mean(spectral_centroids),
            'spectral_centroid_std': np.std(spectral_centroids),
            'spectral_rolloff_mean': np.mean(spectral_rolloff),
            'spectral_rolloff_std': np.std(spectral_rolloff),
            'spectral_bandwidth_mean': np.mean(spectral_bandwidth),
            'spectral_bandwidth_std': np.std(spectral_bandwidth),
            'zero_crossing_rate_mean': np.mean(zero_crossing_rate),
            'zero_crossing_rate_std': np.std(zero_crossing_rate),
        }
    except:
        return {
            'spectral_centroid_mean': 0.0,
            'spectral_centroid_std': 0.0,
            'spectral_rolloff_mean': 0.0,
            'spectral_rolloff_std': 0.0,
            'spectral_bandwidth_mean': 0.0,
            'spectral_bandwidth_std': 0.0,
            'zero_crossing_rate_mean': 0.0,
            'zero_crossing_rate_std': 0.0,
        }


def extract_statistical_features(audio):
    """Extract statistical features from audio signal."""
    try:
        return {
            'mean': np.mean(audio),
            'std': np.std(audio),
            'var': np.var(audio),
            'median': np.median(audio),
            'min': np.min(audio),
            'max': np.max(audio),
            'range': np.max(audio) - np.min(audio),
            'skewness': stats.skew(audio),
            'kurtosis': stats.kurtosis(audio),
        }
    except:
        return {
            'mean': 0.0, 'std': 0.0, 'var': 0.0, 'median': 0.0,
            'min': 0.0, 'max': 0.0, 'range': 0.0, 'skewness': 0.0, 'kurtosis': 0.0
        }


def extract_all_features(audio, sr):
    """
    Extract all features compatible with UCI Parkinson's dataset.
    Returns a feature vector.
    """
    try:
        # Basic acoustic features
        pitch = extract_pitch(audio, sr)
        jitter = extract_jitter(audio, sr)
        shimmer = extract_shimmer(audio, sr)
        hnr = extract_hnr(audio, sr)
        
        # MFCC features
        mfcc_features = extract_mfcc_features(audio, sr, n_mfcc=13)
        
        # Spectral features
        spectral_features = extract_spectral_features(audio, sr)
        
        # Statistical features
        statistical_features = extract_statistical_features(audio)
        
        # Combine all features
        feature_vector = [
            pitch,
            jitter,
            shimmer,
            hnr,
            *mfcc_features,
            spectral_features['spectral_centroid_mean'],
            spectral_features['spectral_centroid_std'],
            spectral_features['spectral_rolloff_mean'],
            spectral_features['spectral_rolloff_std'],
            spectral_features['spectral_bandwidth_mean'],
            spectral_features['spectral_bandwidth_std'],
            spectral_features['zero_crossing_rate_mean'],
            spectral_features['zero_crossing_rate_std'],
            statistical_features['mean'],
            statistical_features['std'],
            statistical_features['var'],
            statistical_features['median'],
            statistical_features['min'],
            statistical_features['max'],
            statistical_features['range'],
            statistical_features['skewness'],
            statistical_features['kurtosis'],
        ]
        
        return np.array(feature_vector)
    
    except Exception as e:
        print(f"Error extracting features: {e}")
        # Return zero vector with same length (34 features)
        return np.zeros(34)

