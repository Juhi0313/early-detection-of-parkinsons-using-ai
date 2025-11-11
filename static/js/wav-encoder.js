/**
 * Simple WAV encoder - converts AudioBuffer to WAV Blob
 * Properly encodes PCM audio to WAV format
 */
function encodeWAV(audioBuffer) {
    const numChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const format = 1; // PCM
    const bitDepth = 16;
    
    const bytesPerSample = bitDepth / 8;
    const blockAlign = numChannels * bytesPerSample;
    
    // Convert to mono by averaging channels if stereo
    let monoBuffer;
    if (numChannels > 1) {
        monoBuffer = audioBuffer.getChannelData(0); // Use first channel
    } else {
        monoBuffer = audioBuffer.getChannelData(0);
    }
    
    const length = monoBuffer.length;
    const pcmData = new Float32Array(length);
    
    // Copy and mix down to mono if needed
    if (numChannels > 1) {
        for (let i = 0; i < length; i++) {
            let sample = 0;
            for (let channel = 0; channel < numChannels; channel++) {
                sample += audioBuffer.getChannelData(channel)[i];
            }
            pcmData[i] = sample / numChannels;
        }
    } else {
        for (let i = 0; i < length; i++) {
            pcmData[i] = monoBuffer[i];
        }
    }
    
    // Create WAV file
    const dataLength = length * bytesPerSample;
    const wavSize = 44 + dataLength;
    const arrayBuffer = new ArrayBuffer(wavSize);
    const view = new DataView(arrayBuffer);
    
    // WAV header helper
    const writeString = (offset, string) => {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    };
    
    const writeUint32 = (offset, value, littleEndian = true) => {
        view.setUint32(offset, value, littleEndian);
    };
    
    const writeUint16 = (offset, value, littleEndian = true) => {
        view.setUint16(offset, value, littleEndian);
    };
    
    // Write WAV header
    let offset = 0;
    writeString(offset, 'RIFF'); offset += 4;
    writeUint32(offset, wavSize - 8); offset += 4; // File size - 8
    writeString(offset, 'WAVE'); offset += 4;
    
    // fmt subchunk
    writeString(offset, 'fmt '); offset += 4;
    writeUint32(offset, 16); offset += 4; // Subchunk1Size
    writeUint16(offset, format); offset += 2; // AudioFormat (1 = PCM)
    writeUint16(offset, 1); offset += 2; // NumChannels (mono)
    writeUint32(offset, sampleRate); offset += 4; // SampleRate
    writeUint32(offset, sampleRate * bytesPerSample); offset += 4; // ByteRate
    writeUint16(offset, bytesPerSample); offset += 2; // BlockAlign
    writeUint16(offset, bitDepth); offset += 2; // BitsPerSample
    
    // data subchunk
    writeString(offset, 'data'); offset += 4;
    writeUint32(offset, dataLength); offset += 4; // Subchunk2Size
    
    // Write PCM data
    offset = 44;
    for (let i = 0; i < length; i++) {
        // Convert float (-1.0 to 1.0) to 16-bit PCM
        const s = Math.max(-1, Math.min(1, pcmData[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        offset += 2;
    }
    
    return new Blob([arrayBuffer], { type: 'audio/wav' });
}

/**
 * Convert MediaRecorder blob (webm/ogg) to WAV using AudioContext
 */
async function convertToWAV(blob) {
    const arrayBuffer = await blob.arrayBuffer();
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    return encodeWAV(audioBuffer);
}

