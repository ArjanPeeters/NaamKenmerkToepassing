function copyToClipboard(elementToCopy) {
    navigator.clipboard.writeText(elementToCopy.value)
    console.log(elementToCopy.value + " copied to Clipboard")
}

