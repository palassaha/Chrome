class RecorderWorklet extends AudioWorkletProcessor {
    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input.length > 0) {
            const channelData = input[0];
            // Send the raw audio samples back to the offscreen script
            this.port.postMessage(channelData);
        }
        return true;
    }
}

registerProcessor('recorder-worklet', RecorderWorklet);