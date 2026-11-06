# Personal Laptop Talon Update & Sync Guide

> **Context for Executing Agent**: This guide is designed to be executed directly on the user's personal macOS laptop to synchronize their custom Talon configuration (`swett_talon`) with the work laptop setup, decouple it from community repo modifications, and ensure full feature parity.

---

## 1. Upstream Community Project Investigation (`knausj_talon` Status)

### What Happened to `knausj_talon`?
- **Renamed and Relocated**: The repository originally created by Jeff Knaus (`knausj85/knausj_talon`) was officially transferred to the `talonhub` GitHub organization and renamed to **[`talonhub/community`](https://github.com/talonhub/community)**.
- **Redirects**: `https://github.com/knausj85/knausj_talon` automatically redirects to `https://github.com/talonhub/community`.
- **Directory Name in Talon**: Talon recursively loads all `.talon` and `.py` scripts located inside `~/.talon/user/` regardless of folder name. Whether the community folder is named `community` or `knausj_talon`, Talon treats it identically.
- **Modern Best Practice**: The standard community folder name is now `~/.talon/user/community`. It should be kept **100% clean and unmodified** so that it tracks upstream `main` without merge conflicts.

---

## 2. Target Workspace Architecture

On the personal laptop, `~/.talon/user/` should look like this:

```
~/.talon/user/
├── community/          # Clean clone of https://github.com/talonhub/community (or knausj_talon)
├── swett_talon/        # git@github.com:jswett77/swett_talon.git (all personal & custom logic)
└── talon-gaze-ocr/     # git@github.com:jswett77/talon-gaze-ocr.git (if using Tobii eye tracker)
```

> [!NOTE]
> `swett_google_only` should **NOT** exist on the personal laptop. All generic functionality (terminal dictation, scrubber, silent window cycling, app focus, tmux tabs, and sleep commands) has been completely extracted into `swett_talon`.

---

## 3. Step-by-Step Sync Instructions for the Personal Laptop

### Step 1: Inspect `~/.talon/user`
Run the following check to see what directories currently exist:
```bash
ls -la ~/.talon/user
```
Identify whether the community repo is named `community` or `knausj_talon`, and confirm `swett_talon` is present.

---

### Step 2: Sync and Update `swett_talon`
Navigate into `swett_talon` and ensure your working directory is clean before pulling:

```bash
cd ~/.talon/user/swett_talon

# Check git status
git status

# If there are unstaged local changes or untracked test files, stash them
git stash --include-untracked

# Ensure remote is tracking origin main and pull latest commits
git fetch origin
git checkout main
git pull origin main
```

#### Verify Recent Commits Landed
Run:
```bash
git log -n 5 --oneline
```
You should see the latest commits:
- `21e7790` — *Disable knausj pop clicks cleanly to prevent interference with Parrot*
- `76ca05c` — *Add sleep focus, wake/sleep commands, and snag app alias to personal repo*
- `347bdb2` — *Extract voice dictate, trailing keyword scrubber, tmux tabs, and handoff to personal repo*
- `757fe0c` — *Add sleep_window action and broaden voice trigger for window cycling*
- `68f0feb` — *Enable window next and window last in sleep mode*

---

### Step 3: Ensure Community Repo Is Clean (No Local Forks/Tweaks)
If the personal laptop has a clone of `community` (or `knausj_talon`), ensure it is on a clean, unmodified tracking branch:

```bash
# Check whichever community folder exists:
COMMUNITY_DIR="$([ -d ~/.talon/user/community ] && echo ~/.talon/user/community || echo ~/.talon/user/knausj_talon)"
cd "$COMMUNITY_DIR"

git status
```

- If `git status` shows modified files (like old `wake_and_sleep.talon` or `mouse.py` tweaks), discard or stash them:
  ```bash
  git stash
  git checkout main
  git pull origin main
  ```
- All custom overrides are now loaded with higher priority from `swett_talon`, so the community repo can stay completely stock.

---

### Step 4: Verify Talon Engine & Reload Log
Talon hot-reloads scripts whenever files are updated. Check the live log:

```bash
tail -n 50 ~/.talon/talon.log
```

Confirm that:
1. `swett_talon/core/windows_and_tabs/sleep_window.py` loaded without errors.
2. `swett_talon/core/parrot/disable_knausj_pop.py` loaded without errors.
3. `swett_talon/core/app_switcher/sleep_focus.py` loaded without errors.
4. `swett_talon/apps/iTerm2/voice_scrub.py` loaded without errors.

---

## 4. Verification & Testing Checklist

Once synced, test each of the following voice commands:

| Command | Expected Action | Verification |
| :--- | :--- | :--- |
| **`window next`** or **`next window`** | Cycles to the next window of the frontmost application using accessibility API | Log prints `[sleep_window] Switching from ... to ...` |
| **`window last`** or **`previous window`** | Cycles backwards through windows of the frontmost app | Cycles to prior window |
| **`snap left`** / **`snap right`** / **`snap next screen`** | Snaps window into position (works in sleep mode) | Window moves/snaps |
| **`focus chrome`** / **`focus term`** / **`focus chat`** | Focuses the specified app (works in sleep mode) | Brings app to front |
| **`snag <app>`** | Focuses running application via app switcher | Brings app to front |
| **`handoff`** | Puts Talon to sleep and triggers macOS native dictation (<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>A</kbd>) | Talon sleeps, macOS dictation microphone appears |
| **`talon wake`** / **`no cap`** / **`raptors`** | Wakes Talon speech engine | Speech status changes to listening |
| **`drowse`** | Disables Talon speech | Speech status changes to sleeping |
| **`wonder`** (in iTerm2) | Types `/voice dictate`, enters, and sleeps Talon | Terminal voice recording starts |
| **`send it`** / **`ten four`** (in iTerm2) | Halts recording, polls terminal, scrubs trailing trigger keywords | Log prints `[voice_scrub] Scrubbed X chars` |
| **`let it rip`** (in iTerm2) | Stops recording, scrubs trailing keywords, and presses Enter to submit | Prompt submits cleanly |

---

## 5. Troubleshooting Reference

- **Mac Accessibility Permissions**: If window cycling or app focusing fails, verify in macOS **System Settings → Privacy & Security → Accessibility** that **Talon** is enabled.
- **Mac Microphone Permissions**: Ensure **Talon** (and **iTerm2** if using local mic server) are granted Microphone access under **System Settings → Privacy & Security → Microphone**.
- **Parrot Noise Clashing**: If making pop sounds clicks the mouse, ensure `core/parrot/disable_knausj_pop.py` is loaded in `swett_talon`. It intercepts `user.noise_trigger_pop` and prevents knausj's default mouse click handler.
