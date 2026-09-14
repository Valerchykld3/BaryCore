import json
from google import genai
from google.genai import types as genai_types

class DynamicEngine:
    def __init__(self, api_key: str, archetype_json_path: str, agent_purpose: str, tools: list):
        self.client = genai.Client(api_key=api_key)
        
        with open(archetype_json_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            
        base_instruction = config_data.get("system_instruction", "")
        self.archetype_name = config_data.get("archetype", "Unknown")
        
        full_instruction = f"{base_instruction}\n\nSpecialization:\n{agent_purpose}"
        
        config = genai_types.GenerateContentConfig(
            system_instruction=full_instruction,
            temperature=0.0,
            tools=tools,
        )
        self.chat_session = self.client.chats.create(
            model='gemini-3.6-flash', 
            config=config
        )

    def process_request(self, goal_instruction: str) -> str:
        response = self.chat_session.send_message(goal_instruction)
        return response.text