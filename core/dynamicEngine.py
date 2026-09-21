import json
from google import genai
from google.genai import types as genai_types

class DynamicEngine:
    def __init__(self, api_key: str, archetype_json_path: str, agent_purpose: str, tools: list, model_name: str):
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)
        
        with open(archetype_json_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            
        base_instruction = config_data.get("system_instruction", "")
        self.archetype_name = config_data.get("archetype", "Unknown")
        
        full_instruction = f"{base_instruction}\n\nSpecialization:\n{agent_purpose}\n\nStrict formatting rule: Format your output strictly using HTML tags. Never use Markdown formatting."
        
        self.config = genai_types.GenerateContentConfig(
            system_instruction=full_instruction,
            temperature=0.0,
            tools=tools,
        )

        self.reset_session()

    def reset_session(self):
        self.chat_session = self.client.chats.create(
            model=self.model_name, 
            config=self.config
        )

    def process_request(self, goal_instruction: str) -> str:
        response = self.chat_session.send_message(goal_instruction)
    
        if response.candidates and response.candidates[0].content.parts:
            text_parts = [part.text for part in response.candidates[0].content.parts if part.text]
            if text_parts:
                return "\n".join(text_parts).strip()
            
        return "Task completed successfully (no text report provided)."