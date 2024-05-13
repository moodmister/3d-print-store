import * as THREE from 'three';
import { ArcballControls } from 'three/addons/controls/ArcballControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

const loader = new STLLoader();
const stlFileInput = document.querySelector('#stl_models');
const stlViewWrapper = document.querySelector('#stl-viewer');
const width = parseInt(stlViewWrapper.style.width);
const height = parseInt(stlViewWrapper.style.height);


const camera = new THREE.PerspectiveCamera( 75, width / height, 0.01, 10000 );
camera.position.set(100, 100, 100);
camera.lookAt(new THREE.Vector3(0, 0, 0));
camera.up = new THREE.Vector3(-Math.cos(Math.PI / 2), -Math.cos(Math.PI / 2), 0);
const scene = new THREE.Scene();


// const geometry = new THREE.BoxGeometry( 0.5, 0.5, 0.5 );
const material = new THREE.MeshNormalMaterial();
const axes = new THREE.AxesHelper(500);
axes.setColors(
  new THREE.Color(0xff0000),
  new THREE.Color(0x00ff00),
  new THREE.Color(0x0000ff)
);
const printerPlate = new THREE.Mesh(
  new THREE.PlaneGeometry(235, 235),
  new THREE.MeshBasicMaterial({ color: new THREE.Color(0xc4a161) })
);
const stlMesh = new THREE.Mesh(new THREE.BoxGeometry(0, 0, 0), material);
printerPlate.material.side = THREE.DoubleSide;
scene.add(printerPlate);
scene.add(axes);

const renderer = new THREE.WebGLRenderer( { antialias: true } );
renderer.setSize( width, height );
renderer.setClearColor(0x212529, 0);

stlViewWrapper.appendChild( renderer.domElement );

const controls = new ArcballControls(camera, renderer.domElement, scene);
controls.target.set(0, 0, 0);
controls.setGizmosVisible(false);
controls.addEventListener('change', () => {
  renderer.render(scene, camera);
});
controls.enablePan = false;
controls.update();

renderer.render( scene, camera );
stlFileInput.addEventListener('change', event => {
  scene.remove(stlMesh);
  loader.load(URL.createObjectURL(event.target.files[0]), geometry => {
    stlMesh.geometry = geometry;
    stlMesh.geometry.center();
    const bbox = new THREE.Box3().setFromObject(stlMesh);
    const size = bbox.getSize(new THREE.Vector3());
    stlMesh.position.z = size.z / 2;
    scene.add(stlMesh);
    renderer.render(scene, camera);
  });
}, false);
