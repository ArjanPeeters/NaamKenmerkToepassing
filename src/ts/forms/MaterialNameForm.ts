import { Kenmerk, MaterialLists, Toepassing } from '@app-interfaces';

export class MaterialNameForm {

    private naamSelectElement: HTMLSelectElement;
    private kenmerkSelectElement: HTMLSelectElement;
    private toepassingSelectElement: HTMLSelectElement;

    constructor() {
        this.naamSelectElement = document.querySelector('#naam_selection');
        this.kenmerkSelectElement = document.querySelector('#kenmerk_selection');
        this.toepassingSelectElement = document.querySelector('#toepassing_selection')

        this.naamSelectElement.addEventListener('change', () => this.renderKenmerkenAndToepassingenOptions());
    }

    private async getMaterialLists(naam: string): Promise<MaterialLists> {
        return await (await fetch(`/naam/${naam}`)).json();
    }

    private async renderKenmerkenAndToepassingenOptions(): Promise<void> {
        const materialLists = await this.getMaterialLists(this.naamSelectElement.value);

        let kenmerkHTML = '';
        let toepassingHTML = '';

        materialLists.kenmerken.forEach((option: Kenmerk) => {
            kenmerkHTML += `<option value="${option.id}">${option.kenmerk}</option>`;
        });

        materialLists.toepassingen.forEach((option: Toepassing) => {
            toepassingHTML += `<option value="${option.id}">${option.toepassing}</option>`;
        });

        this.kenmerkSelectElement.innerHTML = kenmerkHTML;
        this.toepassingSelectElement.innerHTML = toepassingHTML;
    }
}
