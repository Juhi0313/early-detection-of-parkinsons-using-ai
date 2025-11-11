# How to Run the Parkinson's Detection App

## Step-by-Step Instructions

### Step 1: Activate Virtual Environment
Open your terminal/command prompt in the project folder and run:

```bash
.venv\Scripts\activate
```

You should see `(.venv)` in your prompt.

### Step 2: Train the Model (First Time Only)
Before running the app, you need to train the model:

```bash
python train_model.py
```

This will:
- Download the UCI Parkinson's dataset
- Train a Random Forest classifier
- Save `parkinsons_model.pkl` and `scaler.pkl` files

**Note:** This step only needs to be done once. After training, you can skip this step.

### Step 3: Run the Web Application
Start the Flask server:

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

or

```
http://127.0.0.1:5000
```

### Step 5: Use the App
1. Click **"Start Recording"** button
2. Allow microphone access when prompted
3. Speak for 3-5 seconds
4. Click **"Stop Recording"**
5. Click **"Analyze Voice"** to get results

## Quick Commands Summary

```bash
# Activate virtual environment
.venv\Scripts\activate

# Train model (first time only)
python train_model.py

# Run the app
python app.py
```

## Troubleshooting

**If you see "Model not loaded" error:**
- Make sure you ran `python train_model.py` first
- Check that `parkinsons_model.pkl` and `scaler.pkl` exist in the project folder

**If dependencies are missing:**
```bash
pip install -r requirements.txt
```

**If port 5000 is already in use:**
- Close other applications using port 5000, or
- Edit `app.py` and change `port=5000` to a different port

## That's it! 🎉

Your app should now be running and ready to analyze voice recordings!

