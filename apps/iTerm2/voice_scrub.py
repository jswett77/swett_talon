import re
import subprocess
import threading
import time
from talon import Module, actions, cron

mod = Module()

# Single keyword patterns for voice termination commands and common speech-to-text misrecognitions
KEYWORDS = [
    r"10[-/: ]?0?4",                     # 10-4, 10:04, 10/4, 10 4, 104
    r"10[- ]?for",                       # 10 for
    r"ten[- ](?:four|4|for)",            # ten four, ten 4, ten for
    r"send[- ]it",                       # send it, send-it
    r"let[- ](?:it|her|'?er)[- ]rip",    # let it rip, let her rip, let'er rip
    r"letter[- ]rip",                    # letter rip
    r"ship[- ]it",                       # ship it
    r"clean[- ](?:send|four)",           # clean send, clean four
    r"roger(?:[- ]that)?",               # roger, roger that
    r"copy(?:[- ]that)?",                # copy, copy that
    r"stamp[- ]it",                      # stamp it
    r"stampede",                         # stampede
]

KEYWORD_RE = "(?:" + "|".join(KEYWORDS) + ")"
SINGLE_TRAILING_RE = re.compile(
    r"([,\s-]*\s*" + KEYWORD_RE + r"[,.;:!?-]*\s*)$",
    re.IGNORECASE,
)


def get_iterm_text() -> str:
    script = 'tell application "iTerm2" to tell current session of current window to get contents'
    try:
        return subprocess.check_output(["osascript", "-e", script], text=True, timeout=2.0)
    except Exception as e:
        print(f"[voice_scrub] Failed to read iTerm2 contents: {e}")
        return ""


def get_input_box_lines(output: str) -> list[str]:
    raw_lines = [line.rstrip() for line in output.splitlines()]
    while raw_lines and not raw_lines[-1].strip():
        raw_lines.pop()

    if not raw_lines:
        return []

    search_start = max(0, len(raw_lines) - 50)
    border_indices = [
        idx
        for idx in range(search_start, len(raw_lines))
        if raw_lines[idx].count("─") >= 20
    ]

    if len(border_indices) >= 2:
        return raw_lines[border_indices[-2] + 1 : border_indices[-1]]
    return []


def extract_active_prompt(output: str) -> str:
    box_lines = get_input_box_lines(output)
    if not box_lines:
        return ""

    first_stripped = box_lines[0].lstrip()
    if not first_stripped or first_stripped[0] not in (">", "❯"):
        return ""

    first_content = first_stripped[1:]
    if first_content.startswith(" "):
        first_content = first_content[1:]

    parts = [first_content.rstrip()] if first_content.strip() else []
    for line in box_lines[1:]:
        stripped = line.strip()
        if stripped:
            parts.append(stripped)

    return " ".join(parts).rstrip()


def find_trailing_keyword_count(prompt_text: str):
    if not prompt_text:
        return 0, ""

    original = prompt_text
    current = prompt_text
    removed_segments = []

    # Iteratively strip consecutive trailing termination keywords
    while True:
        m = SINGLE_TRAILING_RE.search(current)
        if not m:
            break
        segment = m.group(1)
        if not segment:
            break
        removed_segments.append(segment)
        current = current[:-len(segment)]

    # Clean up any dangling trailing comma or hyphen before the stripped words, preserving sentence periods
    dangling = re.search(r"([,\s-]+)$", current)
    if dangling and current != original:
        current = current[:-len(dangling.group(1))]

    count = len(original) - len(current)
    matched_phrase = "".join(reversed(removed_segments)) if count > 0 else ""
    return count, matched_phrase


def _apply_backspaces_and_submit(count: int, remaining_text: str, submit: bool):
    for _ in range(count):
        actions.key("backspace")
        actions.sleep("15ms")

    if submit and remaining_text.strip():
        actions.sleep("100ms")
        actions.key("enter")


def _poll_and_scrub_worker(wait_for_voice: bool, submit: bool):
    prompt_text = ""
    if wait_for_voice:
        # Give remote voice recording a moment to initiate stopping/transcription
        time.sleep(0.5)
        deadline = time.monotonic() + 8.0
        while time.monotonic() < deadline:
            contents = get_iterm_text()
            candidate = extract_active_prompt(contents) if contents else ""
            if candidate and not candidate.strip().startswith("/voice"):
                time.sleep(0.25)
                contents2 = get_iterm_text()
                candidate2 = extract_active_prompt(contents2) if contents2 else candidate
                if candidate2 == candidate:
                    prompt_text = candidate2
                    break
            time.sleep(0.25)

        if not prompt_text:
            print("[voice_scrub] Timed out waiting for transcription to appear in iTerm2.")
            return
    else:
        contents = get_iterm_text()
        prompt_text = extract_active_prompt(contents) if contents else ""

    if not prompt_text:
        print("[voice_scrub] No prompt text found in iTerm2.")
        return

    count, matched = find_trailing_keyword_count(prompt_text)
    remaining = prompt_text[:-count] if count > 0 else prompt_text
    if count > 0:
        print(
            f"[voice_scrub] Scrubbed {count} chars ({matched!r}) -> {remaining!r}"
        )
    else:
        print(f"[voice_scrub] No trailing keywords found in: {prompt_text!r}")

    cron.after("0ms", lambda: _apply_backspaces_and_submit(count, remaining, submit))


@mod.action_class
class Actions:
    def iterm_start_voice():
        """Starts /voice dictate in Jetski and disables Talon speech."""
        actions.insert("/voice dictate")
        actions.key("enter")
        actions.speech.disable()

    def iterm_scrub_trailing_keywords():
        """Immediately scrubs trailing voice trigger words from the active Jetski prompt."""
        threading.Thread(
            target=_poll_and_scrub_worker, args=(False, False), daemon=True
        ).start()

    def iterm_finish_voice_and_scrub(submit: int = 0):
        """Stops /voice recording, waits for transcription to land in the input box, scrubs trailing keywords, and optionally submits."""
        actions.key("enter")
        threading.Thread(
            target=_poll_and_scrub_worker, args=(True, bool(submit)), daemon=True
        ).start()
