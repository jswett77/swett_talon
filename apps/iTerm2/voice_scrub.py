import os
import re
import subprocess
import tempfile
import time
from typing import Optional
from talon import Module, actions, cron

mod = Module()

# Single keyword patterns for voice termination commands and common speech-to-text misrecognitions
KEYWORDS = [
    r"10[-/: ]?0?4",                     # 10-4, 10:04, 10/4, 10 4, 104
    r"10[- ]?for",                       # 10 for
    r"ten[- ](?:four|4|for)",            # ten four, ten 4, ten for
    r"send[- ]it",                       # send it, send-it
    r"let[- ](?:it|her|'?er)[- ]rip",    # let it rip, let her rip, let'er rip
    r"letter[- ](?:rip|it|her)",         # letter rip, letter it, letter her
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

_ITERM_CONTENTS_SCRIPT = (
    'tell application "iTerm2" to tell current session of current window to get contents'
)

# Active non-blocking poll state (managed exclusively on Talon's cron thread)
_poll_state = None
_poll_generation = 0


def _start_iterm_read() -> Optional[tuple]:
    tmp = None
    try:
        tmp = tempfile.TemporaryFile(mode="w+b")
        proc = subprocess.Popen(
            ["osascript", "-e", _ITERM_CONTENTS_SCRIPT],
            stdin=subprocess.DEVNULL,
            stdout=tmp,
            stderr=subprocess.STDOUT,
        )
        return proc, tmp
    except Exception as e:
        if tmp is not None:
            tmp.close()
        print(f"[voice_scrub] Failed to start iTerm2 read: {e}")
        return None


def _read_tail_from_tmp(tmp, max_bytes: int = 32768) -> str:
    tmp.seek(0, os.SEEK_END)
    size = tmp.tell()
    tmp.seek(max(0, size - max_bytes))
    return tmp.read().decode("utf-8", errors="replace")


def get_iterm_text() -> str:
    try:
        return subprocess.check_output(
            ["osascript", "-e", _ITERM_CONTENTS_SCRIPT],
            stdin=subprocess.DEVNULL,
            text=True,
            timeout=2.0,
        )
    except Exception as e:
        print(f"[voice_scrub] Failed to read iTerm2 contents: {e}")
        return ""


def get_input_box_lines(output: str) -> list[str]:
    raw_lines = [line.rstrip() for line in output.splitlines()]
    while raw_lines and not raw_lines[-1].strip():
        raw_lines.pop()

    if not raw_lines:
        return []

    search_start = max(0, len(raw_lines) - 80)
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

    # Guard against mistakenly matching an older conversation turn if a modal hides the bottom box
    for line in box_lines:
        if line.lstrip().startswith(("▸ Thought", "○ Thought", "● Ran", "○ Running", "└ Tip:")):
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
    if count > 0:
        for _ in range(count):
            actions.key("backspace")
            actions.sleep("15ms")

    if submit and remaining_text.strip():
        actions.sleep("150ms" if count > 0 else "50ms")
        print(f"[voice_scrub] Sending submit enter ({len(remaining_text.strip())} chars)")
        actions.key("enter")


def _close_poll_proc(state: dict):
    proc = state.get("proc")
    if proc is not None:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
        state["proc"] = None
    tmp = state.get("tmp")
    if tmp is not None:
        tmp.close()
        state["tmp"] = None


def _cancel_active_poll():
    global _poll_state, _poll_generation
    _poll_generation += 1
    if _poll_state is not None:
        job = _poll_state.get("job")
        if job is not None:
            cron.cancel(job)
        _close_poll_proc(_poll_state)
        _poll_state = None


def _finish_scrub(prompt_text: str, submit: bool):
    count, matched = find_trailing_keyword_count(prompt_text)
    remaining = prompt_text[:-count] if count > 0 else prompt_text
    if count > 0:
        print(f"[voice_scrub] Scrubbed {count} chars ({matched!r}) -> {remaining!r}")
    else:
        print(f"[voice_scrub] No trailing keywords found in: {prompt_text!r}")

    _apply_backspaces_and_submit(count, remaining, submit)


def _poll_tick(generation: int):
    global _poll_state
    state = _poll_state
    if state is None or generation != _poll_generation:
        return

    now = time.monotonic()
    if now < state["start_at"]:
        return

    proc = state["proc"]
    if proc is not None:
        ret = proc.poll()
        if ret is None:
            if now >= state["deadline"]:
                _cancel_active_poll()
                print("[voice_scrub] Timed out waiting for transcription to appear in iTerm2.")
                return
            if now - state["proc_started_at"] > 2.0:
                _close_poll_proc(state)
                print("[voice_scrub] Timed out reading iTerm2 contents; retrying.")
            else:
                return
        else:
            output = _read_tail_from_tmp(state["tmp"]) if state["tmp"] is not None else ""
            _close_poll_proc(state)
            if ret != 0:
                print(f"[voice_scrub] Failed to read iTerm2 contents: {output.strip()}")
            else:
                candidate = extract_active_prompt(output) if output else ""
                if candidate and not candidate.strip().startswith("/voice"):
                    if candidate == state["last_candidate"]:
                        if now - state["last_candidate_at"] >= 0.25:
                            submit = state["submit"]
                            _cancel_active_poll()
                            _finish_scrub(candidate, submit)
                            return
                    else:
                        state["last_candidate"] = candidate
                        state["last_candidate_at"] = now
                else:
                    state["last_candidate"] = ""
                    state["last_candidate_at"] = 0.0

    if now >= state["deadline"]:
        _cancel_active_poll()
        print("[voice_scrub] Timed out waiting for transcription to appear in iTerm2.")
        return

    if state["proc"] is None:
        started = _start_iterm_read()
        if started is not None:
            state["proc"], state["tmp"] = started
            state["proc_started_at"] = now


def _start_poll_and_scrub(submit: bool):
    global _poll_state, _poll_generation
    _cancel_active_poll()
    gen = _poll_generation
    now = time.monotonic()
    _poll_state = {
        "job": None,
        "proc": None,
        "tmp": None,
        "proc_started_at": 0.0,
        "start_at": now + 0.5,
        "deadline": now + 15.5,
        "last_candidate": "",
        "last_candidate_at": 0.0,
        "submit": submit,
    }
    _poll_state["job"] = cron.interval("150ms", lambda: _poll_tick(gen))


@mod.action_class
class Actions:
    def iterm_start_voice():
        """Starts /voice dictate in Jetski and disables Talon speech."""
        _cancel_active_poll()
        actions.insert("/voice dictate")
        actions.key("enter")
        actions.speech.disable()

    def iterm_scrub_trailing_keywords(submit: int = 0):
        """Immediately scrubs trailing voice trigger words from the active Jetski prompt."""
        contents = get_iterm_text()
        prompt_text = extract_active_prompt(contents) if contents else ""
        if not prompt_text:
            print("[voice_scrub] No prompt text found in iTerm2.")
            return
        _finish_scrub(prompt_text, bool(submit))

    def iterm_finish_voice_and_scrub(submit: int = 0):
        """Stops /voice recording, waits for transcription to land in the input box, scrubs trailing keywords, and optionally submits."""
        # If unscrubbed text is already sitting in the prompt box (e.g. recording already stopped), scrub directly without submitting the keyword first
        contents = get_iterm_text()
        existing = extract_active_prompt(contents) if contents else ""
        if existing and not existing.strip().startswith("/voice"):
            count, _ = find_trailing_keyword_count(existing)
            if count > 0:
                _finish_scrub(existing, bool(submit))
                return
        actions.key("enter")
        _start_poll_and_scrub(bool(submit))
