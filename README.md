# AI for Early Detection of Parkinson's from Voice

A cutting-edge web application that uses machine learning to detect early signs of Parkinson's disease through voice analysis. The application analyzes acoustic features from voice recordings to provide real-time risk assessment.

##  Features

- **Real-time Voice Recording**: Record voice directly through the browser
- **Advanced Feature Extraction**: Extracts pitch, jitter, shimmer, MFCCs, HNR, and spectral features
- **ML-Powered Prediction**: Uses trained Random Forest model for accurate predictions
- **Beautiful UI**: Stunning gradient background with neon buttons and modern design
- **Live Visualization**: Real-time audio waveform visualization during recording
- **Risk Assessment**: Provides detailed risk scores and probabilities

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser with microphone access

### Installation

1. **Clone or download this repository**

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**

   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Train the model**

   ```bash
   python train_model.py
   ```

   This will:

   - Download the UCI Parkinson's dataset (if available)
   - Train a Random Forest classifier
   - Save the model as `parkinsons_model.pkl` and scaler as `scaler.pkl`

6. **Run the application**

   ```bash
   python app.py
   ```

7. **Open your browser**
   Navigate to `http://localhost:5000`

## Project Structure

```
.
├── app.py                  # Flask web application
├── train_model.py          # Model training script
├── feature_extractor.py    # Feature extraction utilities
├── audio_preprocessor.py   # Audio preprocessing utilities
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css      # Styling with gradients and neon effects
│   └── js/
│       ├── app.js         # Main application logic
│       └── recorder.js    # Audio recording utilities
├── parkinsons_model.pkl   # Trained model (generated after training)
├── scaler.pkl             # Feature scaler (generated after training)
└── README.md              # This file
```

## Features Explained

### Voice Recording

- Click "Start Recording" to begin
- Speak for 3-5 seconds
- Real-time audio visualization
- Click "Stop Recording" when done

### Feature Extraction

The system extracts 35 acoustic features including:

- **Pitch (F0)**: Fundamental frequency
- **Jitter**: Pitch period variation
- **Shimmer**: Amplitude variation
- **HNR**: Harmonics-to-Noise Ratio
- **MFCCs**: Mel-frequency cepstral coefficients (13 features)
- **Spectral Features**: Centroid, rolloff, bandwidth, zero-crossing rate
- **Statistical Features**: Mean, std, variance, skewness, kurtosis

### Prediction

- Uses trained Random Forest classifier
- Provides risk score (0-100%)
- Shows probabilities for both healthy and Parkinson's classes
- Displays clear status message

## Technical Details

### Model

- **Algorithm**: Random Forest Classifier
- **Features**: 35 acoustic features
- **Training Data**: UCI Parkinson's Dataset
- **Preprocessing**: StandardScaler for feature normalization

### Audio Processing

- **Sample Rate**: 22050 Hz (resampled if needed)
- **Preprocessing**: Normalization, silence trimming
- **Libraries**: librosa, soundfile, scipy

### Web Technologies

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Audio API**: Web Audio API, MediaRecorder API

## Datasets

The model is trained on:

- **UCI Parkinson's Dataset**: https://archive.ics.uci.edu/ml/datasets/parkinsons
- **Parkinson's Disease Classification Dataset**: https://archive.ics.uci.edu/dataset/470/parkinson+s+disease+classification

## ⚠️ Important Notes

1. **Medical Disclaimer**: This tool is for research and educational purposes only. It should not be used as a substitute for professional medical diagnosis.

2. **Model Training**: Make sure to train the model before running the application. The app will not work without `parkinsons_model.pkl` and `scaler.pkl` files.

3. **Browser Compatibility**: Requires a modern browser with Web Audio API and MediaRecorder API support (Chrome, Firefox, Edge, Safari).

4. **Microphone Permissions**: The browser will ask for microphone permissions. Please allow access for the app to work.

## Usage Tips

1. **Recording Quality**:

   - Use a quiet environment
   - Speak clearly and at a normal volume
   - Record for at least 3-5 seconds

2. **Best Results**:
   - Use a good quality microphone
   - Minimize background noise
   - Speak naturally

## 🛠️ Troubleshooting

### Model not found

- Run `python train_model.py` first to generate the model files

### Microphone not working

- Check browser permissions
- Ensure microphone is connected and working
- Try a different browser

### Import errors

- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

##  License

This project is created for educational and research purposes.

##  Credits

- UCI Machine Learning Repository for datasets
- librosa for audio processing
- scikit-learn for machine learning

## Future Enhancements

- Multi-language support
- Batch processing of multiple recordings
- Historical tracking of risk scores
- Export results as PDF
- Mobile app version

---

**Built with ❤️ for early detection of Parkinson's disease**
