// load initial login code
chrome.storage.local.get(['login-code'], function (result) {
  console.log('Value currently is ' + result['login-code']);
  document.getElementById("login-code").value = result['login-code']
});

// load initial bot selection
chrome.storage.local.get(['button_id'], function (result) {
  console.log('bot currently is ' + result['button_id']);
  document.getElementById(result['button_id']).checked = true;
});

// save login code
document.getElementById("login-btn").onclick = async () => {
  code = document.getElementById("login-code").value
  chrome.storage.local.set({ 'login-code': code }, function () {
    console.log('Code is set to ' + code);
  });
}

const buttons = document.getElementsByName("bot")// .querySelectorAll("input[type='radio']");

// save bot selection
buttons.forEach(button => {
  button.onclick = () => {
    if (button.checked) {
      // alert(button.value + " selected as contact option!");
      selected = document.querySelector('input[name="bot"]:checked')
      bot_path = button.value
      button_id = button.id

      chrome.storage.local.set({ 'bot_path': bot_path }, function () {
        console.log('bot_path is set to ' + bot_path);
      });

      chrome.storage.local.set({ 'button_id': button_id }, function () {
        console.log('button_id is set to ' + button_id);
      });

    }

  }
})


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
    // let site = document.querySelector('input[name="bot"]:checked').value;

    // print(site)

    chrome.storage.local.get(['login-code', 'bot_path'], function (login_result) {
      fetch(login_result['bot_path'], {
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
