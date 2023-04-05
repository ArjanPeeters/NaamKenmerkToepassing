function copyToClipboard() {
    const textbox = document.querySelector('.form-control');
    textbox.select();
    document.execCommand('copy');
    alert('Text copied to clipboard!');
}