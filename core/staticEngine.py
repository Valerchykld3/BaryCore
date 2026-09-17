class StaticEngine:
    def __init__(self, commands_map: dict):
        self.commands_map = commands_map 

    def process_request(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        for keyword, func in self.commands_map.items():
            if keyword in prompt_lower:
                try:
                    return func()
                except Exception as e:
                    return f"An error occurs: {str(e)}"
                    
        return "The task is unclear 💤"