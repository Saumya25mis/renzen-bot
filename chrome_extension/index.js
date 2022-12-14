const codes = ["login-code-production", "login-code-staging", "login-code-local"]
const buttons = document.getElementsByName("bot")

// load saved login codes
codes.forEach(code_name => {
  chrome.storage.local.get([code_name], function (result) {
    console.log(code_name + ' Value currently is ' + result[code_name]);
    document.getElementById(code_name).value = result[code_name]
  })
})

// load saved bot selection
chrome.storage.local.get(['button_id'], function (result) {
  console.log('bot currently is ' + result['button_id']);
  document.getElementById(result['button_id']).checked = true;
});

// save login codes on
document.getElementById("login-btn").onclick = async () => {
  codes.forEach(code_name => {
    code_value = document.getElementById(code_name).value
    console.log(code_name)
    console.log(code_value)
    chrome.storage.local.set({ [code_name]: code_value }).then(() => {
      console.log(code_name + ' Code is set to ' + code_value);
    });
  })
}

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
