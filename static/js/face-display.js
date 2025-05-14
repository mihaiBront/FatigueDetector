class FaceDisplay {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      throw new Error(`Container with id '${containerId}' not found`);
    }
    this.render();
    this.initializeElements();
  }

  render() {
    this.container.innerHTML = `
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
    `;
  }

  initializeElements() {
    this.face = this.container.querySelector('.face');
    this.eyes = this.container.querySelector('.eyes');
    this.mouth = this.container.querySelector('.mouth');
    this.currentState = 'normal';
  }

  setNormal() {
    console.log('root:Setting normal');
    if (this.currentState !== 'normal') {
      console.log('root:Setting normal: removing worried and tired');
      document.body.classList.remove('worried', 'tired');
      this.eyes.classList.remove('worried', 'tired');
      this.mouth.classList.remove('worried', 'tired');
      this.currentState = 'normal';
    }
  }

  setWorried(isWorried) {
    console.log('root:Setting worried');
    if (isWorried && this.currentState !== 'worried') {
      console.log('root:Setting worried: removing tired');
      document.body.classList.remove('tired');
      document.body.classList.add('worried');
      this.eyes.classList.remove('tired');
      this.eyes.classList.add('worried');
      this.mouth.classList.remove('tired');
      this.mouth.classList.add('worried');
      this.currentState = 'worried';
    } else if (!isWorried && this.currentState === 'worried') {
      this.setNormal();
    }
  }

  setTired(isTired) {
    console.log('root:Setting tired');
    if (isTired && this.currentState !== 'tired') {
      console.log('root:Setting tired: removing worried');
      document.body.classList.remove('worried');
      document.body.classList.add('tired');
      this.eyes.classList.remove('worried');
      this.eyes.classList.add('tired');
      this.mouth.classList.remove('worried');
      this.mouth.classList.add('tired');
      this.currentState = 'tired';
    } else if (!isTired && this.currentState === 'tired') {
      this.setNormal();
    }
  }
}
