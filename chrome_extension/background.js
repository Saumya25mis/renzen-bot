chrome.runtime.onInstalled.addListener(async () => {
  chrome.contextMenus.create({
    id: "forward_id",
    title: "send to discord",
    type: "normal",
    contexts: ["selection"],
  });
});

chrome.contextMenus.onClicked.addListener((item, tab) => {
  (async () => {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });
    let result;
    try {
      [{ result }] = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => getSelection().toString(),
      });

      console.log(tab.title)

      //let site = document.querySelector('input[name="bot"]:checked').value;

      // print(site)
      // // let site = "http://api.renzen.io/forward";
      // let site = `http://localhost:81/forward`

      chrome.storage.local.get(['login-code', 'bot_path'], function (login_result) {
        fetch(login_result['bot_path'], {
          method: "POST",
          headers: {
            "Content-Type": "application/json;charset=utf-8",
          },
          body: JSON.stringify({
            "snippet": result,
            "login-code": login_result["login-code"],
            "URL": tab.url,
            "title": tab.title
          }),
        });
      });
    } catch (e) {
      return; // ignoring an unsupported page like chrome://extensions
    }
  })();
});
