chrome.runtime.onMessage.addListener(
  function (request, sender, sendResponse) {
    if (request.message === "clicked_browser_action") {
      data = {};

      function domReady(studentName, cb) {
        if ($('#multiple_submissions').html().trim().length == 0 && $('#this_student_does_not_have_a_submission').html().trim().length == 0) {
          window.requestAnimationFrame(function () {
            domReady(studentName, cb);
          });
          return;
        }

        if ($('#gradebook_header > form > div.left > a.next').html().trim().length == 0) {
          window.requestAnimationFrame(function () {
            domReady(studentName, cb);
          });
          return;
        }

        if ($('#students_selectmenu-button > span.ui-selectmenu-status > span.ui-selectmenu-item-header').html() === undefined) {
          window.requestAnimationFrame(function () {
            domReady(studentName, cb);
          });
          return;
        }

        if ($('#students_selectmenu-button > span.ui-selectmenu-status > span.ui-selectmenu-item-header').text() === studentName) {
          window.requestAnimationFrame(function () {
            domReady(studentName, cb);
          });
          return;
        }

        cb();
      }

      function parseDateTime(dateTimeArray) {
        return dateTimeArray.map(function (dateTimeString) {
          return moment(dateTimeString, 'MMM D at h:ma');
        });
      }

      function scrape() {
        var submission;

        if ($('#this_student_does_not_have_a_submission').is(':visible')) {
          submission = 'No submission';
        } else {
          submission = $('#multiple_submissions').text().toLowerCase().replace('submitted:', '').trim().split('\n');
          if (submission.length > 1) {
            submission = $('#submission_to_view option').map(function () {
              return $(this).text().toLowerCase().replace('late', '').replace(/\(grade\: [0-9]+\)/g, '').trim();
            }).get();
          }
          submission = parseDateTime(submission);
          // get only latest submission time
          submission = submission.sort(function (a, b) {
            return new Date(b) - new Date(a);
          })[0];
        }


        var studentName = $('#students_selectmenu-button > span.ui-selectmenu-status > span.ui-selectmenu-item-header').text();
        var studentId = $('#avatar_image').attr('src').replace('/images/users/', '').split('-')[0].trim();

        if (!data.hasOwnProperty(studentName)) {
          data[studentName] = {
            submissionTime: submission,
            studentId: studentId
          };
          
          // click next
          document.querySelector('#gradebook_header > form > div.left > a.next').click();

          domReady(studentName, function () {
            scrape();
          });
        } else {
          chrome.runtime.sendMessage({
            data: data,
            request: 'download'
          }, function (response) {
            console.log('Downloaded');
          });
        }
      }

      domReady(null, function () {
        scrape();
      });
    }
  }
);
