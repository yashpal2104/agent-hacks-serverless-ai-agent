document.addEventListener('DOMContentLoaded', () => {
    // ... (keep all the existing code from the top)

    // --- DOM Elements ---
    // ... (all existing element variables)
    const narratorView = document.getElementById('narrator-view');
    const webcamFeed = document.getElementById('webcam-feed');
    const narratorStatusText = document.querySelector('#narrator-view p'); // Add this line

    // ... (keep all the existing WebSocket and UI event listeners)

    // --- Core Functions ---
    // ... (keep the sendMessage, addLogMessage, and updateUIAgent functions)

    // --- REVISED startNarrator FUNCTION ---
    async function startNarrator() {
        if (narratorInterval) return; // Prevent multiple intervals

        try {
            // Request access to the webcam
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            
            // If successful, update the UI
            webcamFeed.srcObject = stream;
            webcamFeed.classList.remove('error');
            narratorStatusText.textContent = 'AI is watching and narrating...';
            narratorStatusText.style.color = ''; // Reset color
            addLogMessage('Webcam activated. The Narrator is watching.', 'system');

            // Start sending frames to the backend
            narratorInterval = setInterval(() => {
                if (webcamFeed.readyState >= 2) { // Ensure video is ready
                    const canvas = document.createElement('canvas');
                    canvas.width = webcamFeed.videoWidth;
                    canvas.height = webcamFeed.videoHeight;
                    canvas.getContext('2d').drawImage(webcamFeed, 0, 0);
                    const imageData = canvas.toDataURL('image/jpeg', 0.8);
                    socket.emit('narrator_frame', { image_data: imageData });
                }
            }, 5000);

        } catch (err) {
            console.error("Error accessing webcam:", err);
            
            // --- THIS IS THE NEW USER-FRIENDLY ERROR HANDLING ---
            // Display a helpful error message directly in the UI
            webcamFeed.classList.add('error');
            narratorStatusText.textContent = 'Webcam access denied. Please grant camera permission in your browser and refresh the page.';
            narratorStatusText.style.color = '#ff6b6b'; // Make the error text red
            
            // Also log it to the main chat window
            addLogMessage('Error: Could not access webcam. Please grant permission in your browser settings.', 'system-error');
            
            // Stop any further attempts
            stopNarrator();
        }
    }

    function stopNarrator() {
        clearInterval(narratorInterval);
        narratorInterval = null;
        if (webcamFeed.srcObject) {
            webcamFeed.srcObject.getTracks().forEach(track => track.stop());
            webcamFeed.srcObject = null;
        }
    }
});