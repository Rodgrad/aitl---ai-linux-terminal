#!/usr/bin/env python3
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
import subprocess
import json
from pathlib import Path

# ----------------- Persistent Command History -----------------
history_file = Path.home() / ".ailt_history"
command_history_file = Path.home() / ".ailt_cmd_history.json"

if command_history_file.exists():
    with open(command_history_file, "r", encoding="utf-8") as f:
        cmd_history = json.load(f)
else:
    cmd_history = {}

session = PromptSession(history=FileHistory(history_file))

# ----------------- Completer with Last Used Args -----------------
class CommandHistoryCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.strip()
        parts = text.split()
        if not parts:
            return
        cmd = parts[0]
        last_arg = parts[-1] if len(parts) > 1 else ""
        if cmd in cmd_history:
            for prev in cmd_history[cmd]:
                if prev.startswith(last_arg):
                    yield Completion(prev, start_position=-len(last_arg))

# ----------------- Minimal Shell Loop -----------------
completer = CommandHistoryCompleter()

while True:
    try:
        user_input = session.prompt("> ", completer=completer).strip()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break

        # Save command-specific arguments
        parts = user_input.split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else ""
        if arg:
            cmd_history.setdefault(cmd, [])
            if arg not in cmd_history[cmd]:
                cmd_history[cmd].append(arg)
                # Keep last 50 entries
                cmd_history[cmd] = cmd_history[cmd][-50:]
                with open(command_history_file, "w", encoding="utf-8") as f:
                    json.dump(cmd_history, f, indent=2)

        subprocess.run(user_input, shell=True)

    except KeyboardInterrupt:
        continue
    except EOFError:
        break
