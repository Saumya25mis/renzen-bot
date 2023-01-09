chrome.runtime.onInstalled.addListener(async () => {
  chrome.contextMenus.create({
    id: "forward_id",
    title: "send to renzen",
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

      // selected_bot = document.querySelector('input[name="bot"]:checked').id;

      let selected_bot = await chrome.storage.local.get(['button_id'])
      selected_bot = selected_bot['button_id']
      console.log('SELECTED: '+selected_bot)

      chrome.storage.local.get(['login-code-' + selected_bot, 'bot_path'], function (login_result) {

        console.log(login_result)

        fetch(login_result['bot_path'], {
          method: "POST",
          headers: {
            "Content-Type": "application/json;charset=utf-8",
          },
          body: JSON.stringify({
            "snippet": result,
            "login_code": login_result["login-code-" + selected_bot],
            "url": tab.url,
            "title": tab.title
          }),
        });
      });
    } catch (e) {
      console.log("ERROR "+ e)
      return; // ignoring an unsupported page like chrome://extensions
    }
  })();
});
