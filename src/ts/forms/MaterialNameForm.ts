import { Kenmerk, MaterialLists, Toepassing ,DropdownInformation, DropdownList, ExtraField} from '@app-interfaces';

export class MaterialNameForm {

    private naamSelectElement: HTMLSelectElement;
    private kenmerkSelectElement: HTMLSelectElement;
    private toepassingSelectElement: HTMLSelectElement;
    private dropdownElements: NodeListOf<HTMLOptionElement | HTMLOptGroupElement>

    constructor() {
        this.naamSelectElement = document.querySelector('#naam_selection');
        this.kenmerkSelectElement = document.querySelector('#kenmerk_selection');
        this.toepassingSelectElement = document.querySelector('#toepassing_selection')
        this.dropdownElements = document.querySelectorAll('#dropdown-menu')

        this.naamSelectElement.addEventListener('change', () => this.renderKenmerkenAndToepassingenOptions());
    }

    private async getMaterialLists(naam: string): Promise<MaterialLists> {
        return await (await fetch(`/naam/${naam}`)).json();
    }

    private async  getDropdownLists(naam: string): Promise<DropdownInformation> {
        return await (await fetch(`/get_dropdowns/${naam}`)).json();
    }

    private async renderKenmerkenAndToepassingenOptions(): Promise<void> {
        const materialLists = await this.getMaterialLists(this.naamSelectElement.value);
        const dropdownInformation = await this.getDropdownLists(this.naamSelectElement.value);

        let kenmerkHTML = '';
        let toepassingHTML = '';
        let dropdownHTML = '';

        materialLists.kenmerken.forEach((option: Kenmerk) => {
            kenmerkHTML += `<option value="${option.id}">${option.kenmerk}</option>`;
        });

        materialLists.toepassingen.forEach((option: Toepassing) => {
            toepassingHTML += `<option value="${option.id}">${option.toepassing}</option>`;
        });

        dropdownInformation.list_items.forEach((item: DropdownList) => {
            console.log('List_items')
        });

        this.kenmerkSelectElement.innerHTML = kenmerkHTML;
        this.toepassingSelectElement.innerHTML = toepassingHTML;
    }
}
