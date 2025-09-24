About
AILT is a Linux terminal tool powered by AI. It allows you to issue commands in natural language, which it can execute on your system. Designed primarily as a learning tool and assistant, AILT is intended to support your workflow rather than replace your control—users should remain the main driver while relying on AILT as a helper.

Note: This is an alpha testing prototype. AILT provides the freedom to use third-party LLM models and does not control their responses. AILT serves solely as an interface and is provided "as-is" without any guarantees. While the tool itself is designed to be safe, its usage depends on user practices and command execution. The developers do not assume any responsibility or liability for its use.
Tip: Always ensure that the command is correct and safe before confirming execution.

Features
Natural language command execution
Auto-completion suggestions
AI assistant for complex workflows
Supports Linux distros: RPM, DEB, TAR
Man Pages
Command explanations
Installation
# RPM
sudo rpm -i ailt.rpm

# DEB
sudo dpkg -i ailt.deb
Note: The default AI model used by AILT is Mistral.

Note: Installing and using AILT requires OLLAMA and Mistral7b model, which will download approximately 5 GB of data. Ensure you have enough storage before installation.

Source Code & Contribution
AILT is an open-source project. You can find the source code, report issues, or contribute on GitHub:

AILT GitHub Repository
Report an Issue
Contributing Guidelines





Manual
Usage Example
You can interact with AILT using natural language commands. For example, to get the first line from a file named secret.txt, you can type:

AI: Get me the first line from secret.txt
AILT will interpret your request, run the necessary Linux command, and return the output automatically.

Tip: Always ensure that the command is correct and safe before confirming execution.

Tip: Always verify the file path and permissions before executing commands to avoid errors

AILT Commands
model - Show current Ollama model
set model - Set new Ollama model
verbose - Toggle verbose mode
dryrun - Toggle dry-run mode
history - Show command history
clear history - Clear command history
exit / quit - Exit AI Shell
help - Show this message
Credits
This project was created and is maintained by Luka Beslic.

Contact
email:devluka.public@gmail.com
