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

        try {
            await navigator.clipboard.writeText(value);
            console.debug(`Value '${value}' copied to clipboard`);
        } catch (error) {
            navigator.permissions.query({ name: "clipboard-write" as PermissionName}).then((result) => {
              if (result.state === "granted" || result.state === "prompt") {
                navigator.clipboard.writeText(value);
                console.debug(`Value '${value}' copied to clipboard`);
              } else {
                  console.error('Error copying to clipboard:', error);
                  alert('Failed to copy to clipboard. Please check your browser permissions or copy manually.');
              }
            });

        if (isHyperlink) {
            location.href = element.href;
        }

    }

}}
