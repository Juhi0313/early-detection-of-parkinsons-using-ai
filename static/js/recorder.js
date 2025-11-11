/**
 * Audio recorder utility using MediaRecorder - Converts to WAV in browser
 */

class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.audioBlob = null;
        this.mediaStream = null;
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.isRecording = false;
    }

    async startRecording(canvas, onUpdate) {
        try {
            // Get user media
            this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Create AudioContext for visualization
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = this.audioContext.createMediaStreamSource(this.mediaStream);
            
            // Setup analyser for visualization
            this.setupVisualization(source);
            
            // Create MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.mediaStream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;

            // Start visualization
            if (canvas) {
                this.visualize(canvas);
            }

            return true;
        } catch (error) {
            console.error('Error starting recording:', error);
            throw error;
        }
    }

    async stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            return new Promise((resolve) => {
                this.mediaRecorder.onstop = async () => {
                    // Create blob from chunks
                    const originalBlob = new Blob(this.audioChunks, { type: this.mediaRecorder.mimeType || 'audio/webm' });
                    
                    // Convert to WAV using AudioContext
                    try {
                        this.audioBlob = await convertToWAV(originalBlob);
                        console.log('Converted to WAV:', this.audioBlob.size, 'bytes');
                    } catch (error) {
                        console.error('Error converting to WAV:', error);
                        // Fallback to original blob
                        this.audioBlob = originalBlob;
                    }
                    
                    this.isRecording = false;
                    resolve(this.audioBlob);
                };
                
                this.mediaRecorder.stop();
                
                // Stop all tracks
                if (this.mediaStream) {
                    this.mediaStream.getTracks().forEach(track => track.stop());
                }
                
                // Stop visualization
                if (this.audioContext && this.audioContext.state !== 'closed') {
                    this.audioContext.close();
                }
            });
        }
        return null;
    }

    setupVisualization(source) {
        if (!source) return;

        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 256;
        source.connect(this.analyser);

        const bufferLength = this.analyser.frequencyBinCount;
        this.dataArray = new Uint8Array(bufferLength);
    }

    visualize(canvas) {
        if (!canvas || !this.analyser || !this.isRecording) return;

        const ctx = canvas.getContext('2d');
        const WIDTH = canvas.width;
        const HEIGHT = canvas.height;

        const draw = () => {
            if (!this.isRecording) return;

            requestAnimationFrame(draw);

            this.analyser.getByteFrequencyData(this.dataArray);

            // Clear canvas
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
            ctx.fillRect(0, 0, WIDTH, HEIGHT);

            // Draw bars
            const barWidth = (WIDTH / this.dataArray.length) * 2.5;
            let barHeight;
            let x = 0;

            for (let i = 0; i < this.dataArray.length; i++) {
                barHeight = (this.dataArray[i] / 255) * HEIGHT;

                // Create gradient
                const gradient = ctx.createLinearGradient(0, HEIGHT - barHeight, 0, HEIGHT);
                gradient.addColorStop(0, '#4facfe');
                gradient.addColorStop(0.5, '#00f2fe');
                gradient.addColorStop(1, '#f093fb');

                ctx.fillStyle = gradient;
                ctx.fillRect(x, HEIGHT - barHeight, barWidth, barHeight);

                x += barWidth + 1;
            }
        };

        draw();
    }

    getAudioBlob() {
        return this.audioBlob;
    }
}

