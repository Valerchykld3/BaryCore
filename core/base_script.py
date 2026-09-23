import asyncio
import html
import re
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from core.dynamicEngine import DynamicEngine
from core.staticEngine import StaticEngine

class BaryCoreBase:
    def __init__(self, telegram_token: str, gemini_api_key: str, allowed_user_id: int):
        self.bot = Bot(token=telegram_token)
        self.dp = Dispatcher()
        self.gemini_key = gemini_api_key
        self.allowed_user_id = allowed_user_id
        
        self.dp.message.register(self.handle_message)
        
        self.dynamic_agents = {}
        self.static_agents = {}

    def register_dynamic_agent(self, agent_id: str, full_name: str, archetype_path: str, agent_purpose: str, tools: list, model_name: str):
        self.dynamic_agents[agent_id] = DynamicEngine(
            api_key=self.gemini_key, 
            archetype_json_path=archetype_path, 
            agent_purpose=agent_purpose,
            tools=tools,
            model_name=model_name,
            full_name=full_name
        )

    def register_static_agent(self, agent_id: str, full_name: str, commands_map: dict):
        self.static_agents[agent_id] = StaticEngine(
            commands_map=commands_map,
            full_name=full_name
            )

    async def handle_message(self, message: Message):
        if message.chat.id != self.allowed_user_id:
            return
        
        print(f"Telegram forwarded the text: {message.text}")
        text = message.text
        if not text:
            return
            
        parts = text.split(maxsplit=1)
        agent_id = parts[0].strip(" ,.!?:;\n")
        user_prompt = parts[1] if len(parts) > 1 else ""

        if agent_id == "/agents":
            if not self.dynamic_agents and not self.static_agents:
                await message.reply("There are currently no active agents in orbit.")
                return
                
            response = "Active agents in orbit:\n\n"
            
            if self.dynamic_agents:
                response += "Dynamic:\n"
                for a_id, engine in self.dynamic_agents.items():
                    response += f"• {a_id} — {engine.full_name}\n"
                response += "\n"
                
            if self.static_agents:
                response += "Static:\n"
                for a_id, engine in self.static_agents.items():
                    response += f"• {a_id} — {engine.full_name}\n"
                
            await message.reply(response.strip())
            return

        if agent_id.startswith("@D"):
            if agent_id not in self.dynamic_agents:
                return
            await self._run_dynamic(agent_id, user_prompt, message)
            
        elif agent_id.startswith("@S"):
            if agent_id not in self.static_agents:
                return
            await self._run_static(agent_id, user_prompt, message)

    async def _run_dynamic(self, agent_id: str, prompt: str, message: Message):
        await message.reply("🎯 In progress")
        
        try:
            engine = self.dynamic_agents[agent_id]
            result = await asyncio.to_thread(engine.process_request, prompt)
            
            def format_for_tg_html(raw_text: str) -> str:
                parts = re.split(r'(```[\s\S]*?```)', raw_text)
                formatted = []
                for p in parts:
                    if p.startswith('```') and p.endswith('```'):
                        lines = p.split('\n')
                        body = '\n'.join(lines[1:-1]) if len(lines) > 2 else p.strip('`')
                        formatted.append(f"<pre>{html.escape(body)}</pre>")
                    else:
                        formatted.append(html.escape(p))
                return "".join(formatted)

            safe_output = format_for_tg_html(result)
            await message.reply(f"<b>{agent_id}:</b>\n\n{safe_output}", parse_mode="HTML")
            
            clean_result = result.strip()
            if clean_result.startswith("@"):
                parts = clean_result.split(maxsplit=1)
                next_agent_id = parts[0]
                next_prompt = parts[1] if len(parts) > 1 else ""
                
                if next_agent_id != agent_id:
                    if next_agent_id in self.dynamic_agents:
                        print(f"{agent_id} is handing over the task to {next_agent_id}...")
                        await self._run_dynamic(next_agent_id, next_prompt, message)
                    elif next_agent_id in self.static_agents:
                        print(f"{agent_id} is handing over the task to {next_agent_id}...")
                        await self._run_static(next_agent_id, next_prompt, message)
                    
        except Exception as e:
            safe_err = html.escape(str(e))
            await message.reply(f"🔧 <b>An error:</b>\n<pre>{safe_err}</pre>", parse_mode="HTML")
        finally:
            if agent_id in self.dynamic_agents:
                self.dynamic_agents[agent_id].reset_session()
                print(f"Session for {agent_id} successfully cleared.")

    async def _run_static(self, agent_id: str, prompt: str, message: Message):
        await message.reply("🎯 In progress")
        
        try:
            engine = self.static_agents[agent_id]
            result = await asyncio.to_thread(engine.process_request, prompt)

            safe_result = html.escape(result)
            await message.reply(f"<b>{agent_id}:</b>\n\n{safe_result}", parse_mode="HTML")
        except Exception as e:
            safe_error = html.escape(str(e))
            await message.reply(f"🛠 <b>An error:</b>\n<pre>{safe_error}</pre>", parse_mode="HTML")

    async def start(self):
        print("BaryCore Base starts...")
        await self.dp.start_polling(self.bot, drop_pending_updates=True)