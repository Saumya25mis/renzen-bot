document.getElementById("save-btn").onclick = async () => {
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    let result;
    try {
      [{result}] = await chrome.scripting.executeScript({
        target: {tabId: tab.id},
        function: () => getSelection().toString(),
      });

      fetch('http://myLoadBalancerSite-2024255806.us-west-1.elb.amazonaws.com/forward').then(r => r.text()).then(result2 => {
        // Result now contains the response text, do what you want...
        document.body.append(result2);
    })

    } catch (e) {
      return; // ignoring an unsupported page like chrome://extensions
    }
    document.body.append('Selection: ' + result);
  };