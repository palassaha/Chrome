const micBtn = document.getElementById('micBtn');
const status = document.getElementById('status');
const countdown = document.getElementById('countdown');
let isRecording = false;
let countdownInterval = null;

async function setupOffscreen() {
    if (await chrome.offscreen.hasDocument()) return;
    await chrome.offscreen.createDocument({
        url: 'offscreen.html',
        reasons: ['USER_MEDIA'],
        justification: 'Recording audio for voice search'
    });
}

micBtn.onclick = async () => {
    await setupOffscreen();
    if (!isRecording) {
        chrome.runtime.sendMessage({ target: 'offscreen', type: 'start-recording' });
        isRecording = true;
        micBtn.classList.add('recording');
        status.innerText = "🎙️ Speak now!";

        // Countdown from 5 to 0
        let timeLeft = 5;
        countdown.innerText = timeLeft;

        countdownInterval = setInterval(() => {
            timeLeft--;
            countdown.innerText = timeLeft;

            if (timeLeft <= 0) {
                clearInterval(countdownInterval);
                countdown.innerText = '';

                // Stop recording
                chrome.runtime.sendMessage({ target: 'offscreen', type: 'stop-recording' });
                isRecording = false;
                micBtn.classList.remove('recording');
                status.innerText = "Processing...";
            }
        }, 1000);

    } else {
        // Manual stop
        if (countdownInterval) {
            clearInterval(countdownInterval);
            countdown.innerText = '';
        }
        chrome.runtime.sendMessage({ target: 'offscreen', type: 'stop-recording' });
        isRecording = false;
        micBtn.classList.remove('recording');
        status.innerText = "Processing...";
    }
};

chrome.runtime.onMessage.addListener(async (message) => {
    if (message.type === 'audio-data') {
        status.innerText = "Processing...";

        try {
            const response = await fetch(message.data);
            const blob = await response.blob();

            const formData = new FormData();
            formData.append('file', blob, 'audio.wav');



            const apiRes = await fetch('http://localhost:8000/process-voice', {
                method: 'POST',
                body: formData
            });
            const data = await apiRes.json();

            if (data.url) {
                chrome.tabs.create({ url: data.url });
                status.innerText = "Opening " + data.platform;
                setTimeout(() => {
                    status.innerText = "Click to speak";
                }, 2000);
            } else {
                status.innerText = "No platform detected.";
                setTimeout(() => {
                    status.innerText = "Click to speak";
                }, 2000);
            }
        } catch (err) {
            console.error(err);
            status.innerText = "API Error.";
            setTimeout(() => {
                status.innerText = "Click to speak";
            }, 2000);
        }
    }
});