import '@app-styles/main.scss';

import { ClipboardHelper, CsvService } from '@app-utils';

// ---- data shapes (see dump_json.py) ----
interface NaamEntry {
    naam: string;
    kenmerken: string[];
    toepassingen: string[];
    extra_lijsten: Record<string, string[]>; // soort -> [omschrijving, ...]
}
interface RalEntry { nummer: string; omschrijving: string; r: number; g: number; b: number; }
interface Data { namen: NaamEntry[]; ral: RalEntry[]; nlsfb: Record<string, string>; }

interface ExtraField { id: number; type: string; value: string; }

interface DropItem { type: string; omschrijving: string; }

const LS_KEY = 'naakt_saved';
const NLSFB_EMPTY = '[geen code]';

function esc(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

class App {
    private data!: Data;
    private naam = '';
    private kenmerk = '';
    private toepassing = '';
    private extras: ExtraField[] = [];
    private saved: string[] = [];

    async init(): Promise<void> {
        this.data = await (await fetch('static/data.json')).json();
        try { this.saved = JSON.parse(localStorage.getItem(LS_KEY) || '[]'); } catch { this.saved = []; }

        const first = this.data.namen[0];
        this.naam = first.naam;
        this.kenmerk = first.kenmerken[0] ?? '';
        this.toepassing = first.toepassingen[0] ?? '';

        this.wire();
        this.render();
    }

    // ---- helpers ----
    private entry(): NaamEntry {
        return this.data.namen.find((n) => n.naam === this.naam)!;
    }

    private nlsfbFor(): string {
        return this.data.nlsfb[`${this.naam}_${this.kenmerk}`] ?? NLSFB_EMPTY;
    }

    private clean(v: string): string {
        return v.replace(/\./g, '').replace(/ /g, '-').toLowerCase();
    }

    private materialName(): string {
        let s = `${this.naam}_${this.kenmerk}_${this.toepassing}`;
        for (const f of this.extras) {
            const c = this.clean(f.value);
            if (c !== '' && c !== '[geen-code]') s += `_${c}`;
        }
        return s;
    }

    private dropItems(): DropItem[] {
        const items: DropItem[] = [
            { type: 'input', omschrijving: 'Vrij invulveld' },
            { type: 'nlsfb', omschrijving: 'NL-SfB' },
            { type: 'select_ral', omschrijving: 'RAL kleur' },
        ];
        const e = this.entry();
        const soorten = Object.keys(e.extra_lijsten);
        if (soorten.length) {
            items.push({ type: 'dropdown-header', omschrijving: e.naam });
            for (const soort of soorten) items.push({ type: `select_${e.naam}_${soort}`, omschrijving: soort });
        }
        return items;
    }

    private selectList(type: string): string[] {
        if (type === 'select_ral') return this.data.ral.map((r) => r.nummer);
        const e = this.entry();
        const rest = type.slice('select_'.length);
        if (rest.startsWith(`${e.naam}_`)) return e.extra_lijsten[rest.slice(e.naam.length + 1)] ?? [];
        return [];
    }

    private omschrijvingFor(type: string): string {
        return this.dropItems().find((d) => d.type === type)?.omschrijving ?? type;
    }

    private usedTypes(exceptId: number): Set<string> {
        const s = new Set<string>();
        for (const f of this.extras) if (f.id !== exceptId && f.type !== 'input') s.add(f.type);
        return s;
    }

    // ---- state changes ----
    private onNaamChange(naam: string): void {
        this.naam = naam;
        const e = this.entry();
        this.kenmerk = e.kenmerken[0] ?? '';
        this.toepassing = e.toepassingen[0] ?? '';
        for (const f of this.extras) {
            if (f.type === 'nlsfb') f.value = this.nlsfbFor();
            else if (f.type.startsWith('select_') && f.type !== 'select_ral' && this.selectList(f.type).length === 0) {
                f.type = 'input'; f.value = '';
            }
        }
        this.render();
    }

    private setFieldType(id: number, type: string): void {
        const f = this.extras.find((e) => e.id === id);
        if (!f) return;
        f.type = type;
        if (type === 'nlsfb') f.value = this.nlsfbFor();
        else if (type.startsWith('select_')) f.value = this.selectList(type)[0] ?? '';
        else f.value = '';
        this.render();
    }

    private addField(): void {
        const id = this.extras.length ? Math.max(...this.extras.map((f) => f.id)) + 1 : 1;
        this.extras.push({ id, type: 'input', value: '' });
        this.render();
    }

    private save(): void {
        const name = this.materialName();
        if (!this.saved.includes(name)) {
            this.saved.unshift(name);
            localStorage.setItem(LS_KEY, JSON.stringify(this.saved));
        }
        this.render();
    }

    // ---- rendering ----
    private render(): void {
        // >4 velden totaal (3 basis + extras) -> vaste kolombreedte i.p.v. uitrekken
        document.querySelector('#material_form')!.classList.toggle('fixed-cols', this.extras.length > 1);
        (document.querySelector('#material') as HTMLElement).textContent = this.materialName();
        this.renderSelect('#naam_selection', this.data.namen.map((n) => n.naam), this.naam);
        this.renderSelect('#kenmerk_selection', this.entry().kenmerken, this.kenmerk);
        this.renderSelect('#toepassing_selection', this.entry().toepassingen, this.toepassing);
        this.renderExtras();
        this.renderSaved();
    }

    private renderSelect(sel: string, options: string[], value: string): void {
        const el = document.querySelector<HTMLSelectElement>(sel)!;
        el.innerHTML = options.map((o) => `<option value="${esc(o)}"${o === value ? ' selected' : ''}>${esc(o)}</option>`).join('');
        el.value = value;
    }

    private renderExtras(): void {
        const form = document.querySelector('#material_form')!;
        form.querySelectorAll('.material_form_extra_field_group').forEach((e) => e.remove());
        const used = (id: number) => this.usedTypes(id);
        const html = this.extras.map((f) => {
            const usedSet = used(f.id);
            const menu = this.dropItems().map((item) => {
                if (item.type === 'dropdown-header') {
                    return `<li><hr class="dropdown-divider"></li><li><div class="dropdown-header">${esc(item.omschrijving)}</div></li>`;
                }
                const disabled = usedSet.has(item.type) ? ' disabled' : '';
                return `<li><a class="dropdown-item${disabled}" href="#" data-set-type="${esc(item.type)}" data-field-id="${f.id}">${esc(item.omschrijving)}</a></li>`;
            }).join('');

            let control: string;
            if (f.type === 'nlsfb') {
                control = `<input type="search" class="form-control" value="${esc(f.value)}" data-field-id="${f.id}" disabled>`;
            } else if (f.type.startsWith('select_')) {
                const opts = this.selectList(f.type).map((o) => `<option${o === f.value ? ' selected' : ''}>${esc(o)}</option>`).join('');
                control = `<select class="form-select form-control" data-field-id="${f.id}">${opts}</select>`;
            } else {
                control = `<input type="text" class="form-control" value="${esc(f.value)}" data-field-id="${f.id}">`;
            }

            return `
                <div class="field-col material_form_extra_field_group" data-group-id="${f.id}">
                    <div class="input-group">
                        <label class="input-group-text text-secondary-emphasis">${esc(this.omschrijvingFor(f.type))}</label>
                        <button type="button" class="btn btn-outline-secondary dropdown-toggle text-secondary-emphasis extra-dropdown dropdown-toggle-split" data-bs-toggle="dropdown" aria-expanded="false">
                            <span class="visually-hidden">Toggle Dropdown</span>
                        </button>
                        <ul class="dropdown-menu">${menu}</ul>
                        ${control}
                        <button class="btn btn-outline-secondary" type="button" data-remove-field="${f.id}">-</button>
                    </div>
                </div>`;
        }).join('');

        const tmp = document.createElement('div');
        tmp.innerHTML = html;
        while (tmp.firstElementChild) form.appendChild(tmp.firstElementChild);
    }

    private renderSaved(): void {
        const container = document.querySelector('#saved_list')!;
        if (!this.saved.length) { container.innerHTML = ''; return; }

        const rows = this.saved.map((name, i) => `
            <tr>
                <td class="col text-center align-middle">${this.saved.length - i}</td>
                <td class="col text-center align-middle">${esc(name)}</td>
                <td class="col text-center align-middle">
                    <div class="d-flex justify-content-center align-items-center">
                        <a href="#" title="Delete" class="text-dark-emphasis" data-del-index="${i}"><i class="fa-regular fa-trash-can"></i></a>
                        <button class="btn text-dark-emphasis" title="Copy-to-Clipboard" value="${esc(name)}" data-copy-to-clipboard><i class="fa-regular fa-clipboard"></i></button>
                    </div>
                </td>
            </tr>`).join('');

        container.innerHTML = `
            <div class="container my-5">
                <div class="p-5 text-center bg-body-tertiary rounded-3">
                    <div class="d-inline-flex gap-4 text-center mb-5">
                        <button class="btn btn-outline-light" data-action="csv:download" data-target=".material-list">
                            <span class="fa fa-download"></span> Download as CSV
                        </button>
                        <a href="#" class="btn btn-outline-secondary" data-del-list>Delete list</a>
                    </div>
                    <div class="container-lg">
                        <div class="table-responsive">
                            <table class="table material-list">
                                <thead><tr><th class="col">Rij</th><th class="col">Materiaal naam</th><th class="col">Acties</th></tr></thead>
                                <tbody>${rows}</tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>`;
    }

    // ---- events (delegated, survive innerHTML rebuilds) ----
    private wire(): void {
        document.addEventListener('change', (ev) => {
            const t = ev.target as HTMLElement;
            if (t.id === 'naam_selection') this.onNaamChange((t as HTMLSelectElement).value);
            else if (t.id === 'kenmerk_selection') { this.kenmerk = (t as HTMLSelectElement).value; this.syncNlsfb(); this.render(); }
            else if (t.id === 'toepassing_selection') { this.toepassing = (t as HTMLSelectElement).value; this.render(); }
            else if ((t as HTMLElement).dataset.fieldId) {
                const f = this.extras.find((x) => x.id === +(t as HTMLElement).dataset.fieldId!);
                if (f) { f.value = (t as HTMLInputElement | HTMLSelectElement).value; this.render(); }
            }
        });

        document.addEventListener('click', (ev) => {
            const el = (ev.target as HTMLElement).closest<HTMLElement>(
                '[data-set-type],[data-remove-field],[data-add-field],[data-save],[data-del-list],[data-del-index]');
            if (!el) return;
            const d = el.dataset;
            if (d.setType !== undefined) { ev.preventDefault(); if (!el.classList.contains('disabled')) this.setFieldType(+d.fieldId!, d.setType); }
            else if (d.removeField !== undefined) { ev.preventDefault(); this.extras = this.extras.filter((f) => f.id !== +d.removeField!); this.render(); }
            else if (d.addField !== undefined) { ev.preventDefault(); this.addField(); }
            else if (d.save !== undefined) { this.save(); } // no preventDefault: ClipboardHelper still copies
            else if (d.delList !== undefined) { ev.preventDefault(); this.saved = []; localStorage.removeItem(LS_KEY); this.render(); }
            else if (d.delIndex !== undefined) { ev.preventDefault(); this.saved.splice(+d.delIndex, 1); localStorage.setItem(LS_KEY, JSON.stringify(this.saved)); this.render(); }
        });
    }

    private syncNlsfb(): void {
        for (const f of this.extras) if (f.type === 'nlsfb') f.value = this.nlsfbFor();
    }
}

new ClipboardHelper();
new CsvService();
new App().init();
