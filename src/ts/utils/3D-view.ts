import * as THREE from 'three';
import * as OBC from 'openbim-components';

const container = document.getElementById('3d-view');

const components = new OBC.Components();
components.scene = new OBC.SimpleScene(components);
components.renderer = new OBC.SimpleRenderer(components, container);
components.camera = new OBC.SimpleCamera(components);
components.raycaster = new OBC.SimpleRaycaster(components);
components.init();

const scene = components.scene.get();
components.camera.controls.setLookAt(10, 10, 10, 0, 0, 0);
const grid = new OBC.SimpleGrid(components);
const boxMaterial = new THREE.MeshStandardMaterial({ color: '#6528D7' });
const boxGeometry = new THREE.BoxGeometry(3, 3, 3);
const cube = new THREE.Mesh(boxGeometry, boxMaterial);
cube.position.set(0, 1.5, 0);
scene.add(cube);

components.scene.setup();