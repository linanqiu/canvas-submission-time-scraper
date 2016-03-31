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
    var outputString = [];
    outputString.push('studentName,studentId,submissionTime');
    for (var studentName in request.data) {
      outputString.push(studentName + ',' + request.data[studentName].studentId + ',' + request.data[studentName].submissionTime);
    }
    outputString = outputString.join('\n');
    var doc = URL.createObjectURL(new Blob([outputString], {
      type: 'application/text/plain'
    }));
    chrome.downloads.download({
      url: doc,
      filename: 'submission_times.csv',
      conflictAction: 'overwrite',
      saveAs: true
    });
  }
});
