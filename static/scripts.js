function copyToClipboard(textToCopy) {
    navigator.clipboard.writeText(textToCopy.value)
    console.log(textToCopy.value + " copied to Clipboard")
}