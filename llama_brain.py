import os
import ollama
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

class brain:
    def __init__(self,
                 model_name: str = "qwen3:14b",
                 prompts_dir: str = "prompts",
                 temperature: float = 0.1):
        self.model_name = model_name
        self.temperature = temperature

        self.conversation_history = []
        self.max_history_lenght = 10

        self.prompts_dir = Path(__file__).parent / prompts_dir
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Папка с промптами не найдена: {self.prompts_dir}")

        self.prompts = self._load_all_prompts()

        self._check_model()

    def _load_prompt(self, filename: str) -> str:
        filepath = self.prompts_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(f"Загружен: {filename}")
                return content
        except FileNotFoundError:
            print(f"Файл {filename} не найден")
            return ""
        except Exception as e:
            print(f"Ошибка загрузки {filename}: {e}")
            return ""

    def _load_all_prompts(self) -> Dict[str, str]:
        prompts = {}

        for filepath in self.prompts_dir.glob("*.txt"):
            prompt_name = filepath.stem
            prompts[prompt_name] = self._load_prompt(filepath.name)

        print(f"Всего загружено промптов: {len(prompts)}")

        return prompts

    def _check_model(self):
        try:
            ollama.show(self.model_name)
            print(f"Модель {self.model_name} доступна")
        except Exception as e:
            print(f"Модель {self.model_name} не найдена")
            raise

    def build_messages(self,
                       user_text: str,
                       system_prompt: Optional[str] = None,
                       include_examples: bool = True) -> List[Dict[str, str]]:

        messages = []

        system_content = system_prompt if system_prompt else self.prompts.get("system", "")

        if include_examples and "examples_commands" in self.prompts:
                system_content += "\n\n" + self.prompts["examples_commands"]

        messages.append({"role": "system", "content": system_content})
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_text})

        return messages

    def ask(self,
            user_text: str,
            system_prompt: Optional[str] = None,
            include_examples: bool = True,
            temperature: Optional[float] = None) -> str:

        messages = self.build_messages(user_text, system_prompt, include_examples)

        temp = temperature if temperature is not None else self.temperature

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    'temperature': temp,
                    # 'num_predict': max_tokens,
                    'stop': ['<|endoftext|>', '<|im_end|>', '<|end|>', 'User:', '\n\n\n'],
                    'repeat_penalty': 1.1
                }
            )
            answer = response['message']['content']
            return answer

        except Exception as e:
            print(f"Ошибка при запуске модели: {e}")
            return ""

    def ask_json(self,
                 user_text: str,
                 system_prompt: Optional[str] = None,
                 **kwargs) -> Optional[Dict[str, Any]]:
        response = self.ask(user_text, system_prompt, **kwargs)
        print(response)

        try:
            cleaned = response.strip().strip('```').strip()
            if cleaned.startswith('{') and cleaned.endswith('}'):
                return json.loads(cleaned)
            return response
        except json.JSONDecodeError:
            return None

    """======[Добавляет диалог в историю]======"""
    def add_to_history(self, user_text, assistant_response):
        self.conversation_history.append({"role": "user", "content": user_text})
        self.conversation_history.append({"role": "assistant", "content": assistant_response})

        max_pairs = self.max_history_lenght * 2
        if len(self.conversation_history) > max_pairs:
            self.convrsation_history = self.conversation_history[-max_pairs:]

    """======[Не реализовано]======"""
    def reload_prompts(self):
        self.prompts = self._load_all_prompts()