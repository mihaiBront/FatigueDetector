class FaceDisplay {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.render();
    this.initializeElements();
    // this.startWorryCycle();
    this.setWorried(true);
  }

  render() {
    this.container.innerHTML = `
      <div class="container">
        <div class="face">
          <div class="eyes">
            <div class="eye left">
              <div class="eyebrow"></div>
            </div>
            <div class="eye right">
              <div class="eyebrow"></div>
            </div>
          </div>
          <div class="mouth"></div>
        </div>

        <div class="data-panel">
          <div class="data-item">
            <div class="data-label">Time Traveled</div>
            <div class="data-value" data-id="time">00:00:00</div>
          </div>

          <div class="data-item">
            <div class="data-label">Distance Traveled</div>
            <div class="data-value" data-id="distance">0.0 km</div>
          </div>

          <div class="data-item">
            <div class="data-label">Signs of Fatigue</div>
            <ul class="fatigue-signs" data-id="fatigue-list">
              <li>No signs detected</li>
            </ul>
          </div>
        </div>
      </div>
    `;
  }

  initializeElements() {
    // DOM elements
    this.eyes = this.container.querySelector(".eyes");
    this.mouth = this.container.querySelector(".mouth");
    this.body = document.body;

    // Data elements
    this.timeValue = this.container.querySelector('[data-id="time"]');
    this.distanceValue = this.container.querySelector('[data-id="distance"]');
    this.fatigueList = this.container.querySelector('[data-id="fatigue-list"]');

    // State
    this.isWorried = false;
    this.isDead = true;
    this.data = {
      time: "00:00:00",
      distance: "0.0",
      fatigueSigns: [],
    };
  }

  setWorried(isWorried) {
    this.isWorried = isWorried;
    if (isWorried) {
      this.eyes.classList.add("worried");
      this.mouth.classList.add("worried");
      this.body.classList.add("worried");
    } else {
      this.eyes.classList.remove("worried");
      this.mouth.classList.remove("worried");
      this.body.classList.remove("worried");
    }
  }

  setDead(isDead) {
    this.isDead = isDead;
    if (isDead) {
      this.eyes.classList.add("dead");
      this.mouth.classList.add("dead");
      this.body.classList.add("dead");
    } else {
      this.eyes.classList.remove("dead");
      this.mouth.classList.remove("dead");
      this.body.classList.remove("dead");
    }
  }

  setNomral() {
    this.setWorried(false);
    this.setDead(false);
  }

  updateData(newData) {
    // Update internal data
    Object.assign(this.data, newData);

    // Update display
    if (newData.time) this.timeValue.textContent = newData.time;
    if (newData.distance)
      this.distanceValue.textContent = `${newData.distance} km`;
    if (newData.fatigueSigns) {
      this.fatigueList.innerHTML = newData.fatigueSigns
        .map((sign) => `<li>${sign}</li>`)
        .join("");
    }
  }

  startWorryCycle() {
    setInterval(() => {
      this.setWorried(!this.isWorried);
    }, 15000);
  }
}

// Initialize the display
const faceDisplay = new FaceDisplay("app-container");
