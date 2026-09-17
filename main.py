import asyncio
import json
from core.base_script import BaryCoreBase
from tools.executor import list_directory, find_file, read_file_content, create_directory, create_file, copy_item, move_item, delete_item, get_file_info, execute_shell_command, check_process_status, kill_process, get_system_resources
from tools.integrator import search_drive, list_drive_directory, read_drive_file, create_drive_folder, create_drive_file, copy_drive_item, move_drive_item, delete_drive_item, get_drive_item_info, upload_to_drive, upload_folder_to_drive, download_from_drive, share_drive_file

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
        tools=[list_directory, find_file, read_file_content, create_directory, create_file, copy_item, move_item, delete_item, get_file_info]
    )

    bary_core.register_dynamic_agent(
        agent_id="@DTRB",
        archetype_path="archetypes/executor.json",
        agent_purpose="You are Task Runner Bot (DTRB). Your task is to execute commands in the PowerShell/CMD system console.",
        tools=[execute_shell_command, check_process_status, kill_process, get_system_resources]
    )

    bary_core.register_dynamic_agent(
        agent_id="@DGDB",
        archetype_path="archetypes/integrator.json",
        agent_purpose="You are Google Cloud Bot (DGDB). Your task is to interact with Google Drive API to search, read, and manipulate cloud files.",
        tools=[search_drive, list_drive_directory, read_drive_file, create_drive_folder, create_drive_file, copy_drive_item, move_drive_item, delete_drive_item, get_drive_item_info, upload_to_drive, upload_folder_to_drive, download_from_drive, share_drive_file]
    )
    
    await bary_core.start()

if __name__ == "__main__":
    asyncio.run(main())