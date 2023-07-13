import {MaterialName} from "@app-interfaces";

export class MaterialNameUpdate {

    private materialFormElement: HTMLFormElement;
    private materialNameElement: HTMLSelectElement;

    constructor() {
        this.materialFormElement = document.querySelector('#material_form')
        this.materialNameElement = document.querySelector('#material')

        this.materialFormElement.addEventListener('change', () => this.render());

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
        const returnMaterial = await this.getMaterialUpdate()
        console.log(returnMaterial['material'])
        this.materialNameElement.innerText = returnMaterial['material']
        if ('nlsfb' in returnMaterial) {
            // Assumes you have an element with type "search".
            let nlsfbElement = (<HTMLInputElement>document.querySelector('input[type="search"]'));
            if (nlsfbElement !== null) {
                nlsfbElement.value = String(returnMaterial['nlsfb']);
            }
        }
    }

    private async render(): Promise<void> {
        await this.renderMaterialName()
    }

}
