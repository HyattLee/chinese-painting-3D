/**
 * @author Mugen87 / https://github.com/Mugen87
 *
 * References:
 *	http://www.valvesoftware.com/publications/2010/siggraph2010_vlachos_waterflow.pdf
 * 	http://graphicsrunner.blogspot.de/2010/08/water-using-flow-maps.html
 *
 */

THREE.Water = function ( geometry, options ) {

	THREE.Mesh.call( this, geometry );

	this.type = 'Water';

	var scope = this;

	options = options || {};

	var color = ( options.color !== undefined ) ? new THREE.Color( options.color ) : new THREE.Color( 0xFFFFFF );
	var textureWidth = options.textureWidth || 512;
	var textureHeight = options.textureHeight || 512;
	var clipBias = options.clipBias || 0;
	var flowDirection = options.flowDirection || new THREE.Vector2( 1, 0 );
	var flowSpeed = options.flowSpeed || 0.03;
	var reflectivity = options.reflectivity || 0.02;
	var alpha = options.alpha || 1;
	var scale = options.scale || 1;
	var shader = options.shader || THREE.Water.WaterShader;

	var textureLoader = new THREE.TextureLoader();

	var flowMap = options.flowMap || undefined;
	var normalMap0 = options.normalMap0 || textureLoader.load( '/static/texture/Water_1_M_Normal.jpg' );
	var normalMap1 = options.normalMap1 || textureLoader.load( '/static/texture/Water_2_M_Normal.jpg' );

	var cycle = 0.15; // a cycle of a flow map phase
	var halfCycle = cycle * 0.5;
	var textureMatrix = new THREE.Matrix4();
	var clock = new THREE.Clock();

	// internal components

	if ( THREE.Reflector === undefined ) {

		console.error( 'THREE.Water: Required component THREE.Reflector not found.' );
		return;

	}

	if ( THREE.Refractor === undefined ) {

		console.error( 'THREE.Water: Required component THREE.Refractor not found.' );
		return;

	}

	var reflector = new THREE.Reflector( geometry, {
		textureWidth: textureWidth,
		textureHeight: textureHeight,
		clipBias: clipBias
	} );

	var refractor = new THREE.Refractor( geometry, {
		textureWidth: textureWidth,
		textureHeight: textureHeight,
		clipBias: clipBias
	} );

	reflector.matrixAutoUpdate = false;
	refractor.matrixAutoUpdate = false;

	// material
	this.material = new THREE.ShaderMaterial( {
		uniforms: THREE.UniformsUtils.merge( [
			THREE.UniformsLib[ 'fog' ],
			THREE.ShaderLib[ 'phong' ].uniforms,
			shader.uniforms,
			{
				heightmap: { value: null }, 
				alpha: {value: null}
			},
			THREE.Water.WaterShader.uniforms
		] ),
		vertexShader: shader.vertexShader,
		fragmentShader: shader.fragmentShader,
		transparent: true,
		fog: true
	} );

	if ( flowMap !== undefined ) {

		this.material.defines.USE_FLOWMAP = '';
		this.material.uniforms.tFlowMap = {
			type: 't',
			value: flowMap
		};

	} else {

		this.material.uniforms.flowDirection = {
			type: 'v2',
			value: flowDirection
		};

	}

	// maps
	normalMap0.wrapS = normalMap0.wrapT = THREE.RepeatWrapping;
	normalMap1.wrapS = normalMap1.wrapT = THREE.RepeatWrapping;

	this.material.uniforms.tReflectionMap.value = reflector.getRenderTarget().texture;
	this.material.uniforms.tRefractionMap.value = refractor.getRenderTarget().texture;
	this.material.uniforms.tNormalMap0.value = normalMap0;
	this.material.uniforms.tNormalMap1.value = normalMap1;

	// water
	this.material.uniforms.color.value = color;
	this.material.uniforms.reflectivity.value = reflectivity;
	this.material.uniforms.alpha.value = alpha;
	this.material.uniforms.textureMatrix.value = textureMatrix;

	// inital values
	this.material.uniforms.config.value.x = 0; // flowMapOffset0
	this.material.uniforms.config.value.y = halfCycle; // flowMapOffset1
	this.material.uniforms.config.value.z = halfCycle; // halfCycle
	this.material.uniforms.config.value.w = scale; // scale
	this.material.defines.BOUNDS = BOUNDS.toFixed( 1 );
	this.material.defines.WIDTH = WIDTH.toFixed( 1 );

	// functions
	function updateTextureMatrix( camera ) {

		textureMatrix.set(
			0.5, 0.0, 0.0, 0.5,
			0.0, 0.5, 0.0, 0.5,
			0.0, 0.0, 0.5, 0.5,
			0.0, 0.0, 0.0, 1.0
		);

		textureMatrix.multiply( camera.projectionMatrix );
		textureMatrix.multiply( camera.matrixWorldInverse );
		textureMatrix.multiply( scope.matrixWorld );

	}

	function updateFlow() {

		var delta = clock.getDelta();
		var config = scope.material.uniforms.config;

		config.value.x += flowSpeed * delta; // flowMapOffset0
		config.value.y = config.value.x + halfCycle; // flowMapOffset1

		// Important: The distance between offsets should be always the value of "halfCycle".
		// Moreover, both offsets should be in the range of [ 0, cycle ].
		// This approach ensures a smooth water flow and avoids "reset" effects.

		if ( config.value.x >= cycle ) {

			config.value.x = 0;
			config.value.y = halfCycle;

		} else if ( config.value.y >= cycle ) {

			config.value.y = config.value.y - cycle;

		}

	}

	//

	this.onBeforeRender = function ( renderer, scene, camera ) {

		updateTextureMatrix( camera );
		updateFlow();

		scope.visible = false;

		reflector.matrixWorld.copy( scope.matrixWorld );
		refractor.matrixWorld.copy( scope.matrixWorld );

		reflector.onBeforeRender( renderer, scene, camera );
		refractor.onBeforeRender( renderer, scene, camera );

		scope.visible = true;

	};

};

THREE.Water.prototype = Object.create( THREE.Mesh.prototype );
THREE.Water.prototype.constructor = THREE.Water;

THREE.Water.WaterShader = {

	uniforms: {

		'color': {
			type: 'c',
			value: null
		},

		'reflectivity': {
			type: 'f',
			value: 0
		},

		'tReflectionMap': {
			type: 't',
			value: null
		},

		'tRefractionMap': {
			type: 't',
			value: null
		},

		'tNormalMap0': {
			type: 't',
			value: null
		},

		'tNormalMap1': {
			type: 't',
			value: null
		},

		'textureMatrix': {
			type: 'm4',
			value: null
		},

		'config': {
			type: 'v4',
			value: new THREE.Vector4()
		}

	},

	vertexShader: 
		[
		THREE.ShaderChunk[ 'fog_pars_vertex' ],
		`uniform sampler2D heightmap;
		#define PHONG
		varying vec3 vViewPosition;
		#ifndef FLAT_SHADED
			varying vec3 vNormal;
		#endif
		#include <common>
		#include <uv_pars_vertex>
		#include <uv2_pars_vertex>
		#include <displacementmap_pars_vertex>
		#include <envmap_pars_vertex>
		#include <color_pars_vertex>
		#include <morphtarget_pars_vertex>
		#include <skinning_pars_vertex>
		#include <shadowmap_pars_vertex>
		#include <logdepthbuf_pars_vertex>
		#include <clipping_planes_pars_vertex>

		//
		uniform mat4 textureMatrix;
		varying vec4 vCoord;
		varying vec2 vUv;
		varying vec3 vToEye;

		void main() {
			vec2 cellSize = vec2( 1.0 / WIDTH, 1.0 / WIDTH );
			#include <uv_vertex>
			#include <uv2_vertex>
			#include <color_vertex>
			// # include <beginnormal_vertex>
			// Compute normal from heightmap
			vec3 objectNormal = vec3(
				( texture2D( heightmap, uv + vec2( - cellSize.x, 0 ) ).x - texture2D( heightmap, uv + vec2( cellSize.x, 0 ) ).x ) * WIDTH / BOUNDS,
				( texture2D( heightmap, uv + vec2( 0, - cellSize.y ) ).x - texture2D( heightmap, uv + vec2( 0, cellSize.y ) ).x ) * WIDTH / BOUNDS,
				1.0 );
			//<beginnormal_vertex>
			#include <morphnormal_vertex>
			#include <skinbase_vertex>
			#include <skinnormal_vertex>
			#include <defaultnormal_vertex>

		#ifndef FLAT_SHADED // Normal computed with derivatives when FLAT_SHADED
				vNormal = normalize( transformedNormal );

		#endif
			//# include <begin_vertex>
			float heightValue = texture2D( heightmap, uv ).x;
			vec3 transformed = vec3( position.x, position.y, heightValue );
			//<begin_vertex>
			#include <morphtarget_vertex>
			#include <skinning_vertex>
			#include <displacementmap_vertex>
			#include <project_vertex>
			#include <logdepthbuf_vertex>
			#include <clipping_planes_vertex>

			vViewPosition = - mvPosition.xyz;

			#include <worldpos_vertex>
			#include <envmap_vertex>
			#include <shadowmap_vertex>

			//
			vCoord = textureMatrix * vec4( position, 1.0 );
			vUv = uv;
			vToEye = cameraPosition - worldPosition.xyz;
		`, 
		THREE.ShaderChunk[ 'fog_vertex' ],
		'}'
		].join( '\n' ),

	fragmentShader: [
		'#include <common>',
		'#include <fog_pars_fragment>',

		'uniform sampler2D tReflectionMap;',
		'uniform sampler2D tRefractionMap;',
		'uniform sampler2D tNormalMap0;',
		'uniform sampler2D tNormalMap1;',

		'#ifdef USE_FLOWMAP',
		'	uniform sampler2D tFlowMap;',
		'#else',
		'	uniform vec2 flowDirection;',
		'#endif',

		'uniform vec3 color;',
		'uniform float reflectivity;',
		'uniform float alpha;',
		'uniform vec4 config;',

		'varying vec4 vCoord;',
		'varying vec2 vUv;',
		'varying vec3 vToEye;',

		'void main() {',

		'	float flowMapOffset0 = config.x;',
		'	float flowMapOffset1 = config.y;',
		'	float halfCycle = config.z;',
		'	float scale = config.w;',

		'	vec3 toEye = normalize( vToEye );',

		// determine flow direction
		'	vec2 flow;',
		'	#ifdef USE_FLOWMAP',
		'		flow = texture2D( tFlowMap, vUv ).rg * 2.0 - 1.0;',
		'	#else',
		'		flow = flowDirection;',
		'	#endif',
		'	flow.x *= - 1.0;',

		// sample normal maps (distort uvs with flowdata)
		'	vec4 normalColor0 = texture2D( tNormalMap0, ( vUv * scale ) + flow * flowMapOffset0 );',
		'	vec4 normalColor1 = texture2D( tNormalMap1, ( vUv * scale ) + flow * flowMapOffset1 );',

		// linear interpolate to get the final normal color
		'	float flowLerp = abs( halfCycle - flowMapOffset0 ) / halfCycle;',
		'	vec4 normalColor = mix( normalColor0, normalColor1, flowLerp );',

		// calculate normal vector
		'	vec3 normal = normalize( vec3( normalColor.r * 2.0 - 1.0, normalColor.b,  normalColor.g * 2.0 - 1.0 ) );',

		// calculate the fresnel term to blend reflection and refraction maps
		'	float theta = max( dot( toEye, normal ), 0.0 );',
		'	float reflectance = reflectivity + ( 1.0 - reflectivity ) * pow( ( 1.0 - theta ), 1.5 );', //5.0

		// calculate final uv coords
		'	vec3 coord = vCoord.xyz / vCoord.w;',
		'	vec2 uv = coord.xy + coord.z * normal.xz * 0.05;',

		'	vec4 reflectColor = texture2D( tReflectionMap, uv );',
		'	vec4 refractColor = texture2D( tRefractionMap, uv );',

		// multiply water color with the mix of both textures: '	gl_FragColor = vec4( color, alpha ) * mix( refractColor, reflectColor, reflectance );',
		'	gl_FragColor = vec4( color, alpha ) * mix( refractColor, reflectColor, reflectance );',

		'	#include <tonemapping_fragment>',
		'	#include <encodings_fragment>',
		'	#include <fog_fragment>',

		'}'

	].join( '\n' )
};
