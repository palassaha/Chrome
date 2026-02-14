chrome.runtime.onMessage.addListener(async (message) => {
    if (message.target !== 'offscreen') return;

    if (message.type === 'start-recording') {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioContext = new AudioContext();

        // Load the worklet file
        await audioContext.audioWorklet.addModule('recorder-worklet.js');

        const source = audioContext.createMediaStreamSource(stream);
        const recorderNode = new AudioWorkletNode(audioContext, 'recorder-worklet');

        const chunks = [];
        recorderNode.port.onmessage = (e) => {
            chunks.push(new Float32Array(e.data));
        };

        source.connect(recorderNode);
        recorderNode.connect(audioContext.destination);

        window.stopRecording = async () => {
            recorderNode.port.onmessage = null;
            recorderNode.disconnect();
            source.disconnect();

            const blob = exportWAV(chunks, audioContext.sampleRate);
            const reader = new FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = () => {
                chrome.runtime.sendMessage({ type: 'audio-data', data: reader.result });
            };

            stream.getTracks().forEach(t => t.stop());
            await audioContext.close();
        };

    } else if (message.type === 'stop-recording') {
        if (window.stopRecording) window.stopRecording();
    }
});

// The exportWAV function remains the same as before
function exportWAV(chunks, sampleRate) {
    const totalLength = chunks.reduce((acc, curr) => acc + curr.length, 0);
    const flatChunks = new Float32Array(totalLength);
    let offset = 0;
    for (const chunk of chunks) {
        flatChunks.set(chunk, offset);
        offset += chunk.length;
    }

    const buffer = new ArrayBuffer(44 + flatChunks.length * 2);
    const view = new DataView(buffer);

    const writeString = (view, offset, string) => {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    };

    writeString(view, 0, 'RIFF');
    view.setUint32(4, 32 + flatChunks.length * 2, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(view, 36, 'data');
    view.setUint32(40, flatChunks.length * 2, true);

    let index = 44;
    for (let i = 0; i < flatChunks.length; i++) {
        let sample = Math.max(-1, Math.min(1, flatChunks[i]));
        view.setInt16(index, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
        index += 2;
    }
    return new Blob([view], { type: 'audio/wav' });
}