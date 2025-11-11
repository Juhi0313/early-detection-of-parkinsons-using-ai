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


def extract_pitch(audio, sr):
    """Extract fundamental frequency (F0) using autocorrelation."""
    try:
        # Use librosa's pyin for pitch estimation
        f0, voiced_flag, voiced_probs = librosa.pyin(audio, 
                                                     fmin=librosa.note_to_hz('C2'),
                                                     fmax=librosa.note_to_hz('C7'))
        f0 = f0[~np.isnan(f0)]
        if len(f0) == 0:
            return 0.0
        return np.mean(f0)
    except:
        return 0.0


def extract_jitter(audio, sr):
    """Extract jitter (pitch period variation)."""
    try:
        f0, voiced_flag, voiced_probs = librosa.pyin(audio,
                                                     fmin=librosa.note_to_hz('C2'),
                                                     fmax=librosa.note_to_hz('C7'))
        f0 = f0[~np.isnan(f0)]
        if len(f0) < 2:
            return 0.0
        
        # Calculate period variations
        periods = 1.0 / f0
        period_diffs = np.abs(np.diff(periods))
        jitter = np.mean(period_diffs) / np.mean(periods) if np.mean(periods) > 0 else 0.0
        return jitter
    except:
        return 0.0


def extract_shimmer(audio, sr):
    """Extract shimmer (amplitude variation)."""
    try:
        # Find peaks in the audio signal
        peaks, _ = find_peaks(np.abs(audio), distance=int(sr * 0.01))
        if len(peaks) < 2:
            return 0.0
        
        amplitudes = np.abs(audio[peaks])
        amp_diffs = np.abs(np.diff(amplitudes))
        shimmer = np.mean(amp_diffs) / np.mean(amplitudes) if np.mean(amplitudes) > 0 else 0.0
        return shimmer
    except:
        return 0.0


def extract_hnr(audio, sr):
    """Extract Harmonics-to-Noise Ratio."""
    try:
        # Use autocorrelation to estimate HNR
        autocorr = np.correlate(audio, audio, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find the first peak (fundamental period)
        peaks, _ = find_peaks(autocorr[:len(autocorr)//2], distance=int(sr * 0.01))
        if len(peaks) == 0:
            return 0.0
        
        # Estimate harmonic and noise components
        fundamental_period = peaks[0] if peaks[0] > 0 else 1
        harmonic_energy = np.sum(autocorr[fundamental_period::fundamental_period][:10])
        noise_energy = np.sum(autocorr) - harmonic_energy
        
        hnr = 10 * np.log10(harmonic_energy / noise_energy) if noise_energy > 0 else 0.0
        return hnr
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

