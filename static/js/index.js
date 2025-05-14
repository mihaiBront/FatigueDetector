// Function to format runtime seconds into HH:MM:SS
function formatRuntime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

// Function to reset distance tracking on the server
async function resetDistance() {
    try {
        const response = await fetch('/api/reset_distance', {
            method: 'POST'
        });
        const data = await response.json();
        if (data.status === 'ok') {
            console.log('Distance reset successful');
        }
    } catch (error) {
        console.error('Error resetting distance:', error);
    }
}

// Function to fetch OBD data and update display
async function updateOBDData() {
    try {
        const response = await fetch('/api/obd/data');
        const data = await response.json();

        if (data.error) {
            console.error('OBD Error:', data.error);
            return;
        }

        // Calculate display data
        const time = formatRuntime(data.runtime);

        // Update face display
        faceDisplay.updateData({
            time: time,
            speed: data.speed,
            distance: data.accumulated_distance
        });

    } catch (error) {
        console.error('Error fetching OBD data:', error);
    }
}

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Update data every second
    setInterval(updateOBDData, 1000);

    // Initial update
    updateOBDData();
});

//# sourceMappingURL=index.js.map 