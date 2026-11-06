# Local silent rehearsal

`evaluation/record_rehearsal.py` captures the reviewed product using the existing synthetic release, schematic map and deterministic suggested question. It blocks requests outside the two supplied loopback origins. It makes no model call and uploads nothing. This is a recording aid, not a narrated final submission video or proof of a live AI answer.

Keep the reviewed application at `2e8e023` for the recording freeze. Start the public planner and private operator locally following `demo/REHEARSAL.md`. Use a Python environment with Playwright, a Chromium browser and FFmpeg/ffprobe. Playwright must also have a compatible recording FFmpeg available. In Astra's environment, the installed system FFmpeg is exposed through `/tmp/routesafe-pw/ffmpeg-1011/ffmpeg-linux`; that temporary path is not portable.

```bash
PLAYWRIGHT_BROWSERS_PATH=/tmp/routesafe-pw python evaluation/record_rehearsal.py \
  --planner http://127.0.0.1:8791 --operator http://127.0.0.1:8792 \
  --output runtime/routesafe-silent-rehearsal-2e8e023-v3.webm \
  --receipt evidence/e6/silent-rehearsal-final.json --application-commit 2e8e023
```

Existing outputs are deliberately not overwritten. Supply new paths for another take. `--speed 10` is useful for checking transitions; only the default speed enforces the two-minute limit. The storyboard timestamps are compressed to 90% to allow initial navigation and encoder overhead. The receipt records scene times relative to the first loaded planner screen; video timestamps also include initial loading.

Before using this footage, watch the whole clip, add human-approved narration, and recheck the final edited duration. Say **suggested question/preset**, not live AI: the visible badge says AI offline. Say **synthetic data** and keep the utility failure and pending-review disclosures. The original 124.8-second take is retained locally as a failed timing attempt; use only a take with a passing receipt. Video files stay in ignored `runtime/`; nothing has been uploaded or submitted.

Verified local final take: **112.56 seconds**, 1366×768, no audio or page errors. SHA-256 `a2163f550194e5a1267fad8da83e7b76fd61014285b0022e17e182ae8852081b`. The utility-warning frame was visually checked and the missed-target text is fully visible. A human still needs to watch the whole take before use.
