/**
 * Audio recorder utility - Records directly to WAV format using Web Audio API
 * This bypasses MediaRecorder issues and ensures quality audio
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
        this.processor = null;
        this.recordingBuffer = [];
        this.sampleRate = 44100;
        this.recordingStartTime = null;
    }

    async startRecording(canvas, onUpdate) {
        try {
            // Get user media
            this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: false,
                    sampleRate: 44100
                }
            });
            
            // Create AudioContext for recording and visualization
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.sampleRate = this.audioContext.sampleRate;
            console.log('AudioContext sample rate:', this.sampleRate);
            
            const source = this.audioContext.createMediaStreamSource(this.mediaStream);
            
            // Setup analyser for visualization
            this.setupVisualization(source);
            
            // Create ScriptProcessor for direct audio capture
            // Use 4096 buffer size for better quality
            const bufferSize = 4096;
            this.processor = this.audioContext.createScriptProcessor(bufferSize, 1, 1);
            
            this.recordingBuffer = [];
            this.recordingStartTime = Date.now();
            
            this.processor.onaudioprocess = (event) => {
                if (!this.isRecording) return;
                
                const inputData = event.inputBuffer.getChannelData(0);
                // Store reference to the data
                this.recordingBuffer.push(new Float32Array(inputData));
            };
            
            // Connect nodes
            source.connect(this.processor);
            this.processor.connect(this.audioContext.destination);
            
            this.isRecording = true;
            console.log('Recording started...');

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
        this.isRecording = false;
        
        if (!this.processor) {
            return null;
        }
        
        return new Promise((resolve) => {
            // Disconnect processor
            this.processor.disconnect();
            
            // Give a small delay to ensure last data is captured
            setTimeout(() => {
                try {
                    // Combine all recording buffers
                    const totalLength = this.recordingBuffer.reduce((acc, buf) => acc + buf.length, 0);
                    console.log('Total recorded samples:', totalLength);
                    console.log('Duration (approx):', (totalLength / this.sampleRate).toFixed(2), 'seconds');
                    
                    if (totalLength === 0) {
                        console.error('No audio data recorded');
                        resolve(null);
                        return;
                    }
                    
                    // Merge all buffers into single array
                    const mergedBuffer = new Float32Array(totalLength);
                    let offset = 0;
                    for (let buffer of this.recordingBuffer) {
                        mergedBuffer.set(buffer, offset);
                        offset += buffer.length;
                    }
                    
                    // Encode to WAV
                    const wavBlob = this.encodeWAVDirect(mergedBuffer, this.sampleRate);
                    console.log('Encoded WAV blob:', wavBlob.size, 'bytes');
                    
                    this.audioBlob = wavBlob;
                    
                    // Stop all tracks
                    if (this.mediaStream) {
                        this.mediaStream.getTracks().forEach(track => track.stop());
                    }
                    
                    // Close audio context
                    if (this.audioContext && this.audioContext.state !== 'closed') {
                        this.audioContext.close();
                    }
                    
                    resolve(wavBlob);
                } catch (error) {
                    console.error('Error stopping recording:', error);
                    resolve(null);
                }
            }, 100);
        });
    }
    
    encodeWAVDirect(floatData, sampleRate) {
        /**
         * Encode raw float32 audio data to WAV format
         * This ensures highest quality - no re-encoding
         */
        const numChannels = 1; // Mono
        const bitDepth = 16;
        const bytesPerSample = bitDepth / 8;
        
        // Calculate sizes
        const dataLength = floatData.length * bytesPerSample;
        const wavSize = 44 + dataLength;
        
        // Create buffer for WAV file
        const arrayBuffer = new ArrayBuffer(wavSize);
        const view = new DataView(arrayBuffer);
        
        // Helper functions
        const writeString = (offset, string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };
        
        // Write RIFF header
        writeString(0, 'RIFF');
        view.setUint32(4, wavSize - 8, true);
        writeString(8, 'WAVE');
        
        // Write fmt subchunk
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true); // Subchunk1Size
        view.setUint16(20, 1, true); // AudioFormat (PCM)
        view.setUint16(22, numChannels, true); // NumChannels
        view.setUint32(24, sampleRate, true); // SampleRate
        view.setUint32(28, sampleRate * numChannels * bytesPerSample, true); // ByteRate
        view.setUint16(32, numChannels * bytesPerSample, true); // BlockAlign
        view.setUint16(34, bitDepth, true); // BitsPerSample
        
        // Write data subchunk
        writeString(36, 'data');
        view.setUint32(40, dataLength, true);
        
        // Write PCM data
        let offset = 44;
        for (let i = 0; i < floatData.length; i++) {
            // Convert float32 (-1.0 to 1.0) to 16-bit PCM
            const sample = Math.max(-1, Math.min(1, floatData[i]));
            view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
            offset += 2;
        }
        
        return new Blob([arrayBuffer], { type: 'audio/wav' });
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

