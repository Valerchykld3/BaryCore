import asyncio
import json
from core.base_script import BaryCoreBase
from tools.executor import list_directory, find_file, read_file_content, create_directory, create_file, edit_file, copy_item, move_item, delete_item, get_file_info, execute_shell_command, check_process_status, kill_process, get_system_resources
from tools.integrator import search_drive, list_drive_directory, read_drive_file, create_drive_folder, batch_move_drive_items, create_drive_file, copy_drive_item, move_drive_item, delete_drive_item, get_drive_item_info, upload_to_drive, upload_folder_to_drive, download_from_drive, share_drive_file, read_unread_emails, get_mailbox_status, create_draft
from tools.analyst import get_entity_from_cache, get_channel_history

async def main():
    with open("KEYS.json", "r", encoding="utf-8") as f:
        keys = json.load(f)

    bary_core = BaryCoreBase(
        telegram_token=keys["telegram_token"], 
        gemini_api_key=keys["gemini_api_key"]
    )

    # Executors

    bary_core.register_dynamic_agent(
        agent_id="@DFMB",
        full_name="File Manager Bot",
        archetype_path="archetypes/executor.json",
        agent_purpose="You are the File Manager Bot (DFMB). Your task is to navigate the file system and read the contents of files.",
        tools=[list_directory, find_file, read_file_content, create_directory, create_file, edit_file, copy_item, move_item, delete_item, get_file_info],
        model_name="gemini-3.8-flash"
    )

    bary_core.register_dynamic_agent(
        agent_id="@DTRB",
        full_name="Task Runner Bot",
        archetype_path="archetypes/executor.json",
        agent_purpose="You are Task Runner Bot (DTRB). Your task is to execute commands in the PowerShell/CMD system console.",
        tools=[execute_shell_command, check_process_status, kill_process, get_system_resources],
        model_name="gemini-3.8-flash"
    )

    # Integrators

    bary_core.register_dynamic_agent(
        agent_id="@DGDB",
        full_name="Google Drive Bot",
        archetype_path="archetypes/integrator.json",
        agent_purpose="You are Google Cloud Bot (DGDB). Your task is to interact with Google Drive API to search, read, and manipulate cloud files.",
        tools=[search_drive, list_drive_directory, read_drive_file, create_drive_folder, batch_move_drive_items, create_drive_file, copy_drive_item, 
               move_drive_item, delete_drive_item, get_drive_item_info, upload_to_drive, upload_folder_to_drive, 
               download_from_drive, share_drive_file],
        model_name="gemini-3.8-flash"
    )

    bary_core.register_static_agent(
        agent_id="@SGRB",
        full_name="Gmail Reader Bot",
        commands_map={
            "unread": read_unread_emails,
            "status": get_mailbox_status,
            "draft": create_draft,
        }
    )

    # Analysts

    bary_core.register_dynamic_agent(
        agent_id="@DMSB",
        full_name="Math Solver Bot",
        archetype_path="archetypes/analyst.json",
        agent_purpose="You are Math Solver Bot (DMSB), a Dynamic Analyst agent. "
            "Your task is to solve problems in higher mathematics and theoretical physics step-by-step. "
            "Provide detailed analytical derivations with full intermediate steps. "
            "Represent formulas and derivations using rich Unicode symbols "
            "and wrap multi-line mathematical derivations inside code blocks using ``` ... ``` for proper alignment. "
            "Provide explanations in clear natural text. Never change local or external states.",
        tools=[],
        model_name="gemini-3.1-pro-preview"
    )

    bary_core.register_dynamic_agent(
        agent_id="@DNIB",
        full_name="News Intercept Bot",
        archetype_path="archetypes/analyst.json",
        agent_purpose="You are the News Intercept Bot (DNIB). Your task is to fetch recent news and posts from user-specified "
            "Telegram channels, deeply analyze them, and provide structured, concise summaries or exact information based on user "
            "requests. Filter out ads and irrelevant noise.",
        tools=[get_entity_from_cache, get_channel_history],
        model_name="gemini-3.1-pro-preview"
    )

    # Communicators
    
    await bary_core.start()

if __name__ == "__main__":
    asyncio.run(main())