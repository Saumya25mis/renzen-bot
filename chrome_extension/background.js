chrome.runtime.onInstalled.addListener(async () => {
    chrome.contextMenus.create({
        id: "forward_id",
        title: "send to discord",
        type: 'normal',
        contexts: ['selection']
    })
})

// Open a new search tab when the user clicks a context menu
chrome.contextMenus.onClicked.addListener((item, tab) => {

    (async () => {

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    let result;
    try {
      [{ result }] = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => getSelection().toString(),
      });
  
      let site = "http://api.renzen.io/forward"
  
      chrome.storage.sync.get(['login-code'], function (login_result) {
        fetch(site, {
          method: 'POST', headers: {
            'Content-Type': 'application/json;charset=utf-8'
          }, body: JSON.stringify({ "snippet": result, "login-code": login_result['login-code'], "URL": tab.url, })
        })
        // .then(r => r.text()).then(result2 => {
        //   // Result now contains the response text, do what you want...
        // //   document.body.append(result2);
        // })
      });
  
    } catch (e) {
      return; // ignoring an unsupported page like chrome://extensions
    }

})()
    // const tld = item.menuItemId
    // let url = new URL(`https://google.${tld}/search`)
    // url.searchParams.set('q', item.selectionText)
    // chrome.tabs.create({ url: url.href, index: tab.index + 1 });
  });