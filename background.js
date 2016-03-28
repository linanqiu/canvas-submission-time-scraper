chrome.browserAction.onClicked.addListener(function (tab) {
  chrome.tabs.query({
    active: true,
    currentWindow: true
  }, function (tabs) {
    var activeTab = tabs[0];
    chrome.tabs.sendMessage(activeTab.id, {
      "message": "clicked_browser_action"
    });
  });
});

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.request === 'download') {
    var doc = URL.createObjectURL(new Blob([JSON.stringify(request.data, null, 2)], {
      type: 'application/text/plain'
    }));
    chrome.downloads.download({
      url: doc,
      filename: 'submission_times.txt',
      conflictAction: 'overwrite',
      saveAs: true
    });
  }
});
