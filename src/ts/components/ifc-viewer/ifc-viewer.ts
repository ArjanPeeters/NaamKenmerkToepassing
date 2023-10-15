import * as THREE from 'three';

import { Components } from 'openbim-components/core/Components';
import { SimpleCamera } from 'openbim-components/core/SimpleCamera';
import { SimpleGrid } from 'openbim-components/core/SimpleGrid';
import { SimpleRaycaster } from 'openbim-components/core/SimpleRaycaster';
import { SimpleRenderer } from 'openbim-components/core/SimpleRenderer';
import { SimpleScene } from 'openbim-components/core/SimpleScene';

export class IfcViewer {

    private components: Components;
    private scene: THREE.Scene;

    constructor(
        private element: HTMLElement,
        private options: any, // TODO: define options interface if needed
    ) {
        if (! this.element) {
            console.error('No element provided');
            return;
        }

        this.initializeComponents();
        this.initializeScene();
    }

    private initializeComponents() {
        this.components = new Components();
        this.components.scene = new SimpleScene(this.components);
        this.components.renderer = new SimpleRenderer(this.components, this.element);
        this.components.camera = new SimpleCamera(this.components);
        this.components.raycaster = new SimpleRaycaster(this.components);
        this.components.init();
    }

    private initializeScene(): void {
        this.scene = this.components.scene.get();
        (this.components.camera as THREE.camera).controls.setLookAt(10, 10, 10, 0, 0, 0);

        const grid = new SimpleGrid(this.components);

        const boxMaterial = new THREE.MeshStandardMaterial({ color: '#6528D7' });
        const boxGeometry = new THREE.BoxGeometry(3, 3, 3);
        const cube = new THREE.Mesh(boxGeometry, boxMaterial);
        cube.position.set(0, 1.5, 0);
        this.scene.add(cube);

        (this.components.scene as THREE.scene).setup();
    }

}
