# Personal Laptop Talon Update & Sync Guide

> **Context for Executing Agent**: This guide is designed to be executed directly on the user's personal macOS laptop by an AI coding assistant (or user) to synchronize their custom Talon configuration (`swett_talon`) with the work laptop setup, decouple it from community repo modifications, and ensure full feature parity.

---

## 1. Upstream Community Project Investigation (`knausj_talon` Status)

### What Happened to `knausj_talon`?
- **Renamed and Relocated**: The repository originally created by Jeff Knaus (`knausj85/knausj_talon`) was officially transferred to the `talonhub` GitHub organization and renamed to **[`talonhub/community`](https://github.com/talonhub/community)**.
- **Redirects**: `https://github.com/knausj85/knausj_talon` automatically redirects to `https://github.com/talonhub/community`.
- **Directory Name in Talon**: Talon recursively loads all `.talon` and `.py` scripts located inside `~/.talon/user/` regardless of folder name. Whether the community folder is named `community` or `knausj_talon`, Talon treats it identically.
- **IMPORTANT - Do Not Double-Load**: Ensure you have only **one** community folder (`community` OR `knausj_talon`). Having both will cause duplicate declaration collisions.
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

> [!WARNING]
> `swett_google_only` should **NOT** exist in `~/.talon/user/` on the personal laptop. All generic functionality (terminal dictation, scrubber, silent window cycling, app focus, tmux tabs, and sleep commands) has been completely extracted into `swett_talon`.
> If `swett_google_only` is currently present on the personal laptop, do not delete it outright; move it out of the active user directory:
> ```bash
> mv ~/.talon/user/swett_google_only ~/.talon/swett_google_only.bak
> ```

---

## 3. Step-by-Step Sync Instructions for the Personal Laptop

### Step 1: Inspect `~/.talon/user`
Run the following check to inspect existing folders:
```bash
ls -la ~/.talon/user
```
- Confirm `swett_talon` is present (if missing, clone: `git clone git@github.com:jswett77/swett_talon.git`).
- Check whether the community repository is named `community` or `knausj_talon`. If neither exists, clone it:
  ```bash
  git clone https://github.com/talonhub/community.git ~/.talon/user/community
  ```
- If `swett_google_only` is present, move it out:
  ```bash
  mv ~/.talon/user/swett_google_only ~/.talon/swett_google_only.bak
  ```

---

### Step 2: Sync and Update `swett_talon`
Navigate into `swett_talon`, inspect status, and pull latest:

```bash
cd ~/.talon/user/swett_talon

# Check git status
git status

# If there are modified tracked files or unstaged changes, stash them safely:
# git stash

# Pull latest commits from main
git fetch origin
git checkout main
git pull origin main
```

#### Verify Recent Commits Landed
Run:
```bash
git log -n 5 --oneline
```
Expected recent commits:
- `disable_knausj_pop` & settings override (pop noise decoupling for Parrot)
- `Add sleep focus, wake/sleep commands, and snag app alias to personal repo`
- `Extract voice dictate, trailing keyword scrubber, tmux tabs, and handoff to personal repo`
- `Add sleep_window action and broaden voice trigger for window cycling`
- `Enable window next and window last in sleep mode`

---

### Step 3: Clean and Update Community Repository
Check the installed Talon version (`grep "Talon Version:" ~/.talon/talon.log | tail -n 1`) before selecting the community revision—upstream `main` now targets **Talon 1.0+** (`egui` / Python 3.14), whereas **Talon 0.4.x** requires the **`v0.4`** release tag:

```bash
COMMUNITY_DIR="$([ -d ~/.talon/user/community ] && echo ~/.talon/user/community || echo ~/.talon/user/knausj_talon)"
cd "$COMMUNITY_DIR"

# 1. Update remote URL if still pointing to old knausj85 address
git remote set-url origin https://github.com/talonhub/community.git
git fetch origin --tags

# 2. Check current branch and preserve any old custom branch (e.g. my_tweaks) as backup
git status
git branch
# git branch my_tweaks_backup

# 3a. If running Talon 0.4.x (check `grep "Talon Version:" ~/.talon/talon.log | tail -n 1`):
git checkout -B community_v0.4 v0.4

# 3b. Only if running Talon 1.0+:
# git checkout main && git pull origin main
```

---

### Step 4: Verify Talon Engine Reload
Talon hot-reloads scripts automatically. Filter the log for errors or `swett_talon` events:

```bash
grep -nE "ERROR|swett_talon" ~/.talon/talon.log | tail -n 25
```

Ensure there are no `RuntimeError` or duplicate action declaration crashes.

---

## 4. Verification Checklists

### A. Automated Agent Verification (Files & Triggers on Disk)
An executing agent can verify the environment programmatically:

1. **Pop noise decoupling**:
   ```bash
   grep "mouse_enable_pop_click = 0" ~/.talon/user/swett_talon/core/parrot/parrot.talon
   ```
2. **Window cycling & snapping**:
   ```bash
   test -f ~/.talon/user/swett_talon/core/windows_and_tabs/sleep_window.py && echo "sleep_window.py OK"
   grep -E "window next|cycle window" ~/.talon/user/swett_talon/core/windows_and_tabs/sleep_snap.talon
   ```
3. **Voice dictation & trailing scrubber**:
   ```bash
   test -f ~/.talon/user/swett_talon/apps/iTerm2/voice_scrub.py && echo "voice_scrub.py OK"
   grep -E "wonder|send it|let it rip" ~/.talon/user/swett_talon/apps/iTerm2/voice.talon
   ```
4. **Handoff & Snag**:
   ```bash
   grep -E "handoff" ~/.talon/user/swett_talon/core/modes/wake_and_sleep_mac.talon
   grep -E "snag" ~/.talon/user/swett_talon/core/windows_and_tabs/global_mac.talon
   ```
5. **Silent Mode App Focus**:
   ```bash
   test -f ~/.talon/user/swett_talon/core/app_switcher/sleep_focus.py && echo "sleep_focus.py OK"
   grep -E "focus chrome|focus term|focus chat" ~/.talon/user/swett_talon/core/app_switcher/sleep_focus.talon
   ```

---

### B. User Voice Verification (Spoken by User)

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

- **SSH Authentication on Personal Laptop**: Pulling `swett_talon` requires that GitHub SSH keys (`git@github.com:...`) are configured on the personal laptop. If using HTTPS, ensure `gh auth login` or a Personal Access Token is active.
- **Mac Accessibility Permissions**: If window cycling or app focusing fails, verify in macOS **System Settings → Privacy & Security → Accessibility** that **Talon** is enabled.
- **Mac Microphone Permissions**: Ensure **Talon** is granted Microphone access under **System Settings → Privacy & Security → Microphone**.
