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
    r"sen[dt][- ]it",                    # send it, send-it, sent it
    r"let[- ](?:it|her|'?er|a)[- ]rip",  # let it rip, let her rip, let'er rip
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
    r"([,\s-]*\s*" + KEYWORD_RE + r"[,.;:!?…-]*\s*)$",
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


_TURN_MARKERS = (
    "▸ Thought",
    "○ Thought",
    "● Ran",
    "○ Running",
    "● Running",
    "● Used",
    "● Edited",
    "└ Tip:",
)

_RECORDING_BANNER_RE = re.compile(
    r"^\s*[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏⣾⣽⣻⢿⡿⣟⣯⣷●◉○]\s*(?:Recording|Transcribing|Listening)\b"
)


def _is_finishing_up_line(line: str) -> bool:
    s = line.strip()
    if s.startswith((">", "❯", "•", "-", "*", "`", '"', "'")):
        return False
    return (
        "Finishing up..." in s
        and ("esc to discard" in s or "insert what you have" in s)
        and "`" not in s
        and '"' not in s
    )


def _is_dictation_banner_line(line: str) -> bool:
    s = line.strip()
    if s.startswith((">", "❯", "•", "-", "*", "`", '"', "'")):
        return False
    if _is_finishing_up_line(s):
        return True
    if "· esc to discard" in s and "`" not in s and '"' not in s:
        return True
    return bool(_RECORDING_BANNER_RE.match(line))


def _is_border_line(line: str) -> bool:
    stripped = line.strip()
    return len(stripped) >= 20 and stripped.count("─") >= len(stripped) - 2


def _find_prompt_section(output: str) -> tuple[list[str], bool, bool]:
    """Returns (input_box_lines, is_dictation_active, is_finishing_up)."""
    raw_lines = [line.rstrip() for line in output.splitlines()]
    while raw_lines and not raw_lines[-1].strip():
        raw_lines.pop()

    if not raw_lines:
        return [], False, False

    search_start = max(0, len(raw_lines) - 80)
    border_indices = [
        idx
        for idx in range(search_start, len(raw_lines))
        if _is_border_line(raw_lines[idx])
    ]
    if len(border_indices) < 2:
        return [], False, False

    # Full-width TUI prompt/drawer borders match the terminal width, whereas
    # conversation turn dividers are fixed 60-char '─' lines.
    max_width = max(raw_lines[idx].count("─") for idx in border_indices)
    full_borders = [
        idx for idx in border_indices if raw_lines[idx].count("─") >= max_width - 4
    ]
    if len(full_borders) < 2:
        full_borders = border_indices

    # Walk upward from the bottom through consecutive full-width border pairs so
    # drawers below the prompt (e.g. '● Swarm(...)', '● Live') are skipped.
    for k in range(len(full_borders) - 2, -1, -1):
        top, bot = full_borders[k], full_borders[k + 1]
        if bot - top > 30:
            continue
        candidate_box = raw_lines[top + 1 : bot]
        if not candidate_box:
            continue
        if any(line.lstrip().startswith(_TURN_MARKERS) for line in candidate_box):
            continue
        first_stripped = candidate_box[0].lstrip()
        if first_stripped and first_stripped[0] in (">", "❯"):
            ui_lines = raw_lines[max(search_start, top - 3) : top] + raw_lines[bot + 1 :]
            finishing_up = any(_is_finishing_up_line(u) for u in ui_lines)
            dictation_active = finishing_up or any(
                _is_dictation_banner_line(u) for u in ui_lines
            )
            return candidate_box, dictation_active, finishing_up

    return [], False, False


def get_input_box_lines(output: str) -> list[str]:
    box_lines, _, _ = _find_prompt_section(output)
    return box_lines


def _extract_prompt_from_box(box_lines: list[str]) -> str:
    if not box_lines:
        return ""

    if any(line.lstrip().startswith(_TURN_MARKERS) for line in box_lines):
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


def extract_active_prompt(output: str) -> str:
    box_lines, _, _ = _find_prompt_section(output)
    return _extract_prompt_from_box(box_lines)


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
                box_lines, dictation_active, finishing_up = (
                    _find_prompt_section(output) if output else ([], False, False)
                )
                candidate = _extract_prompt_from_box(box_lines)
                elapsed = now - state["initiated_at"]

                if finishing_up:
                    if state["finishing_up_since"] == 0.0:
                        state["finishing_up_since"] = now
                    finishing_dur = now - state["finishing_up_since"]
                    kw_count, _ = (
                        find_trailing_keyword_count(candidate)
                        if candidate
                        else (0, "")
                    )
                    # If 'Finishing up...' stalls (e.g. heavy Cloudtop Swarm / mic-serve load),
                    # press enter once to 'insert what you have', then scrub on the next tick
                    # once dictation_active clears.
                    should_force_insert = (
                        not state["sent_finish_enter"]
                        and candidate
                        and not candidate.strip().startswith("/voice")
                        and (
                            (kw_count > 0 and finishing_dur >= 0.9)
                            or finishing_dur >= 2.0
                        )
                    )
                    if should_force_insert:
                        print(
                            "[voice_scrub] 'Finishing up...' stalled; pressing enter to insert draft."
                        )
                        state["sent_finish_enter"] = True
                        state["last_candidate"] = ""
                        state["last_candidate_at"] = 0.0
                        actions.key("enter")
                        return
                else:
                    state["finishing_up_since"] = 0.0

                # Safety valve so an unexpected banner match cannot block forever
                if dictation_active and state["sent_finish_enter"] and elapsed > 6.0:
                    dictation_active = False

                if (
                    not dictation_active
                    and candidate
                    and not candidate.strip().startswith("/voice")
                ):
                    kw_count, _ = find_trailing_keyword_count(candidate)
                    if candidate == state["last_candidate"]:
                        required_stable = 0.15 if state["sent_finish_enter"] else 0.35
                        stable_for = now - state["last_candidate_at"]
                        settled = (
                            stable_for >= required_stable
                            if (kw_count > 0 or state["sent_finish_enter"])
                            else (elapsed >= 2.2 and stable_for >= 1.2)
                        )
                        if settled:
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
        "initiated_at": now,
        "start_at": now + 0.4,
        "deadline": now + 15.5,
        "finishing_up_since": 0.0,
        "sent_finish_enter": False,
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
        _cancel_active_poll()
        contents = get_iterm_text()
        prompt_text = extract_active_prompt(contents) if contents else ""
        if not prompt_text:
            print("[voice_scrub] No prompt text found in iTerm2.")
            return
        _finish_scrub(prompt_text, bool(submit))

    def iterm_finish_voice_and_scrub(submit: int = 0):
        """Stops /voice recording, waits for transcription to land in the input box, scrubs trailing keywords, and optionally submits."""
        _cancel_active_poll()
        actions.key("enter")
        _start_poll_and_scrub(bool(submit))
