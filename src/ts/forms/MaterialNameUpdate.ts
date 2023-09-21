import {MaterialName} from "@app-interfaces";

export class MaterialNameUpdate {
    private materialFormElement: HTMLFormElement;
    private materialNameElement: HTMLElement;
    private kenmerkSelectionElement: HTMLSelectElement;
    private toepassingSelectionElement: HTMLSelectElement;
    private naamSelectionElement: HTMLSelectElement;

    constructor() {
        this.materialFormElement = document.querySelector('#material_form');
        this.materialNameElement = document.querySelector('#material');
        this.kenmerkSelectionElement = document.querySelector('.form-control.kenmerk');
        this.toepassingSelectionElement = document.querySelector('.form-control.toepassing');
        this.naamSelectionElement = document.querySelector('.form-control.naam');

        this.materialFormElement.addEventListener('change', () => this.render());
        this.naamSelectionElement.addEventListener('change', () => this.resetSelections());
    }

    private resetSelections(): void {
        // Reset the selection fields to their first option.
        this.kenmerkSelectionElement.selectedIndex = 0;
        this.toepassingSelectionElement.selectedIndex = 0;

        this.render();
    }

    private async getMaterialUpdate(): Promise<MaterialName> {

        let nlsfbElement = (<HTMLInputElement>document.querySelector('input[type="search"]'));
        if (nlsfbElement !== null) {
            nlsfbElement.disabled = false;
        }

        let formData = new FormData(this.materialFormElement);
        formData.delete('csrf_token')

        if (nlsfbElement !== null) {
            nlsfbElement.disabled = true;
        }

        let params = new URLSearchParams(formData as any);
        return await (await fetch(`/material?${params.toString()}`)).json();
    }

    private async renderMaterialName(): Promise<void> {
        try {
            const returnMaterial = await this.getMaterialUpdate();
            console.log(returnMaterial['material']);
            this.materialNameElement.innerText = returnMaterial['material'];

            // Assume the `material` in `returnMaterial` is the value of the option to be selected.

            if ('nlsfb' in returnMaterial) {
                let nlsfbElement = (<HTMLInputElement>document.querySelector('input[type="search"]'));
                if (nlsfbElement !== null) {
                    nlsfbElement.value = String(returnMaterial['nlsfb']);
                }
            }
        } catch (error) {
            console.error('Failed to update material name:', error);
        }
    }

    private async render(): Promise<void> {
        await this.renderMaterialName()
    }

}
