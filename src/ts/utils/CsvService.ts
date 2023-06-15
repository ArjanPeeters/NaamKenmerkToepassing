import EventDelegation from '@jjwesterkamp/event-delegation';

export class CsvService {

    constructor() {
        EventDelegation
            .global()
            .events('click')
            .select('[data-action="csv:download"]')
            .listen((event) => {
                const targetElement = event.delegator as HTMLElement;
                const tableElement = document
                    .querySelector<HTMLTableElement>(targetElement.dataset.target);
                this.generateCsvForTable(tableElement, targetElement.dataset.filename)
            });
    }

    private generateCsvForTable(tableElement: HTMLTableElement, filename = 'Materiaalnamen.csv'): void {
        console.log('generate csv for table', tableElement);
        const csvData = this.generateData(tableElement);

        const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
    }

    private generateData(tableElement: HTMLTableElement) {
        let csvContent = [];
        let headerRow = [];
        tableElement.querySelectorAll<HTMLTableCellElement>('th').forEach((header) => {
            headerRow.push(`"${header.innerText.replace(/"/g, '""')}"`);
        });
        headerRow.pop();
        csvContent.push(headerRow.join(','));

        tableElement.querySelectorAll<HTMLTableRowElement>('tbody tr').forEach(row => {
            let rowData = [];
            row.querySelectorAll('td:not(:last-child)').forEach((cell: HTMLTableCellElement) => {
                rowData.push(`"${cell.innerText.replace(/"/g, '""')}"`);
            });
            csvContent.push(rowData.join(','));
        });

        return csvContent.join('\n');
    }
}
