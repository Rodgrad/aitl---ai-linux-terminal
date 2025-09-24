#!/usr/bin/env python3
import os
import sys
import distro
import subprocess
import requests
import json
from pathlib import Path
from rich import print
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory

# ------------------- CONFIG -------------------
CONFIG_PATH = Path.home() / ".config" / "ailt" / "config.json"
DEFAULT_CONFIG = {"model": "mistral", "verbose": False, "dry_run": False}

# ------------------- HISTORY -------------------
HISTORY_FILE = Path.home() / ".ailt_history"
COMMAND_HISTORY_FILE = Path.home() / ".ailt_cmd_history.json"

# ------------------- OLLAMA -------------------
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
DISTRO_NAME = distro.id() or "unknown"

# ------------------- LOAD / SAVE CONFIG -------------------
def load_config():
    try:
        if not CONFIG_PATH.exists():
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("[yellow]Config file corrupted, resetting to default.[/yellow]")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

config = load_config()
session = PromptSession(history=FileHistory(HISTORY_FILE))

# ------------------- LOAD COMMAND HISTORY -------------------
try:
    if COMMAND_HISTORY_FILE.exists():
        with open(COMMAND_HISTORY_FILE, "r", encoding="utf-8") as f:
            cmd_history = json.load(f)
    else:
        cmd_history = {}
except (json.JSONDecodeError, FileNotFoundError):
    print("[yellow]Command history corrupted, resetting.[/yellow]")
    cmd_history = {}




# ------------------- CONFIRMATION -------------------
def confirm_command(command: str) -> str | None:
    while True:
        print(Panel(f"[cyan][AI suggests][/cyan] [yellow]{command}[/yellow]", title="AI Shell"))
        choice = Prompt.ask(f"[cyan][ y/N/r ] Run it?[/cyan]", default="n").strip().lower()
        if choice == "y":
            return command
        elif choice in ("n", ""):
            return None
        elif choice == "r":
            return "retry"
        else:
            print("[red]Invalid input.[/red] Choose y, n, or r.")

# ------------------- DANGEROUS COMMAND CHECK -------------------
def is_dangerous(command: str) -> bool:
    dangerous_patterns = ["rm -rf /", "shutdown", "reboot", ":(){:|:&};:"]
    return any(pattern in command for pattern in dangerous_patterns)

# ------------------- COMPLETER -------------------
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

completer = CommandHistoryCompleter()

# ------------------- META COMMANDS -------------------
def show_model(args=None):
    print(f"[green]Active Model:[/green] [bold]{config['model']}[/bold]")

def set_model(args=None):
    if not args:
        print("[red]Specify a model name![/red]")
        return
    config["model"] = args[0]
    save_config(config)
    print(f"[green]Model updated to {args[0]}[/green]")

def toggle_verbose(args=None):
    config["verbose"] = not config.get("verbose", False)
    save_config(config)
    print(f"[green]Verbose mode set to {config['verbose']}[/green]")

def toggle_dry_run(args=None):
    config["dry_run"] = not config.get("dry_run", False)
    save_config(config)
    print(f"[green]Dry-run mode set to {config['dry_run']}[/green]")

def show_help(args=None):
    print("""
[bold]AI Shell Meta Commands:[/bold]
model            - Show current Ollama model
set model <name> - Set new Ollama model
verbose          - Toggle verbose mode
dryrun           - Toggle dry-run mode
history          - Show command history
clear history    - Clear command history
exit / quit      - Exit AI Shell
help             - Show this message
""")

def show_history(args=None):
    for cmd, args_list in cmd_history.items():
        print(f"[cyan]{cmd}:[/cyan] {args_list}")

def clear_history(args=None):
    global cmd_history
    cmd_history = {}
    COMMAND_HISTORY_FILE.unlink(missing_ok=True)
    print("[green]Command history cleared[/green]")

def exit_shell(args=None):
    print("[red]Exiting AI Shell.[/red]")
    sys.exit(0)

META_COMMANDS = {
    "model": show_model,
    "set model": set_model,
    "verbose": toggle_verbose,
    "dryrun": toggle_dry_run,
    "help": show_help,
    "history": show_history,
    "clear history": clear_history,
    "exit": exit_shell,
    "quit": exit_shell
}


def get_prompt():
    cwd = os.getcwd()  # Current working directory
    prompt_text = (
        f"\x1b[1;32m🤖 ai@{DISTRO_NAME}\x1b[0m  "
        f"[\x1b[36m{cwd}\x1b[0m]:: "
    )
    return ANSI(prompt_text)

# ------------------- AI TRANSLATION -------------------
def ai_translate(natural_text: str) -> str:
    payload = {
        "model": config["model"],
        "prompt": f"""
You are a Linux {DISTRO_NAME} shell command generator.
Rules:
-home folder path is ~/ and not /home
-if command contains text in quotes it mush end with closing quote
- Output only bash command text, exactly as it can be run.
-Output the exact command **exactly as it should be typed in a shell**. 
-Do NOT add backticks, quotes, or markdown formatting. 
-Do not add extra text, explanation, or safety escapes. 
-If the command contains special characters like /, ~, or spaces, include them literally.
- No explanations, notes, or extra text.
- Example correct: cd ~/ 
- Example incorrect: `cd -` or "ls -l /home"
- Add sudo when needed
- All folders must end with '/' in command
- If no data provided assume operations on current directory
- If user asks about command and not for command, provide short explanation
Distro: {DISTRO_NAME}
User request: {natural_text}
Command:
"""
    }

    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=10) as response:
            response.raise_for_status()
            # Read the entire response content first
            raw = b"".join(response.iter_content(chunk_size=None))
            raw_text = raw.decode("utf-8")

            # Extract all JSON objects and concatenate 'response' fields
            result = ""
            for obj in raw_text.strip().splitlines():
                try:
                    data = json.loads(obj)
                    if "response" in data:
                        result += data["response"]
                except json.JSONDecodeError:
                    continue

            if config.get("verbose"):
                print(f"[cyan]AI Payload:[/cyan] {payload}")
                print(f"[green]AI Response:[/green] {result}")

            return result

    except requests.RequestException as e:
        print(f"[red]Error contacting AI API:[/red] {e}")
        return ""
    

# ------------------- MAIN LOOP -------------------
def main():
    shell = os.environ.get("SHELL", "/bin/bash")
    print(Panel(
        f"[bold green]# System:[/bold green] {DISTRO_NAME}\n"
        f"[bold green]# AI Shell running with {shell}[/bold green]\n"
        "Type 'ai <text>' for natural language commands, or shell commands directly.\n"
        "Type 'help' for meta commands.",
        title="AI Shell"
    ))

    while True:
        try:
            user_input = session.prompt(get_prompt(), completer=completer).strip()
            if not user_input:
                continue

            # Check meta commands first
            command_key = next((key for key in META_COMMANDS if user_input.startswith(key)), None)
            if command_key:
                args = user_input[len(command_key):].strip().split()
                META_COMMANDS[command_key](args)
                continue


            if user_input.startswith("cd "):
                path = user_input[3:].strip() or os.path.expanduser("~")
                try:
                    os.chdir(os.path.expanduser(path))
                except FileNotFoundError:
                    print(f"[red]Directory not found:[/red] {path}")
                except Exception as e:
                    print(f"[red]Error changing directory:[/red] {e}")
                continue


            # AI command
            # AI command
            if user_input.startswith("ai "):
                natural_text = user_input[3:].strip()
                while True:
                    command = ai_translate(natural_text)
                    if not command:
                        break
                    if config.get("dry_run"):
                        print(f"[yellow]Dry-run: {command}[/yellow]")
                        break
                    result = confirm_command(command)
                    if result == "retry":
                        continue
                    elif result is None:
                        break
                    elif is_dangerous(result):
                        print("[red]Dangerous command detected! Not executing.[/red]")
                        break
                    else:
                        # Handle AI-generated cd commands
                        cmd_strip = result.strip()
                        if cmd_strip.startswith("cd "):
                            path = cmd_strip[3:].strip() or os.path.expanduser("~")
                            try:
                                os.chdir(os.path.expanduser(path))
                                print(f"[green]Changed directory to {os.getcwd()}[/green]")
                            except FileNotFoundError:
                                print(f"[red]Directory not found:[/red] {path}")
                            except Exception as e:
                                print(f"[red]Error changing directory:[/red] {e}")
                        else:
                            try:
                                subprocess.run(result, shell=True, check=True)
                            except subprocess.CalledProcessError as e:
                                print(f"[red]Command failed: {e}[/red]")
                        break
                continue


            # Save command arguments for completer
            parts = user_input.split(maxsplit=1)
            cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else ""
            if arg:
                cmd_history.setdefault(cmd, [])
                if arg not in cmd_history[cmd]:
                    cmd_history[cmd].append(arg)
                    cmd_history[cmd] = cmd_history[cmd][-50:]
                    with open(COMMAND_HISTORY_FILE, "w", encoding="utf-8") as f:
                        json.dump(cmd_history, f, indent=2)

            if is_dangerous(user_input):
                print("[red]Dangerous command detected! Not executing.[/red]")
                continue

            if config.get("dry_run"):
                print(f"[yellow]Dry-run: {user_input}[/yellow]")
                continue

            # Execute shell command
            try:
                subprocess.run(user_input, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"[red]Command failed: {e}[/red]")

        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            print()
            break

# ------------------- ENTRY POINT -------------------
def run():
    main()

if __name__ == "__main__":
    run()
