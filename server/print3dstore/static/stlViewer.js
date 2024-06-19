import * as THREE from 'three';
import { ArcballControls } from 'three/addons/controls/ArcballControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

(() => {
  const stlFileInput = document.querySelector('#stl_models');
  const stlViewWrapper = document.querySelector('#stl-viewer');
  const stlAnchorLinks = document.querySelectorAll('.view-model');
  if (!stlViewWrapper) return;

  const loader = new STLLoader();
  const width = parseInt(stlViewWrapper.style.width);
  const height = parseInt(stlViewWrapper.style.height);
  
  
  const camera = new THREE.PerspectiveCamera(75, width / height, 0.01, 10000);
  camera.position.set(250, 250, 250);
  camera.lookAt(new THREE.Vector3(0, 0, 0));
  camera.up = new THREE.Vector3(-Math.cos(Math.PI / 2), -Math.cos(Math.PI / 2), 0);
  const scene = new THREE.Scene();
  
  
  // const geometry = new THREE.BoxGeometry( 0.5, 0.5, 0.5 );
  const material = new THREE.MeshNormalMaterial();
  const printableAreaMesh = new THREE.Mesh(
    new THREE.BoxGeometry(235, 235, 265)
  );
  printableAreaMesh.position.z = 132;
  const printableArea = new THREE.BoxHelper(
    printableAreaMesh,
    new THREE.Color(0xffffff)
  );
  const printerPlate = new THREE.Mesh(
    new THREE.PlaneGeometry(235, 235),
    new THREE.MeshBasicMaterial({ color: new THREE.Color(0xc4a161) })
  );
  const stlMesh = new THREE.Mesh(new THREE.BoxGeometry(0, 0, 0), material);
  printerPlate.material.side = THREE.DoubleSide;
  scene.add(printerPlate);
  scene.add(printableArea);
  
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(width, height);
  renderer.setClearColor(0x212529, 0);
  
  stlViewWrapper.appendChild(renderer.domElement);
  
  const controls = new ArcballControls(camera, renderer.domElement, scene);
  controls.target.set(0, 0, 132);
  controls.setGizmosVisible(false);
  controls.addEventListener('change', () => {
    renderer.render(scene, camera);
  });
  controls.enablePan = false;
  controls.update();
  
  renderer.render(scene, camera);
  if (stlFileInput) {
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
  }
  if (!!stlAnchorLinks.length) {
    stlAnchorLinks.forEach(anchor => {
      anchor.addEventListener('click', event => {
        event.preventDefault();
        loader.load(event.target.href, geometry => {
          stlMesh.geometry = geometry;
          stlMesh.geometry.center();
          const bbox = new THREE.Box3().setFromObject(stlMesh);
          const size = bbox.getSize(new THREE.Vector3());
          stlMesh.position.z = size.z / 2;
          scene.add(stlMesh);
          renderer.render(scene, camera);
        });
      })
    });
  }
})();
