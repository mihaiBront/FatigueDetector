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

        // Fatigue state management (now managed by backend)
        this.isPersistentFatigueActive = false;
        this.restButton = null;

        // Then render and initialize elements
        this.render();
        this.initializeElements();
        this.createRestButton();

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

    createRestButton() {
        console.log('Creating rest button...');
        this.restButton = document.createElement('button');
        this.restButton.textContent = 'Stop to Rest';
        this.restButton.className = 'rest-button';
        this.restButton.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            padding: 20px 40px;
            font-size: 24px;
            font-weight: bold;
            background-color: #ff4444;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            z-index: 2000;
            display: none;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        `;
        
        this.restButton.addEventListener('click', () => {
            console.log('Rest button clicked!');
            this.clearPersistentFatigue();
        });

        document.body.appendChild(this.restButton);
        console.log('Rest button created and added to DOM');
    }

    activatePersistentFatigue() {
        if (this.isPersistentFatigueActive) {
            console.log('Persistent fatigue already active, skipping...');
            return;
        }
        
        console.log('ACTIVATING PERSISTENT FATIGUE STATE!');
        this.isPersistentFatigueActive = true;
        this.faceDisplay.setTired(true);
        
        if (this.restButton) {
            this.restButton.style.display = 'block';
            console.log('Rest button shown');
        } else {
            console.error('Rest button not found!');
        }
        
        // Force display "Cansado" status
        this.fatigueValue.textContent = "Cansado";
        console.log('Fatigue status set to Cansado');
    }

    async clearPersistentFatigue() {
        console.log('Clearing persistent fatigue state');
        
        try {
            // Call backend to reset fatigue state
            const response = await fetch('/api/reset_fatigue', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Backend fatigue state reset:', result);
                
                this.isPersistentFatigueActive = false;
                this.restButton.style.display = 'none';
                this.faceDisplay.setNormal();
                
                // Update fatigue display to current actual status
                this.fatigueValue.textContent = "Not Tired";
                console.log('Fatigue state reset successfully');
            } else {
                console.error('Failed to reset fatigue state on backend');
            }
        } catch (error) {
            console.error('Error resetting fatigue state:', error);
        }
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

        // Check fatigue - handle both string and numeric values
        let fatigueLevel;
        if (typeof this.data.fatigue === 'string') {
            fatigueLevel = this.getFatigueLevel(this.data.fatigue);
        } else {
            fatigueLevel = this.data.fatigue;
        }
        
        console.log('Current fatigue level:', fatigueLevel, 'Type:', typeof fatigueLevel, 'Raw data:', this.data.fatigue);
        
        this.fatigueValue.classList.toggle('exceeded', fatigueLevel > this.thresholds.fatigue);

        // Calculate time percentage for tired state
        const timePercentage = (currentTimeSeconds / thresholdTimeSeconds) * 100;

        // Handle persistent fatigue state (managed by backend)
        // Check if backend indicates persistent fatigue is active
        if ((fatigueLevel === 2 || this.data.persistent_fatigue_active) && !this.isPersistentFatigueActive) {
            console.log('Backend activated persistent fatigue! Showing button...', {
                fatigueLevel: fatigueLevel,
                persistent_fatigue_active: this.data.persistent_fatigue_active
            });
            this.activatePersistentFatigue();
            return; // Don't process other states when persistent fatigue is active
        }

        // Only process other states if persistent fatigue is not active
        if (!this.isPersistentFatigueActive) {
            const isExceeded = currentSpeed > this.thresholds.speed ||
                currentDistance > this.thresholds.distance ||
                currentTimeSeconds > thresholdTimeSeconds ||
                fatigueLevel > this.thresholds.fatigue;

            const isTired = timePercentage >= 50 && timePercentage < 100;

            // Update face state based on conditions
            if (isExceeded) {
                console.log('Setting worried');
                this.faceDisplay.setWorried(true);
            } else if (isTired) {
                console.log('Setting tired (time based)');
                this.faceDisplay.setTired(true);
            } else {
                console.log('Setting normal');
                this.faceDisplay.setNormal();
            }
        }
    }

    getFatigueLevel(status) {
        const levels = {
            'Unknown': -1,
            'Not Tired': 0,
            'Tired': 1,
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
        // Store backend fatigue state
        if (newData.persistent_fatigue_active !== undefined) {
            this.data.persistent_fatigue_active = newData.persistent_fatigue_active;
        }
        if (newData.fatigue_counter !== undefined) {
            this.data.fatigue_counter = newData.fatigue_counter;
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
        if (newData.fatigue && !this.isPersistentFatigueActive) {
            // Only update fatigue display if not in persistent fatigue mode
            const displayText = newData.fatigue === "Tired" ? "Cansado" : newData.fatigue;
            this.fatigueValue.textContent = displayText;
        }

        // Check if any parameters exceed thresholds
        this.checkExceeded();
    }

    getFatigueStatus() {
        return this.data.fatigue;
    }
} 