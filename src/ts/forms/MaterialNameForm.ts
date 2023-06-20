import { Kenmerk, MaterialLists, Toepassing ,DropdownInformation, DropdownListItem } from '@app-interfaces';

export class MaterialNameForm {

    private naamSelectElement: HTMLSelectElement;
    private kenmerkSelectElement: HTMLSelectElement;
    private toepassingSelectElement: HTMLSelectElement;
    private extraFieldGroupElements: NodeListOf<HTMLDivElement>;

    constructor() {
        this.naamSelectElement = document.querySelector('#naam_selection');
        this.kenmerkSelectElement = document.querySelector('#kenmerk_selection');
        this.toepassingSelectElement = document.querySelector('#toepassing_selection');
        this.extraFieldGroupElements = document.querySelectorAll('.material_form_extra_field_group');

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
        const options: DropdownListItem[] = dropdownInformation['drop-items'];

        this.extraFieldGroupElements.forEach((extraFieldGroupElement: HTMLDivElement) => {
            const dropdownElement = extraFieldGroupElement.querySelector('.dropdown-menu');
            const groupId = extraFieldGroupElement.dataset.groupId;
            let dropdownHtml = '';

            options.forEach((option: DropdownListItem) => {
                if (option.type === 'dropdown-header') {
                    dropdownHtml += `
                                    <li><hr class="dropdown-divider"></li>
                                    <li><div class="dropdown-header">${option.omschrijving}</div></li>
                                    `;
                } else {
                    dropdownHtml += `
                        <li>
                            <a class="dropdown-item"
                               href="/change_field/${groupId}/${option.type}"
                            >
                                ${option.omschrijving}
                            </a>
                        </li>
                    `;
                }
            });

            dropdownElement.innerHTML = dropdownHtml;
        });
    }

    private async render(): Promise<void> {
        await this.renderKenmerkenAndToepassingenOptions();
        await this.renderExtraFieldGroupOptions();
    }

}
