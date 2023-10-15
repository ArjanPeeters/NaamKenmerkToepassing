import * as THREE from 'three';

import { Components } from 'openbim-components/core/Components';
import { SimpleCamera } from 'openbim-components/core/SimpleCamera';
import { SimpleGrid } from 'openbim-components/core/SimpleGrid';
import { SimpleRaycaster } from 'openbim-components/core/SimpleRaycaster';
import { SimpleRenderer } from 'openbim-components/core/SimpleRenderer';
import { SimpleScene } from 'openbim-components/core/SimpleScene';
import { FragmentManager } from 'openbim-components/fragments/FragmentManager';
import { FragmentIfcLoader } from 'openbim-components/fragments/FragmentIfcLoader';

export class IfcViewer {

    private canvasElement: HTMLElement;
    private materialsListElement: HTMLElement;
    private uploadInputElement: HTMLInputElement;

    private components: Components;
    private scene: THREE.Scene;
    private model: any;

    private fragmentManager: FragmentManager;
    private fragmentIfcLoader: FragmentIfcLoader;

    constructor(
        private element: HTMLElement,
        private options: any, // TODO: define options interface if needed
    ) {
        if (! this.element) {
            console.error('No element provided');
            return;
        }

        this.initializeElements();
        this.initializeComponents();
        this.initializeScene();
    }

    public async loadIfcFile(file: File): Promise<void> {
        this.clearScene();

        const data = await file.arrayBuffer();
        const buffer = new Uint8Array(data);
        this.model = await this.fragmentIfcLoader.load(buffer, file.name);

        this.scene.add(this.model);
    }

    public clearScene(): void {
        this.model?.removeFromParent();
        this.fragmentManager?.reset();
    }

    private initializeElements(): void {
        this.canvasElement = this.element.querySelector('.ifc-viewer-canvas');
        this.materialsListElement = this.element.querySelector('.ifc-viewer-materials-list');
        this.uploadInputElement = this.element.querySelector('.ifc-viewer-upload-input');

        this.uploadInputElement.addEventListener('change', (event) => {
            const file = (event.target as HTMLInputElement).files[0];
            this.loadIfcFile(file);
        });
    }

    private initializeComponents(): void {
        this.components = new Components();
        this.components.scene = new SimpleScene(this.components);
        this.components.renderer = new SimpleRenderer(this.components, this.canvasElement);
        this.components.camera = new SimpleCamera(this.components);
        this.components.raycaster = new SimpleRaycaster(this.components);
        this.components.init();

        this.fragmentManager = new FragmentManager(this.components);
        this.fragmentIfcLoader = new FragmentIfcLoader(this.components);

        this.fragmentIfcLoader.settings.wasm = {
            path: 'https://unpkg.com/web-ifc@0.0.43/',
            absolute: true,
        }

        this.fragmentIfcLoader.settings.webIfc.COORDINATE_TO_ORIGIN = true;
        this.fragmentIfcLoader.settings.webIfc.OPTIMIZE_PROFILES = true;
    }

    private initializeScene(): void {
        this.scene = this.components.scene.get();
        (this.components.camera as THREE.camera).controls.setLookAt(10, 10, 10, 0, 0, 0);

        const grid = new SimpleGrid(this.components);

        const boxMaterial = new THREE.MeshStandardMaterial({ color: '#6528D7' });
        const boxGeometry = new THREE.BoxGeometry(3, 3, 3);
        this.model = new THREE.Mesh(boxGeometry, boxMaterial);
        this.model.position.set(0, 1.5, 0);
        this.scene.add(this.model);

        (this.components.scene as THREE.scene).setup();
    }

}
