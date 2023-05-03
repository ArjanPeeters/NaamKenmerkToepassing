function copyToClipboard(elementToCopy) {
    navigator.clipboard.writeText(elementToCopy.value)
    console.log(elementToCopy.value + " copied to Clipboard")
}

function copyToClipboardMaterial(){
    let textToCopy = document.getElementById("material").innerText
    navigator.clipboard.writeText(textToCopy)
    console.log(textToCopy + " copied to Clipboard")
}

document.getElementById('save_button').addEventListener(
    "click", navigator.clipboard.writeText(
        document.getElementById("material"
        ).innerText
    )
)
