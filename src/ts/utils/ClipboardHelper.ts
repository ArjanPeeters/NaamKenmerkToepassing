import EventDelegation from '@jjwesterkamp/event-delegation';

export class ClipboardHelper {

    constructor() {
        EventDelegation
            .global()
            .events('click')
            .select('[data-copy-to-clipboard]')
            .listen((event) => this.copyToClipboard(event));
    }


    private async copyToClipboard(event): Promise<void> {
        const element = event.delegator;
        const selector: string = element.dataset.copyToClipboard;
        const value: string = selector ? document.querySelector(selector).textContent : element.value;
        const isHyperlink = element.tagName === 'A' && element.href !== '#';

        if (isHyperlink) {
            event.preventDefault();
        }

        // navigator.clipboard bestaat alleen in een secure context (https/localhost);
        // over http (bv. LAN-IP) valt-ie terug op de legacy execCommand-methode.
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(value);
            } else {
                this.legacyCopy(value);
            }
            console.debug(`Value '${value}' copied to clipboard`);
        } catch (error) {
            console.error('Error copying to clipboard:', error);
            alert('Failed to copy to clipboard. Please check your browser permissions or copy manually.');
        }

        if (isHyperlink) {
            location.href = element.href;
        }
    }

    private legacyCopy(value: string): void {
        const ta = document.createElement('textarea');
        ta.value = value;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
    }

}
