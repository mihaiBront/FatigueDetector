// Get DOM elements
const speedInput = document.getElementById('speed');
const distanceInput = document.getElementById('distance');
const timeInput = document.getElementById('time');
const fatigueInput = document.getElementById('fatigue');
const saveButton = document.getElementById('save');
const resetButton = document.getElementById('reset');
const statusMessage = document.getElementById('status-message');
const adjustButtons = document.querySelectorAll('.adjust-btn');

// Default configuration
const defaultConfig = {
    speed_threshold: 120,
    distance_threshold: 200,
    time_threshold: 7200,
    fatigue_threshold: 2
};

// Current configuration
let currentConfig = { ...defaultConfig };

// Input constraints (matching HTML attributes)
const constraints = {
    speed: { min: 30, max: 160, step: 5 },
    distance: { min: 30, max: 1000, step: 10 },
    time: { min: 0.5, max: 12, step: 0.5 },
    fatigue: { min: 0, max: 2, step: 1 }
};

// Adjust input value
function adjustValue(input, step) {
    const id = input.id;
    const constraint = constraints[id];
    let value = id === 'time' ? parseFloat(input.value) : parseInt(input.value);

    if (isNaN(value)) {
        value = constraint.min; // Use minimum value instead of 0
    }

    // Calculate new value
    value += parseFloat(step);

    // Round to avoid floating point issues
    if (id === 'time') {
        value = Math.round(value * 10) / 10;
    }

    // Enforce min/max limits without wraparound
    value = Math.min(Math.max(value, constraint.min), constraint.max);

    input.value = value;

    // Disable buttons at limits
    const minusBtn = input.previousElementSibling;
    const plusBtn = input.nextElementSibling;

    minusBtn.disabled = value <= constraint.min;
    plusBtn.disabled = value >= constraint.max;
}

// Validate input on direct entry
function validateInput(input) {
    const id = input.id;
    const constraint = constraints[id];
    let value = id === 'time' ? parseFloat(input.value) : parseInt(input.value);

    if (isNaN(value)) {
        value = constraint.min;
    } else {
        // Round to nearest step
        const steps = Math.round((value - constraint.min) / constraint.step);
        value = constraint.min + (steps * constraint.step);

        // Enforce min/max
        value = Math.min(Math.max(value, constraint.min), constraint.max);

        // Round time values
        if (id === 'time') {
            value = Math.round(value * 10) / 10;
        }
    }

    input.value = value;
}

// Handle button click/touch
function handleAdjustButton(button, isLongPress = false) {
    const input = document.getElementById(button.dataset.input);
    const step = parseFloat(button.dataset.step);

    adjustValue(input, step);

    // For long press, adjust more quickly
    if (isLongPress) {
        longPressTimeout = setTimeout(() => {
            handleAdjustButton(button, true);
        }, 100);
    }
}

// Setup button event listeners
let longPressTimeout = null;

adjustButtons.forEach(button => {
    // Handle both click and touch events
    const startEvent = (e) => {
        e.preventDefault(); // Prevent double trigger on touch devices
        handleAdjustButton(button);
        longPressTimeout = setTimeout(() => {
            handleAdjustButton(button, true);
        }, 500);
    };

    const endEvent = () => {
        if (longPressTimeout) {
            clearTimeout(longPressTimeout);
            longPressTimeout = null;
        }
    };

    button.addEventListener('mousedown', startEvent);
    button.addEventListener('touchstart', startEvent);
    button.addEventListener('mouseup', endEvent);
    button.addEventListener('mouseleave', endEvent);
    button.addEventListener('touchend', endEvent);
    button.addEventListener('touchcancel', endEvent);
});

// Add input validation on change
[speedInput, distanceInput, timeInput].forEach(input => {
    input.addEventListener('change', () => validateInput(input));
    input.addEventListener('blur', () => validateInput(input));
});

// Show status message
function showStatus(message, isError = false) {
    statusMessage.textContent = message;
    statusMessage.className = 'status-message ' + (isError ? 'error' : 'success');
    setTimeout(() => {
        statusMessage.className = 'status-message';
    }, 3000);
}

// Convert hours to seconds
function hoursToSeconds(hours) {
    return Math.round(hours * 3600);
}

// Convert seconds to hours
function secondsToHours(seconds) {
    return seconds / 3600;
}

// Load current configuration
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();

        // Update current config
        currentConfig = config;

        // Update form values
        speedInput.value = config.speed_threshold;
        distanceInput.value = config.distance_threshold;
        timeInput.value = secondsToHours(config.time_threshold);
        fatigueInput.value = config.fatigue_threshold;
    } catch (error) {
        console.error('Error loading configuration:', error);
        showStatus('Failed to load configuration', true);
    }
}

// Get changed values only
function getChangedValues() {
    const changes = {};

    const newSpeed = parseInt(speedInput.value);
    if (!isNaN(newSpeed) && newSpeed !== currentConfig.speed_threshold) {
        changes.speed_threshold = newSpeed;
    }

    const newDistance = parseInt(distanceInput.value);
    if (!isNaN(newDistance) && newDistance !== currentConfig.distance_threshold) {
        changes.distance_threshold = newDistance;
    }

    const newTime = hoursToSeconds(parseFloat(timeInput.value));
    if (!isNaN(newTime) && newTime !== currentConfig.time_threshold) {
        changes.time_threshold = newTime;
    }

    const newFatigue = parseInt(fatigueInput.value);
    if (!isNaN(newFatigue) && newFatigue !== currentConfig.fatigue_threshold) {
        changes.fatigue_threshold = newFatigue;
    }

    return changes;
}

// Save configuration
async function saveConfig() {
    try {
        // Get only changed values
        const changes = getChangedValues();

        // If no changes, show message and return
        if (Object.keys(changes).length === 0) {
            showStatus('No changes to save');
            return;
        }

        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(changes)
        });

        const result = await response.json();

        if (response.ok) {
            // Update current config with new values
            currentConfig = result.config;
            showStatus('Configuration saved successfully');
        } else {
            showStatus(result.error || 'Failed to save configuration', true);
        }
    } catch (error) {
        console.error('Error saving configuration:', error);
        showStatus('Failed to save configuration', true);
    }
}

// Reset configuration
function resetConfig() {
    speedInput.value = defaultConfig.speed_threshold;
    distanceInput.value = defaultConfig.distance_threshold;
    timeInput.value = secondsToHours(defaultConfig.time_threshold);
    fatigueInput.value = defaultConfig.fatigue_threshold;
}

// Event listeners
saveButton.addEventListener('click', saveConfig);
resetButton.addEventListener('click', resetConfig);

// Load initial configuration
loadConfig(); 