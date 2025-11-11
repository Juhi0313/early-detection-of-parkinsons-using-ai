/**
 * Main application logic
 */

const recorder = new AudioRecorder();
let audioBlob = null;

// DOM elements
const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const recordingInfo = document.getElementById('recordingInfo');
const resultsSection = document.getElementById('resultsSection');
const canvas = document.getElementById('canvas');
const riskValue = document.getElementById('riskValue');
const riskBar = document.getElementById('riskBar');
const statusValue = document.getElementById('statusValue');
const healthyProb = document.getElementById('healthyProb');
const parkinsonsProb = document.getElementById('parkinsonsProb');
const messageText = document.getElementById('messageText');
const messageBox = document.getElementById('messageBox');

// Set canvas size
canvas.width = canvas.offsetWidth;
canvas.height = canvas.offsetHeight;

// Event listeners
recordBtn.addEventListener('click', startRecording);
stopBtn.addEventListener('click', stopRecording);
analyzeBtn.addEventListener('click', analyzeAudio);

async function startRecording() {
    try {
        // Reset canvas
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        await recorder.startRecording(canvas);
        
        // Update UI
        recordBtn.disabled = true;
        stopBtn.disabled = false;
        analyzeBtn.disabled = true;
        recordingInfo.textContent = 'Recording... Speak now!';
        recordingInfo.classList.add('recording');
        resultsSection.style.display = 'none';
        audioBlob = null;
    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Error accessing microphone. Please check permissions.');
        recordingInfo.textContent = 'Error: Could not access microphone';
    }
}

async function stopRecording() {
    // Stop recording and get the blob (now async)
    recordingInfo.textContent = 'Processing recording...';
    
    try {
        audioBlob = await recorder.stopRecording();
        
        // Update UI
        recordBtn.disabled = false;
        stopBtn.disabled = true;
        
        if (audioBlob && audioBlob.size > 0) {
            analyzeBtn.disabled = false;
            recordingInfo.textContent = 'Recording stopped. Click "Analyze Voice" to get results.';
        } else {
            analyzeBtn.disabled = true;
            recordingInfo.textContent = 'Recording failed. Please try again.';
        }
        recordingInfo.classList.remove('recording');
    } catch (error) {
        console.error('Error stopping recording:', error);
        recordingInfo.textContent = 'Error processing recording. Please try again.';
        recordBtn.disabled = false;
        stopBtn.disabled = true;
        analyzeBtn.disabled = true;
    }
}

async function analyzeAudio() {
    // Get the blob from recorder if not set
    if (!audioBlob) {
        audioBlob = recorder.getAudioBlob();
    }
    
    if (!audioBlob || audioBlob.size === 0) {
        alert('Please record audio first! Make sure you click "Stop Recording" after speaking.');
        return;
    }

    // Update UI
    analyzeBtn.disabled = true;
    recordingInfo.textContent = 'Analyzing voice... Please wait.';
    
    // Show loading state
    resultsSection.style.display = 'block';
    riskValue.textContent = '...';
    statusValue.textContent = 'Analyzing...';
    healthyProb.textContent = '...';
    parkinsonsProb.textContent = '...';
    messageText.textContent = 'Processing your voice sample...';

    try {
        // Create FormData - now always WAV format
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        // Send to server
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Update results
            displayResults(data);
        } else {
            // Show the actual error message from server
            const errorMsg = data.error || 'Analysis failed';
            throw new Error(errorMsg);
        }
    } catch (error) {
        console.error('Error analyzing audio:', error);
        let errorMessage = error.message || 'An error occurred during analysis.';
        
        // Show more detailed error if available
        if (error.message && error.message.includes('ffmpeg')) {
            errorMessage = 'Audio format conversion failed. Please try recording again or install ffmpeg.';
        } else if (error.message && error.message.includes('too short')) {
            errorMessage = 'Recording is too short. Please record for at least 2-3 seconds.';
        } else if (error.message && error.message.includes('empty')) {
            errorMessage = 'No audio detected. Please check your microphone and try again.';
        }
        
        recordingInfo.textContent = 'Error: ' + errorMessage;
        messageText.textContent = errorMessage;
        messageBox.style.borderColor = '#ff6b6b';
    } finally {
        analyzeBtn.disabled = false;
    }
}

function displayResults(data) {
    // Update risk score
    const riskScore = data.risk_score;
    riskValue.textContent = riskScore + '%';
    riskBar.style.width = riskScore + '%';

    // Update status
    if (data.prediction === 1) {
        statusValue.textContent = 'High Risk';
        statusValue.style.color = '#ff6b6b';
        messageText.textContent = '⚠️ High risk detected. Please consult a healthcare professional.';
        messageBox.style.borderColor = '#ff6b6b';
        messageBox.style.boxShadow = '0 0 20px rgba(255, 107, 107, 0.5)';
    } else {
        statusValue.textContent = 'Low Risk';
        statusValue.style.color = '#4ecdc4';
        messageText.textContent = '✅ Low risk detected. Continue monitoring your health.';
        messageBox.style.borderColor = '#4ecdc4';
        messageBox.style.boxShadow = '0 0 20px rgba(78, 205, 196, 0.5)';
    }

    // Update probabilities
    healthyProb.textContent = data.probability_healthy + '%';
    parkinsonsProb.textContent = data.probability_parkinsons + '%';

    // Animate risk bar
    setTimeout(() => {
        riskBar.style.transition = 'width 1s ease';
    }, 100);

    recordingInfo.textContent = 'Analysis complete!';
}

// Check server health on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        if (!data.model_loaded) {
            recordingInfo.textContent = 'Warning: Model not loaded. Please train the model first.';
            recordingInfo.style.color = '#ff6b6b';
        }
    } catch (error) {
        console.error('Error checking server health:', error);
    }
});

