/** 
A brute-forced incompressible 
fluid based on Smoothed Particles Hydrodynamics with 
Navier-Stokes equations 
*/

class SPHFluid {
  constructor() {
    // Physical attrs
    this.numParticles = 500;
    this.viscousity = 900 * 5;
    this.particleMass = 500 * .13;
    this.stiffness = 400 * 5;
    this.gravityConst = 120000 * 9.82;
    this.dt = 0.0004;

    this.particles_ = [];
    this.particlePositions_ = [this.numParticles];

    this.heightMap = null;

    this.START_OFFSET_X = 0;
    this.START_OFFSET_Y = 0;
    this.START_OFFSET_Z = 0;
    this.SQUARE_SIZE = 20;
    this.PARTICLE_RADIUS = 0.1*2/2; // h/2
    
    this.initParticles();
  }

  get particles() { return this.particles_; }
  get particlePositions() { return this.particlePositions_; }

  initParticles() {
    this.particles_ = [];
    // Set starting positions
    let k = 0;
    let j = 0;

    for (let i = 0; i < this.numParticles; i++) { //TODO:
      this.particles_.push({
        position: new THREE.Vector3(0, 0, 0),
        vel: new THREE.Vector3(100, 0, 0),
        pressure: 0,
        density: 0,
        viscousityForce: new THREE.Vector3(0, 0, 0),
        pressureForce: new THREE.Vector3(0, 0, 0),
        gravityForce: new THREE.Vector3(0, 0, 0),
        otherForce: new THREE.Vector3(0, 0, 0),
      });

      if (i % 40 === 0) {
        k++;
        j = 0;
      }
      j++;

      this.particles_[i].position.set(this.START_OFFSET_X + j * this.PARTICLE_RADIUS, 0, this.START_OFFSET_Z + k * this.PARTICLE_RADIUS);
      this.particlePositions_[i] = this.particles_[i].position;
    }
  }

  calculateDensityAndPressure() {
    for (let i = 0; i < this.particles_.length; i++) {
      let densitySum = 0;

      for (let j = 0 ; j < this.particles_.length; j++) {
        let diffVec = new THREE.Vector3(0, 0, 0);
        diffVec.subVectors(this.particles_[i].position, this.particles_[j].position);
        const absDiffVec = diffVec.length();

        if (absDiffVec < this.PARTICLE_RADIUS*2) {
          densitySum += this.particleMass *
              (315 / (64 * Math.PI * Math.pow(this.PARTICLE_RADIUS*2, 9.0))) *
              Math.pow((Math.pow(this.PARTICLE_RADIUS*2, 2.0) - Math.pow(absDiffVec, 2)), 3.0);
        }
      }

      this.particles_[i].density = densitySum;
      this.particles_[i].pressure = this.stiffness * (densitySum - 998);
    }
  }

  calculateForces() {
    for (let i = 0; i < this.numParticles; i++) {
      let gravity = new THREE.Vector3(
          0, -this.gravityConst * this.particles_[i].density, 0);
      let pressure = new THREE.Vector3(0, 0, 0);
      let viscousity = new THREE.Vector3(0, 0, 0);

      for (let j = 0; j < this.numParticles; j++) {
        if (i === j) {
          continue;
        }

        const diffVec = new THREE.Vector3(0, 0, 0);
        diffVec.subVectors(
            this.particles_[i].position, this.particles_[j].position);

        const absDiffVec = diffVec.length();
        if (absDiffVec < this.PARTICLE_RADIUS*2) {
          let W_const_pressure = 45 / (Math.PI * Math.pow(this.PARTICLE_RADIUS*2, 6.0)) *
              Math.pow(this.PARTICLE_RADIUS*2 - absDiffVec, 3.0) / absDiffVec;
          let W_pressure_gradient = new THREE.Vector3(
              W_const_pressure * diffVec.x, W_const_pressure * diffVec.y, W_const_pressure * diffVec.z);
          let visc_gradient =
              (45 / (Math.PI * Math.pow(this.PARTICLE_RADIUS*2, 6.0))) * (this.PARTICLE_RADIUS*2 - absDiffVec);

          pressure.add(
              W_pressure_gradient.multiplyScalar(
                  -this.particleMass *
                  ((this.particles_[i].pressure + this.particles_[j].pressure) /
                   (2 * this.particles_[j].density))));

          let tempVel = new THREE.Vector3(0, 0, 0);
          tempVel.subVectors(this.particles_[j].vel, this.particles_[i].vel);

          viscousity.add(
              tempVel.divideScalar(this.particles_[j].density)
                  .multiplyScalar(
                      this.viscousity * this.particleMass * visc_gradient));
        }
      }

      this.particles_[i].viscousityForce.set(viscousity.x, viscousity.y, viscousity.z);
      this.particles_[i].pressureForce.set(pressure.x, pressure.y, pressure.z);
      this.particles_[i].gravityForce.set(gravity.x, gravity.y, gravity.z);
    }
  }

  // Brute force style
  calculateAcceleration() {
    this.calculateDensityAndPressure();
    this.calculateForces();
  }

  idle() {
    let newPos = new THREE.Vector3(0, 0, 0);
    let newVel = new THREE.Vector3(0, 0, 0);
    let newPositions = [];

    for (let i = 0; i < this.particles_.length; i++) {
      newPos.addVectors(this.particles_[i].gravityForce, this.particles_[i].viscousityForce);
      newPos.add(this.particles_[i].pressureForce);
      newPos.add(this.particles_[i].otherForce)
          newPos.multiplyScalar((this.dt * this.dt) / (2 * this.particles_[i].density));
      newPos.add(this.particles_[i].vel.multiplyScalar(this.dt));
      newPos.add(this.particles_[i].position);

      newVel.subVectors(newPos, this.particles_[i].position);
      newVel.multiplyScalar(1 / this.dt);

      this.particles_[i].position.set(newPos.x, newPos.y, newPos.z);
      this.particles_[i].vel.set(newVel.x, newVel.y, newVel.z);
      newPositions.push(this.particles_[i].position);
      this.checkBoundaries(this.particles_[i]);
    }
    this.particlePositions_ = newPositions;
  }

  checkBoundaries(particle) {
    if ((particle.position.x*particle.position.x+particle.position.z*particle.position.z)<this.SQUARE_SIZE*this.SQUARE_SIZE) {
      particle.vel.x = -0.8 * particle.vel.x;
      particle.vel.z = -0.8 * particle.vel.z;
    }

    /*if (particle.position.x < -0.5* this.SQUARE_SIZE + this.PARTICLE_RADIUS + 1) {
      particle.vel.x = -0.8 * particle.vel.x;
      particle.position.x = -0.5* this.SQUARE_SIZE + this.PARTICLE_RADIUS + 1;
    }

    else if (particle.position.x > 0.5* this.SQUARE_SIZE - this.PARTICLE_RADIUS - 1) {
      particle.vel.x = -0.8 * particle.vel.x;
      particle.position.x = 0.5* this.SQUARE_SIZE - this.PARTICLE_RADIUS - 1;
    }

    if (particle.position.y < this.PARTICLE_RADIUS + 1) {
      particle.vel.y = -0.8 * particle.vel.y;
      particle.position.y = this.PARTICLE_RADIUS + 1;

    } else if (
      particle.position.y > this.SQUARE_SIZE - this.PARTICLE_RADIUS - 1) {
      particle.vel.y = -0.8 * particle.vel.y;
      particle.position.y = this.SQUARE_SIZE - this.PARTICLE_RADIUS - 1;
    }

    if (particle.position.z < -0.1* this.SQUARE_SIZE + this.PARTICLE_RADIUS + 1) {
      particle.vel.z = -0.8 * particle.vel.z;
      particle.position.z = -0.1* this.SQUARE_SIZE + this.PARTICLE_RADIUS + 1;

    } else if (
      particle.position.z > 0.1* this.SQUARE_SIZE - this.PARTICLE_RADIUS - 1) {
      particle.vel.z = -0.8 * particle.vel.z;
      particle.position.z = 0.1* this.SQUARE_SIZE - this.PARTICLE_RADIUS - 1;
    }*/
    
  }
}
