# Quick Start Guide

## 🚀 Fast Setup (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Train the Model

```bash
python train_model.py
```

This will:

- Download the UCI Parkinson's dataset
- Train a Random Forest model
- Save `parkinsons_model.pkl` and `scaler.pkl`

### Step 3: Run the App

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

## 🎤 How to Use

1. **Click "Start Recording"** - Allow microphone access when prompted
2. **Speak for 3-5 seconds** - Speak clearly in a quiet environment
3. **Click "Stop Recording"** - When you're done speaking
4. **Click "Analyze Voice"** - Get your risk assessment

## 📋 Requirements

- Python 3.8+
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Microphone access
- Internet connection (for initial dataset download)

## ⚠️ Troubleshooting

**Model not found?**

- Run `python train_model.py` first

**Microphone not working?**

- Check browser permissions
- Try a different browser

**Import errors?**

- Make sure you installed: `pip install -r requirements.txt`

## 🎨 Features

- ✨ Beautiful gradient UI with neon buttons
- 🎤 Real-time voice recording
- 📊 Live audio visualization
- 🤖 AI-powered risk assessment
- 📈 Detailed probability scores

---

**Ready to detect early signs of Parkinson's! 🚀**
