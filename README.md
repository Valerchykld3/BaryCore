# BaryCore

**Modular Telegram-based remote automation system** written in Python.

BaryCore provides a unified Telegram interface for executing tasks on a local computer or a cloud-hosted Linux environment. It combines deterministic command handlers with Google Gemini-powered agents that can invoke Python tools.

> **Project status:** Personal, experimental automation system. The Sky implementation runs on an Ubuntu VM; it is not a production-hardened multi-user platform. This repository also includes historical Ground development in a separate branch.

## Why it exists

The project was developed to make files, scripts, system utilities, and connected cloud services accessible while away from the primary computer. The initial local design (**Ground**) depended on the user's PC staying awake. **Sky** moves execution to a cloud VM, reducing that dependence.

## Architecture

```text
User (private Telegram chat)
        |
        v
aiogram polling / BaryCoreBase
        |-- Agent registration and routing
        |-- StaticEngine  -> predefined Python functions
        `-- DynamicEngine -> Google Gemini + Python tool calling
                                     |
                  +------------------+-------------------+
                  |                  |                   |
             Executor            Integrator           Analyst
          Linux files/shell    Google APIs      Telegram history/math
```

- **BaryCoreBase** (`core/base_script.py`): Telegram handling, agent routing, access check, replies, and hand-offs.
- **StaticEngine** (`core/staticEngine.py`): dispatches keyword-based commands to predetermined functions.
- **DynamicEngine** (`core/dynamicEngine.py`): loads archetype instructions from JSON, creates a Gemini chat session, and exposes Python tools.
- **Archetypes** (`archetypes/`): Executor, Integrator, Analyst, and a Communicator definition. The Communicator tools module is currently empty.

### Registered agents in Sky

| ID | Agent | Engine | Main responsibility |
|---|---|---|---|
| `@DFMB` | File Manager Bot | Dynamic | Linux file operations |
| `@DTRB` | Task Runner Bot | Dynamic | Shell commands and system monitoring |
| `@DGDB` | Google Drive Bot | Dynamic | Google Drive file operations |
| `@SGRB` | Gmail Reader Bot | Static | Unread mail, mailbox status, drafting |
| `@DMSB` | Math Solver Bot | Dynamic | Mathematics and physics reasoning |
| `@DNIB` | News Intercept Bot | Dynamic | Reading and summarizing Telegram channels |

Send `/agents` to list registered agents. To address an agent, start a Telegram message with its ID, for example `@DTRB show system resources`. Available functionality depends on the registered tools, API permissions, and model availability.

## Deployment models

**Ground:** The code executes on a personal computer and can interact with that host. The PC must remain available.

**Sky:** The code executes on an Ubuntu cloud VM and interacts with that VM's filesystem, processes, and connected services. Use the `BaryCore-Sky` branch for the cloud model. Cloud uptime does not guarantee application uptime; monitor the process and provider separately.

## Getting started: Sky

Requirements: Python 3.10+, Ubuntu/Linux VM, Telegram BotFather token, Gemini API key, and user Telegram ID. Google Workspace and Telethon integration require additional credentials.

```bash
git clone --branch BaryCore-Sky https://github.com/Valerchykld3/BaryCore.git
cd BaryCore
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**Dependency note:** The pinned package versions in `requirements.txt` are a candidate November 2026 set, **not** the versions extracted from the author's operating VM. Test them in a separate environment before upgrading an existing installation.

Create a private `KEYS.json` in the repository root (never commit it):

```json
{
  "telegram_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "gemini_api_key": "YOUR_GEMINI_API_KEY",
  "allowed_user_id": "YOUR_TELEGRAM_USER_ID",
  "api_id": "YOUR_TELEGRAM_API_ID",
  "api_hash": "YOUR_TELEGRAM_API_HASH"
}
```

The Telegram `api_id` and `api_hash` fields are needed for the Telegram channel analysis tool. Google integration needs `credentials.json` and `token.json`; Telethon needs an authorized `user_session.session`. For a headless VM, perform interactive OAuth/Telegram login locally and transfer the generated files securely. Access and token lifetimes depend on the providers' settings.

To test in the foreground:

```bash
python main.py
```

For persistent operation, follow the **systemd setup** in [Sky setup instructions](.README/how_to_use-sky.txt). Keep the `WorkingDirectory` and `ExecStart` paths consistent with the checkout and virtual environment. Do not run two polling processes using the same Telegram bot token.

## Repository layout

```text
main.py                    # Agent registration and entrypoint
core/                      # Telegram orchestration and execution engines
tools/                     # Executor, Integrator, Analyst integrations
archetypes/                # JSON agent instructions
auth_telethon.py           # Local Telethon login helper
.README/how_to_use-sky.txt # Detailed Sky deployment and OAuth instructions
.README/Sky&Ground.txt     # Model differences
```

## Security and limitations

- **Single-user design.** The current code filters `message.chat.id` against an allowlisted Telegram user ID. It is intended for private chats and does not implement a separate sender-ID check for groups.
- **Powerful execution tools.** Dynamic agents can call shell commands and perform destructive file actions. System instructions are guidance for the model, **not** an enforceable approval mechanism or sandbox.
- **Permanent deletion on Sky.** Linux file operations may permanently remove data; avoid running the service with privileged credentials.
- **Credentials.** `KEYS.json`, Google OAuth files, and Telethon session files must remain private and are excluded by `.gitignore`. Audit deployment permissions and avoid exposing secrets in logs or screenshots.
- **Operational maturity.** There is no published automated test suite, and no claim of tested 24/7 availability or production-grade isolation.

## Documentation

- [BaryCore technical articles on NovTech](https://novtech-ruby.vercel.app/BaryCore/en/p0)
- [Detailed Sky setup](.README/how_to_use-sky.txt)
- [Ground vs Sky](.README/Sky&Ground.txt)
- [System instruction notes](.README/SI_doc.txt)

## License

See [LICENSE](LICENSE).
