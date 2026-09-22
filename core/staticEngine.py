import html

class StaticEngine:
    def __init__(self, commands_map: dict, full_name: str):
        self.commands_map = commands_map
        self.full_name = full_name

    def process_request(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        for keyword, func in self.commands_map.items():
            if keyword in prompt_lower:
                try:
                    return func(prompt)
                except Exception as e:
                    return f"An error occurs: {html.escape(str(e))}"
                    
        return "The task is unclear 💤"