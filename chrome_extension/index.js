chrome.storage.local.get(['login-code'], function(result) {
  console.log('Value currently is ' + result.key);
  document.getElementById("login-code").value = result['login-code']
});

document.getElementById("save-btn").onclick = async () => {
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    let result;
    try {
      [{result}] = await chrome.scripting.executeScript({
        target: {tabId: tab.id},
        function: () => getSelection().toString(),
      });

      let site = "http://api.renzen.io/forward"

      chrome.storage.sync.get(['login-code'], function(login_result) {
        // console.log('Value currently is ' + result.key);
        fetch(site, {method: 'POST',   headers: {
        // fetch('http://myLoadBalancerSite-2024255806.us-west-1.elb.amazonaws.com/forward', {method: 'POST',   headers: {
          'Content-Type': 'application/json;charset=utf-8'
        }, body: JSON.stringify({"snippet":result, "login-code": login_result['login-code'], "URL": tab.url, })}).then(r => r.text()).then(result2 => {
          // Result now contains the response text, do what you want...
          document.body.append(result2);
      })
      });

    //   fetch('http://myLoadBalancerSite-2024255806.us-west-1.elb.amazonaws.com/forward', {method: 'POST',   headers: {
    //     'Content-Type': 'application/json;charset=utf-8'
    //   }, body: JSON.stringify({"snippet":result, "URL": tab.url})}).then(r => r.text()).then(result2 => {
    //     // Result now contains the response text, do what you want...
    //     document.body.append(result2);
    // })

    } catch (e) {
      return; // ignoring an unsupported page like chrome://extensions
    }
    document.body.append('Selection: ' + result);
  };

document.getElementById("login-btn").onclick = async () => {

  code = document.getElementById("login-code").value

  chrome.storage.local.set({'login-code': code}, function() {
    console.log('Value is set to ' + code);
  });
}

//https://developer.chrome.com/docs/extensions/reference/storage/#type-StorageArea
//
// chrome.storage.sync.set({key: value}, function() {
//   console.log('Value is set to ' + value);
// });

// chrome.storage.sync.get(['key'], function(result) {
//   console.log('Value currently is ' + result.key);
// });