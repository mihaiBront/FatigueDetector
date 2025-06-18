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

// Function to map fatigue level to status text
function mapFatigueToStatus(fatigueLevel) {
    console.log('Mapping fatigue level:', fatigueLevel, 'Type:', typeof fatigueLevel);
    
    // Handle both numeric and string inputs
    const level = typeof fatigueLevel === 'string' ? parseInt(fatigueLevel) : fatigueLevel;
    
    if (level === null || level === undefined || isNaN(level)) return "Unknown";
    if (level === 0) return "Not Tired";
    if (level === 1) return "Tired";
    if (level === 2) return "Heavily Tired";
    return "Unknown";
}

// Function to update face based on fatigue status and triggers
function updateFaceState(data) {
    const fatigueStatus = mapFatigueToStatus(data.fatigue_level);
    const triggers = data.worried_triggers;

    // Set worried state if any trigger is exceeded
    if (triggers && (
        triggers.speed_exceeded ||
        triggers.distance_exceeded ||
        triggers.time_exceeded ||
        triggers.fatigue_exceeded
    )) {
        faceDisplay.setWorried(true);
    } else {
        faceDisplay.setNormal();
    }
}

// Initialize UI components
let faceDisplay;
let dataPanel;
let fatigueDetection;

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

        // Update data panel (face state is handled inside DataPanel)
        dataPanel.updateData({
            time: time,
            speed: data.speed,
            distance: data.accumulated_distance,
            fatigue: mapFatigueToStatus(data.fatigue_level),
            persistent_fatigue_active: data.persistent_fatigue_active,
            fatigue_counter: data.fatigue_counter
        });

    } catch (error) {
        console.error('Error fetching OBD data:', error);
    }
}

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    faceDisplay = new FaceDisplay('face-container');
    dataPanel = new DataPanel('data-container', faceDisplay);
    fatigueDetection = new FatigueDetection();

    // Update data every second
    setInterval(updateOBDData, 1000);

    // Initial update
    updateOBDData();
});

//# sourceMappingURL=index.js.map 