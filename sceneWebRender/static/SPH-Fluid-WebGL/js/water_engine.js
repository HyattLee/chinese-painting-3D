/** 
A simple ThreeJS/WebGL renderer that takes in a sph-fluid
and renders the positions of the particles
 */

class WaterEngine {
  constructor(fluid){
    this.controls = null
    this.scene = null;
    this.camera = null; 
    this.renderer = null
    this.meshes = [];
    this.fluid = fluid;
    
    // Set up all ThreeJS stuff
    this.setup();
    this.initScene();
  }

  clear() {
    for( var i = this.scene.children.length - 1 ; i > 0; i--){
      this.scene.remove(this.scene.children[i]);
    }
  }

  setup(){
    this.scene = new THREE.Scene();

    this.camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 1, 10000 );
    this.camera.position.z = 1000;
    this.camera.position.set(WaterEngine.SQUARE_SIZE / 2, WaterEngine.SQUARE_SIZE / 2, WaterEngine.START_OFFSET_Z);

    this.renderer = new THREE.WebGLRenderer();
    this.renderer.setSize( window.innerWidth, window.innerHeight );
    this.renderer.setClearColor( 0xe0e0e0, 1);

    this.controls = new THREE.TrackballControls( this.camera, this.renderer.domElement );
    this.controls.rotateSpeed = 15.0;
    this.controls.zoomSpeed = 6;
    this.controls.panSpeed = 0.8;
    this.controls.noZoom = false;
    this.controls.noPan = false;
    this.controls.staticMoving = true;
    this.controls.dynamicDampingFactor = 0.15;
    this.controls.keys = [ 65, 83, 68 ];

    // Resizing window
    THREEx.WindowResize(this.renderer, this.camera);
    document.body.appendChild( this.renderer.domElement );
  };

  initScene() {
    this.clear();
    this.drawGrid();
  
    const geometry = new THREE.CircleGeometry( WaterEngine.PARTICLE_RADIUS, 16 );
    const material = new THREE.MeshBasicMaterial( {color: 0x2FA1D6} );
    // const material = new THREE.MeshBasicMaterial( {map : new
    // THREE.TextureLoader().load('../img/circle.png')} );
    for (const position of this.fluid.particlePositions) {
      let mesh = new THREE.Mesh(geometry, material);      
      mesh.position.set(position.x, position.y, position.z);
      this.meshes.push(mesh);
      this.scene.add(mesh);
    }
  }

  update_(positions) {
    for (let i = 0; i < positions.length; i++) {
      this.meshes[i].position.set(
          positions[i].x, positions[i].y, positions[i].z);
    }
  }

  render() {
    requestAnimationFrame( this.render.bind(this) ); 
    this.fluid.calculateAcceleration();
    this.fluid.idle();
    this.update_(this.fluid.particlePositions);
    this.controls.update();
    this.renderer.render( this.scene, this.camera );
  }

  drawGrid() {
    let rectShape = new THREE.Shape();
    rectShape.moveTo(0, 0);
    rectShape.lineTo(0, WaterEngine.SQUARE_SIZE);
    rectShape.lineTo(WaterEngine.SQUARE_SIZE, WaterEngine.SQUARE_SIZE);
    rectShape.lineTo(WaterEngine.SQUARE_SIZE, 0);
    rectShape.lineTo(0, 0);

    const rectGeom = new THREE.ShapeGeometry(rectShape);
    const rectMesh = new THREE.Mesh(
        rectGeom, new THREE.MeshBasicMaterial({color: 0xffffff}));

    const geometry = new THREE.Geometry();
    const material = new THREE.LineBasicMaterial(
        {color: 0xff9b9b, linewidth: WaterEngine.LINE_WIDTH});

    this.scene.add(rectMesh)
  };
}

WaterEngine.START_OFFSET_X = 100;
WaterEngine.START_OFFSET_Y = 256;
WaterEngine.START_OFFSET_Z = 750;
WaterEngine.SQUARE_SIZE = 512;
WaterEngine.LINE_WIDTH = 10;
WaterEngine.PARTICLE_RADIUS = 16/2; // h/2
