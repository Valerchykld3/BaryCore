import asyncio
import json
from core.base_script import BaryCoreBase
from tools.executor import find_file, read_file_content, execute_shell_command

async def main():
    with open("KEYS.json", "r", encoding="utf-8") as f:
        keys = json.load(f)

    bary_core = BaryCoreBase(
        telegram_token=keys["telegram_token"], 
        gemini_api_key=keys["gemini_api_key"]
    )
    
    bary_core.register_dynamic_agent(
        agent_id="@DFMB",
        archetype_path="archetypes/executor.json",
        agent_purpose="You are the File Manager Bot (DFMB). Your task is to navigate the file system and read the contents of files.",
        tools=[find_file, read_file_content]
    )

    bary_core.register_dynamic_agent(
        agent_id="@DTRB",
        archetype_path="archetypes/executor.json",
        agent_purpose="You are Task Runner Bot (DTRB). Your task is to execute commands in the PowerShell/CMD system console.",
        tools=[execute_shell_command]
    )
    
    await bary_core.start()

if __name__ == "__main__":
    asyncio.run(main())