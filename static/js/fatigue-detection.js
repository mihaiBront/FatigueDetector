class FatigueDetection {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.websocket = null;
        this.isRunning = false;
        this.fatigueLevel = null;
        this.fatigueData = null;
        this.captureInterval = null;
        this.imageElement = null;
        
        this.init();
    }

    async init() {
        try {
            // Create image element to show camera feed from Python
            this.imageElement = document.createElement('img');
            this.imageElement.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                width: 320px;
                height: 240px;
                z-index: 1000;
                border: 2px solid red;
                object-fit: cover;
            `;
            this.imageElement.alt = "Camera Feed";
            document.body.appendChild(this.imageElement);

            console.log('Camera display initialized (Python backend)');
            this.startImageUpdate();

        } catch (error) {
            console.error('Error initializing camera display:', error);
        }
    }

    startImageUpdate() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        
        // Update image every second
        this.captureInterval = setInterval(() => {
            this.updateCameraImage();
        }, 1000);
    }

    updateCameraImage() {
        if (!this.imageElement) return;
        
        // Add timestamp to prevent caching
        const timestamp = new Date().getTime();
        this.imageElement.src = `/static/current_frame.jpg?t=${timestamp}`;
        
        // Handle image load error
        this.imageElement.onerror = () => {
            console.log('No camera image available yet...');
        };
        
        this.imageElement.onload = () => {
            console.log('Camera image updated');
        };
    }

    stopDetection() {
        this.isRunning = false;
        if (this.captureInterval) {
            clearInterval(this.captureInterval);
            this.captureInterval = null;
        }
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
    }

    getFatigueLevel() {
        return this.fatigueLevel;
    }

    getFatigueData() {
        return this.fatigueData;
    }
}

// Export for use in other scripts
window.FatigueDetection = FatigueDetection; 