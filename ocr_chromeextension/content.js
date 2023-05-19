function getSelectedTextAndImages() {
    const selection = window.getSelection();
    const range = selection.getRangeAt(0);
    const fragment = range.cloneContents();

    const rawText = selection.toString();
    const encodedText = btoa(unescape(encodeURIComponent(rawText))); // Base64 エンコーディング
    const images = fragment.querySelectorAll('img');
    const imageURLs = Array.from(images)
        .map(img => encodeURIComponent(img.src))
        .filter(url => !url.endsWith('svg'));

    return { text: encodedText, imageURLs };
}

function postToAPI(data) {
    const apiUrl = 'http://127.0.0.1:8000/with_ocr/';
    const payload = {
        text: data.text,
        imageURLs: data.imageURLs,
        pageURL: window.location.href
    };

    console.log('Sending data:', payload); // 追加

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.command === 'extractData') {
        const data = getSelectedTextAndImages();
        postToAPI(data);
    }
});
