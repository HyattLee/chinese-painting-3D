/** 
A brute-forced incompressible 
fluid based on Smoothed Particles Hydrodynamics with 
Navier-Stokes equations 
*/

class SPHFluid {
  constructor(terrain) {
    // Physical attrs
    //this.numParticles = 500;
    this.viscousity = 900 * 5;
    this.particleMass = 500 * .13;
    this.stiffness = 6* 400 * 5;
    this.gravityConst = 3* 60000 * 9.82;
    this.dt = 0.0004;

    this.terrain = terrain;

    this.PARTICLE_RADIUS = 1*2/2; // h/2

    this.particles_ = [];
    this.numParticles = 0;
    this.particlePositions = [];
  }

  coverParticlesOnGround() {
    var fromID = this.numParticles;
    for (let x = -0.5*this.terrain['BOUND'][0]; x < 0.5*this.terrain['BOUND'][0]; x=x+2*this.PARTICLE_RADIUS) { //TODO:
      for (let z = -0.5*this.terrain['BOUND'][1]; z < 0.5*this.terrain['BOUND'][1]; z=z+2*this.PARTICLE_RADIUS) {
        if (this.terrain['POS'][x.toString()+'/'+z.toString()]==null) {
          continue;
        }
        var norm = this.terrain['POS'][x.toString()+'/'+z.toString()][0];
        var height = this.terrain['POS'][x.toString()+'/'+z.toString()][1];
        if (norm[0]==0 && norm[2]==0) {
          //continue;
        }
        if ((norm[0]!=0 || norm[2]!=0) || height!=0) {
          continue;
        }
        this.particles_.push({
          position: new THREE.Vector3(0, 0, 0),
          vel: new THREE.Vector3(0, 0, 0),
          pressure: 0,
          density: 0,
          viscousityForce: new THREE.Vector3(0, 0, 0),
          pressureForce: new THREE.Vector3(0, 0, 0),
          gravityForce: new THREE.Vector3(0, 0, 0),
          otherForce: new THREE.Vector3(0, 0, 0),
        });
        this.particles_[this.numParticles].position.set(x, this.terrain['POS'][x.toString()+'/'+z.toString()][1], z);
        this.particlePositions.push(this.particles_[this.numParticles].position);
        this.numParticles = this.numParticles + 1;
      }
    }
    var toID = this.numParticles-1;
    return [fromID, toID]
  }

  addParticles(pos_start, pos_end, move_dir, move_speed) {
    var tmp = this.calculatexyz(pos_start, pos_end);
    var tmp2 = this.calculatexyzSpeed(move_dir, move_speed);
    var currentNumParticles = Math.sqrt(Math.pow(pos_start[0]-pos_end[0],2)+Math.pow(pos_start[1]-pos_end[1],2)+Math.pow(pos_start[2]-pos_end[2],2))/this.PARTICLE_RADIUS;

    var fromID = this.numParticles;
    this.numParticles = this.numParticles + currentNumParticles;
    var toID = this.numParticles-1;

    var j = 0;
    for (let i = fromID; i < toID+1; i++) { //TODO:
      this.particles_.push({
        position: new THREE.Vector3(0, 0, 0),
        vel: new THREE.Vector3(0, 0, 0),
        pressure: 0,
        density: 0,
        viscousityForce: new THREE.Vector3(0, 0, 0),
        pressureForce: new THREE.Vector3(0, 0, 0),
        gravityForce: new THREE.Vector3(0, 0, 0),
        otherForce: new THREE.Vector3(0, 0, 0),
      });

      this.particles_[i].position.set(pos_start[0]+j*tmp[0], pos_start[1]+j*tmp[1], pos_start[2]+j*tmp[2]);
      this.particles_[i].vel.set(tmp2[0], tmp2[1], tmp2[2]);
      this.particlePositions.push(this.particles_[i].position);
      j = j + 1;
    }
    return [fromID, toID]
  }

  calculatexyz(pos_start, pos_end) {
    var tmpX = pos_end[0]-pos_start[0];
    var tmpY = pos_end[1]-pos_start[1];
    var tmpZ = pos_end[2]-pos_start[2];
    var tmpx = 0;
    var tmpy = 0;
    var tmpz = 0;
    if (tmpX!=0) {
      tmpx = 2*this.PARTICLE_RADIUS/Math.sqrt(Math.pow(tmpY/tmpX, 2)+1+Math.pow(tmpZ/tmpX, 2));
    }
    if (tmpY!=0) {
      tmpy = 2*this.PARTICLE_RADIUS/Math.sqrt(Math.pow(tmpX/tmpY, 2)+1+Math.pow(tmpZ/tmpY, 2));
    }
    if (tmpZ!=0) {
      tmpz = 2*this.PARTICLE_RADIUS/Math.sqrt(Math.pow(tmpX/tmpZ, 2)+1+Math.pow(tmpY/tmpZ, 2));
    }
    return [tmpx, tmpy, tmpz];
  }

  calculatexyzSpeed(move_dir, move_speed) {
    var tmp = Math.sqrt(Math.pow(move_dir[0], 2)+Math.pow(move_dir[1], 2)+Math.pow(move_dir[2], 2));
    return [move_speed*move_dir[0]/tmp, move_speed*move_dir[1]/tmp, move_speed*move_dir[2]/tmp];
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
    this.particlePositions = newPositions;
  }

  getTerrainInfo(x, z) {
    var id = Math.round(x).toString()+'/'+Math.round(z).toString();
    if (this.terrain['POS'][id]!=null) {
      return this.terrain['POS'][id];
    } else {
      return null
    }
  }

  calculateReflection(inputVec, normVec) {
    var outVec = [0, 0, 0];
    //console.warn(inputVec);
    var inputVecValue = Math.sqrt(inputVec[0]*inputVec[0]+inputVec[1]*inputVec[1]+inputVec[2]*inputVec[2]);
    var inputVecNew = [inputVec[0]/inputVecValue, inputVec[1]/inputVecValue, inputVec[2]/inputVecValue];
    
    var inputVecNew_normVec = inputVecNew[0]*normVec[0]+inputVecNew[1]*normVec[1]+inputVecNew[2]*normVec[2];
    outVec[0] = inputVecValue*(inputVecNew[0]-2*inputVecNew_normVec*normVec[0]);
    outVec[1] = inputVecValue*(inputVecNew[1]-2*inputVecNew_normVec*normVec[1]);
    outVec[2] = inputVecValue*(inputVecNew[2]-2*inputVecNew_normVec*normVec[2]);
    return outVec;
  }

  gridPos(pos) {
    return (pos);
  }

  checkBoundaries(particle) {
    var decline = 0.65;
    if (this.gridPos(particle.position.x) < -0.5* this.terrain['BOUND'][0] + this.PARTICLE_RADIUS + 1) {
      particle.vel.x = -0.8 * particle.vel.x;
      particle.position.x = -0.5* this.terrain['BOUND'][0] + this.PARTICLE_RADIUS + 1;
    }

    else if (this.gridPos(particle.position.x) > 0.5* this.terrain['BOUND'][0] - this.PARTICLE_RADIUS - 1) {
      particle.vel.x = -0.8 * particle.vel.x;
      particle.position.x = 0.5* this.terrain['BOUND'][0] - this.PARTICLE_RADIUS - 1;
    }

    if (this.gridPos(particle.position.z) < -0.5* this.terrain['BOUND'][1] + this.PARTICLE_RADIUS + 1) {
      particle.vel.z = -0.8 * particle.vel.z;
      particle.position.z = -0.5* this.terrain['BOUND'][1] + this.PARTICLE_RADIUS + 1;

    } else if (
      this.gridPos(particle.position.z) > 0.5* this.terrain['BOUND'][1] - this.PARTICLE_RADIUS - 1) {
      particle.vel.z = -0.8 * particle.vel.z;
      particle.position.z = 0.5* this.terrain['BOUND'][1] - this.PARTICLE_RADIUS - 1;
    }

    if (this.gridPos(particle.position.y) > this.terrain['BOUND'][0] - this.PARTICLE_RADIUS - 1) {
      particle.vel.y = -0.8 * particle.vel.y;
      particle.position.y = this.terrain['BOUND'][0] - this.PARTICLE_RADIUS - 1;
    }

    var terrainInfo = this.getTerrainInfo(particle.position.x, particle.position.z);
    if (terrainInfo!=null) {
      if(terrainInfo[1]>this.gridPos(particle.position.y)) {
          var vTmp = this.calculateReflection([particle.vel.x, particle.vel.y, particle.vel.z], terrainInfo[0]);
          particle.vel.x = decline*vTmp[0];
          particle.vel.y = decline*vTmp[1];
          particle.vel.z = decline*vTmp[2];

          particle.position.y = terrainInfo[1];
      }
    }
  }
}
