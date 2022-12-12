chrome.storage.local.get(['login-code'], function (result) {
  console.log('Value currently is ' + result['login-code']);
  document.getElementById("login-code").value = result['login-code']
});

document.getElementById("save-btn").onclick = async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  let result;
  try {
    [{ result }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: () => getSelection().toString(),
    });

    // let subdomain = document.getElementById('subdomain').value;
    // let site = `http://${subdomain}.renzen.io/forward`

    // let subdomain = document.getElementById('subdomain').value;
    let site = `http://localhost:81/forward`

    chrome.storage.local.get(['login-code'], function (login_result) {
      fetch(site, {
        method: 'POST', headers: {
          'Content-Type': 'application/json;charset=utf-8'
        }, body: JSON.stringify({ "snippet": result, "login-code": login_result['login-code'], "URL": tab.url, })
      }).then(r => r.text()).then(result2 => {
        // Result now contains the response text, do what you want...
        document.body.append(result2);
      })
    });

  } catch (e) {
    return; // ignoring an unsupported page like chrome://extensions
  }
  document.body.append('Selection: ' + result);
};

document.getElementById("login-btn").onclick = async () => {

  code = document.getElementById("login-code").value

  chrome.storage.local.set({ 'login-code': code }, function () {
    console.log('Value is set to ' + code);
  });
}
