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
        let formData = new FormData(this.materialFormElement);
        formData.delete('csrf_token')
        let params = new URLSearchParams(formData as any);

        return await (await fetch(`/material?${params.toString()}`)).json();
    }

    private async renderMaterialName(): Promise<void> {
        const test = await this.getMaterialUpdate()
        console.log(test['material'])
        this.materialNameElement.innerText = test['material']
    }

    private async render(): Promise<void> {
        await this.renderMaterialName()
    }

}
