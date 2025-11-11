# Troubleshooting Guide

## Audio Analysis Error

If you're seeing "Error: Analysis failed", here are the most common causes and solutions:

### 1. Audio Format Issue (Most Common)
**Problem:** Browser records in WebM format, but conversion fails.

**Solution:** 
- Install ffmpeg (required for pydub to convert audio formats)
- Windows: Download from https://ffmpeg.org/download.html
- Or try recording again - sometimes it works on retry

### 2. Recording Too Short
**Problem:** Audio recording is less than 1 second.

**Solution:** 
- Record for at least 2-3 seconds
- Speak clearly and continuously

### 3. No Audio Detected
**Problem:** Microphone not working or no sound captured.

**Solution:**
- Check microphone permissions in browser
- Test microphone in another app
- Try a different browser (Chrome, Firefox, Edge)
- Make sure microphone is not muted

### 4. Model Not Loaded
**Problem:** Model files missing.

**Solution:**
```bash
python train_model.py
```

### 5. Feature Extraction Failed
**Problem:** Could not extract features from audio.

**Solution:**
- Ensure audio has actual voice content (not just silence)
- Record in a quiet environment
- Speak at normal volume

## Check Server Logs

The Flask server prints detailed error messages. Check the terminal where you ran `python app.py` to see the exact error.

## Quick Fixes

1. **Restart the server:**
   ```bash
   # Stop the server (Ctrl+C)
   python app.py
   ```

2. **Clear browser cache and try again**

3. **Try a different browser**

4. **Check browser console (F12) for JavaScript errors**

## Still Not Working?

Check the terminal output for detailed error messages. The server logs will show exactly what went wrong.

