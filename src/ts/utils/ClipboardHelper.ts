import EventDelegation from '@jjwesterkamp/event-delegation';

export class ClipboardHelper {

    constructor() {
        EventDelegation
            .global()
            .events('click')
            .select('[data-copy-to-clipboard]')
            .listen((event) => this.copyToClipboard(event));
    }

    private async copyToClipboard(event: any): Promise<void> {
        const element = event.delegator;
        const selector: string = element.dataset.copyToClipboard;
        const value: string = selector ? document.querySelector(selector).textContent : element.value;
        const isHyperlink = element.tagName === 'A' && element.href !== '#';

        if (isHyperlink) {
            event.preventDefault();
        }

        try {
            await navigator.clipboard.writeText(value);
        } catch (error) {
            // @ts-ignore (legacy API)
            navigator.permissions.query({ name: 'clipboard-write' }).then((result) => {
                if (result.state === 'granted' || result.state === 'prompt') {
                    navigator.clipboard.writeText(value);
                } else {
                    alert('Failed to copy to clipboard. Please check your browser permissions or copy manually.');
                }
            });

            if (isHyperlink) {
                location.href = element.href;
            }

        }

    }
}
