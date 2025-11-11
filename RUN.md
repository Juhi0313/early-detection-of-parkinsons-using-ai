# How to Run the Parkinson's Detection App

## Quick Start (3 Steps)

### Step 1: Activate Virtual Environment
```bash
.venv\Scripts\activate
```

### Step 2: Train the Model (First Time Only)
```bash
python train_model.py
```
This will:
- Download the UCI Parkinson's dataset
- Train a Random Forest model
- Save `parkinsons_model.pkl` and `scaler.pkl`

**Note:** You only need to do this once. If the model files already exist, skip this step.

### Step 3: Run the Web Application
```bash
python app.py
```

You should see output like:
```
Model and scaler loaded successfully!
 * Running on http://127.0.0.1:5000
```

### Step 4: Open in Browser
Open your web browser and go to:
```
http://localhost:5000
```

## Using the App

1. **Click "Start Recording"** - Allow microphone access when prompted
2. **Speak for 3-5 seconds** - Speak clearly in a quiet environment
3. **Click "Stop Recording"** - When you're done speaking
4. **Click "Analyze Voice"** - Get your risk assessment

## Troubleshooting

### Model Not Found Error
If you see "Model not loaded", run:
```bash
python train_model.py
```

### Port Already in Use
If port 5000 is busy, edit `app.py` and change:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
to a different port like `port=5001`

### Microphone Not Working
- Check browser permissions (click the lock icon in address bar)
- Try a different browser (Chrome, Firefox, Edge)
- Make sure your microphone is connected and working

## Complete Command Sequence

```bash
# Activate virtual environment
.venv\Scripts\activate

# Train model (first time only)
python train_model.py

# Run the app
python app.py
```

Then open: **http://localhost:5000**

---

**That's it! Enjoy your beautiful AI-powered Parkinson's detection app! 🚀**

