# Canvas Submission Time Scraper

Canvas is kind of clunky when it comes to exporting data. Furthermore, many profs like to give grace days / hours / minutes (because they're nice people unlike me) even after submissions are due. Then, they'll have to manually mark submissions as "on-time" even though Canvas marks them late.

Canvas **currently does not export student assignment submission times**. That can be annoying for classes / professors / TAs that work on a grace day system (like mine). Wouldn't it be nice to export each student's submission time as a CSV file for a given assignment?

This is what we do.

## Quick Start

### Installation

To install this **Chrome Extension**

- Download this entire repo as a `.zip` and unpack it
- Go to `chrome://extensions` on Chrome
- Check `Developer Mode`
- Click on `Load unpacked extension...` and select the folder for the repo
- Green panda should appear and you can use it as described above.

### Usage

Navigate to **Speed Grader** for the homework you'd like to export.

That is, go to **Assignments** on the side bar.

![Assignments](./screenshots/screenshot_1.png)

Click on the homework you'd want to export.

![Select homework](./screenshots/screenshot_2.png)

Click on **Speed Grader** and allow the page to load.

![Speed Grader](./screenshots/screenshot_3.png)

Now click on the green panda and wait. **Chrome may tell you that the page has frozen and tell you that you should kill it. Don't. It is simply clicking through all (possibly hundreds) of students to get their submission times**.

![Speed Grader](./screenshots/screenshot_4.png)

A "save as" dialog will pop up asking you to download `submission_times.csv`. Download `submission_times.csv` and profit.

Unfortunately, we are not able to cross reference UNIs from student names and student IDs because Canvas. You'll have to cross reference them on your own from gradebook exports. That's trivial using either spreadsheet functions (`VLOOKUP`) or a simple script.
