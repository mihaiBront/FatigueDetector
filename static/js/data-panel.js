class DataPanel {
    constructor(containerId, faceDisplay) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container with id '${containerId}' not found`);
        }

        this.faceDisplay = faceDisplay;
        if (!this.faceDisplay) {
            throw new Error('FaceDisplay instance is required');
        }

        // Initialize data and default thresholds
        this.data = {
            time: "00:00:00",
            speed: "0",
            distance: "0.0",
            fatigue: "Unknown"
        };

        // Set default thresholds
        this.thresholds = {
            speed: 120,
            distance: 500,
            time: "04:00:00",
            fatigue: 1
        };

        // Then render and initialize elements
        this.render();
        this.initializeElements();

        // Finally load config
        this.loadConfig();
    }

    render() {
        this.container.innerHTML = `
            <div class="data-panel">
                <div class="data-item">
                    <div class="data-label">Time Traveled</div>
                    <div class="data-value" data-id="time">00:00:00</div>
                </div>

                <div class="data-item">
                    <div class="data-label">Current Speed</div>
                    <div class="data-value" data-id="speed">0 km/h</div>
                </div>

                <div class="data-item">
                    <div class="data-label">Distance Traveled</div>
                    <div class="data-value" data-id="distance">0.0 km</div>
                </div>

                <div class="data-item">
                    <div class="data-label">Fatigue Status</div>
                    <div class="data-value" data-id="fatigue">Unknown</div>
                </div>
            </div>
        `;
    }

    initializeElements() {
        // Get references to DOM elements after they are rendered
        this.timeValue = this.container.querySelector('[data-id="time"]');
        this.speedValue = this.container.querySelector('[data-id="speed"]');
        this.distanceValue = this.container.querySelector('[data-id="distance"]');
        this.fatigueValue = this.container.querySelector('[data-id="fatigue"]');

        if (!this.timeValue || !this.speedValue || !this.distanceValue || !this.fatigueValue) {
            throw new Error('Failed to initialize data elements');
        }
    }

    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const config = await response.json();
            console.log('Raw config from API:', config);

            // Map API response fields to our threshold fields
            this.thresholds = {
                speed: config.speed_threshold,
                distance: config.distance_threshold,
                time: this.formatTime(config.time_threshold), // Convert seconds to HH:MM:SS
                fatigue: config.fatigue_threshold
            };

            console.log('Mapped thresholds:', this.thresholds);
            this.checkExceeded();
        } catch (error) {
            console.error('Failed to load configuration:', error);
            // Keep using default thresholds
            console.log('Using default thresholds:', this.thresholds);
        }
    }

    formatTime(seconds) {
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    parseTime(timeStr) {
        const [hrs, mins, secs] = timeStr.split(':').map(Number);
        return hrs * 3600 + mins * 60 + secs;
    }

    checkExceeded() {
        // Check speed - parse the speed value correctly by removing "km/h" and converting to number
        const currentSpeed = parseFloat(this.data.speed.toString().replace(' km/h', ''));
        this.speedValue.classList.toggle('exceeded', currentSpeed > this.thresholds.speed);

        // Check distance - parse the distance value correctly by removing "km"
        const currentDistance = parseFloat(this.data.distance.toString().replace(' km', ''));
        this.distanceValue.classList.toggle('exceeded', currentDistance > this.thresholds.distance);

        // Check time
        const currentTimeSeconds = this.parseTime(this.data.time);
        const thresholdTimeSeconds = this.parseTime(this.thresholds.time);
        this.timeValue.classList.toggle('exceeded', currentTimeSeconds > thresholdTimeSeconds);

        // Check fatigue
        const fatigueLevel = this.getFatigueLevel(this.data.fatigue);
        this.fatigueValue.classList.toggle('exceeded', fatigueLevel > this.thresholds.fatigue);

        // Calculate time percentage for tired state
        const timePercentage = (currentTimeSeconds / thresholdTimeSeconds) * 100;
        console.log('Time percentage:', timePercentage);

        // Check conditions for face state
        const isExceeded = currentSpeed > this.thresholds.speed ||
            currentDistance > this.thresholds.distance ||
            currentTimeSeconds > thresholdTimeSeconds ||
            fatigueLevel > this.thresholds.fatigue;

        const isTired = timePercentage >= 50 && timePercentage < 100;
        console.log('Is tired:', isTired);

        // Update face state based on conditions
        if (isExceeded) {
            console.log('Setting worried');
            this.faceDisplay.setWorried(true);
        } else if (isTired) {
            console.log('Setting tired');
            this.faceDisplay.setTired(true);
        } else {
            console.log('Setting normal');
            this.faceDisplay.setNormal();
        }
    }

    getFatigueLevel(status) {
        const levels = {
            'Unknown': -1,
            'Not Tired': 0,
            'Lightly Tired': 1,
            'Heavily Tired': 2
        };
        return levels[status] || -1;
    }

    updateData(newData) {
        // Update internal data - store raw numbers without units
        if (newData.speed !== undefined) {
            this.data.speed = newData.speed.toString();
        }
        if (newData.distance) {
            this.data.distance = newData.distance.toString();
        }
        if (newData.time) {
            this.data.time = newData.time;
        }
        if (newData.fatigue) {
            this.data.fatigue = newData.fatigue;
        }

        // Update display with units
        if (newData.speed !== undefined) {
            this.speedValue.textContent = `${newData.speed} km/h`;
        }
        if (newData.distance) {
            this.distanceValue.textContent = `${newData.distance} km`;
        }
        if (newData.time) {
            this.timeValue.textContent = newData.time;
        }
        if (newData.fatigue) {
            this.fatigueValue.textContent = newData.fatigue;
        }

        // Check if any parameters exceed thresholds
        this.checkExceeded();
    }

    getFatigueStatus() {
        return this.data.fatigue;
    }
} 