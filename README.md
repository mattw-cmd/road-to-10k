# Road to 10k

Installable web app for Matt Wade's Instagram content system (@mattwade_____): calendar, post log, growth chart, pillar and hook performance, streak.

- All data is stored on the device (IndexedDB). Nothing is sent anywhere.
- **Sync** in the header exports a JSON snapshot and imports one back. The Sunday review reads the export from Google Drive and leaves an import file in the same folder.
- Built from `plan.json` + `template.html` with `pwa_build.py` in the PROJECT AUTOMATE session scratchpad.

Install: open the site on your phone, Share, Add to Home Screen.
