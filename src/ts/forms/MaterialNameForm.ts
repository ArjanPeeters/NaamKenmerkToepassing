import { Kenmerk, MaterialLists, Toepassing ,DropdownInformation, DropdownList } from '@app-interfaces';

export class MaterialNameForm {

    private naamSelectElement: HTMLSelectElement;
    private kenmerkSelectElement: HTMLSelectElement;
    private toepassingSelectElement: HTMLSelectElement;
    private extraFieldGroupElements: NodeListOf<HTMLDivElement>;

    // private dropdownElements: NodeListOf<HTMLOptionElement | HTMLOptGroupElement>;

    constructor() {
        this.naamSelectElement = document.querySelector('#naam_selection');
        this.kenmerkSelectElement = document.querySelector('#kenmerk_selection');
        this.toepassingSelectElement = document.querySelector('#toepassing_selection');
        this.extraFieldGroupElements = document.querySelectorAll('.material_form_extra_field_group');

        // this.dropdownElements = document.querySelectorAll('.dropdown-menu');

        this.naamSelectElement.addEventListener('change', () => this.render());
    }

    private async getMaterialLists(naam: string): Promise<MaterialLists> {
        return await (await fetch(`/naam/${naam}`)).json();
    }

    private async getCustomFieldList(naam: string): Promise<DropdownInformation> {
        return await (await fetch(`/get_dropdowns/${naam}`)).json();
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

    private async renderExtraFieldGroupOptions(): Promise<void> {
        const dropdownInformation = await this.getCustomFieldList(this.naamSelectElement.value);
        const items = dropdownInformation['drop-items'];

        console.log({ items });
        // this.extraFieldGroupElements.forEach((extraFieldGroupElement: HTMLDivElement) => {
        //     const dropdownElement = extraFieldGroupElement.querySelector('.dropdown-menu');
        //     const dropdownButtonElement = extraFieldGroupElement.querySelector('.dropdown-toggle');
        //
        //     dropdownInformation.list_items.forEach((item: DropdownList) => {
        //         dropdownElement.innerHTML += `<li><a class="dropdown-item {{ 'disabled' if menu_item_disabled else '' }}" href="/change_field/{{ extra.id }}/{{ short }}">{{ long }}</a></li>`;
        //     });
        //
        //     dropdownButtonElement.innerHTML = dropdownInformation.dropdown_name;
        // });
    }

    private async render(): Promise<void> {
        await this.renderKenmerkenAndToepassingenOptions();
        await this.renderExtraFieldGroupOptions();
    }

}
