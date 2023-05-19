chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: 'extractData',
        title: 'OCRもする！ 選択範囲をGPTで要約してDiscord',
        contexts: ['selection']
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'extractData') {
        chrome.tabs.sendMessage(tab.id, { command: 'extractData' });
    }
});
