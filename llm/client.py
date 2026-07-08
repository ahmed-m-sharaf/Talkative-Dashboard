import os
import logging

import instructor
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger("TalkativeDashboard.LLMClient")


class LLMClient:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        self.current_client_idx = 0

        possible_keys = [
            os.getenv("GROQ_API_KEY"),
            os.getenv("GROQ_API_KEY_2"),
            os.getenv("GROQ_API_KEY_3"),
        ]

        self.api_keys = []
        for k in possible_keys:
            if k and k.strip() and not k.strip().startswith("gsk_YOUR_"):
                self.api_keys.append(k.strip())

        if not self.api_keys:
            fallback = os.getenv("GROQ_API_KEY")
            if fallback:
                self.api_keys.append(fallback)
            else:
                self.api_keys.append("NO_KEY_DEFINED")

        self.clients = []
        for key in self.api_keys:
            openai_client = OpenAI(
                api_key=key,
                base_url="https://api.groq.com/openai/v1",
                timeout=3.0,
            )
            inst_client = instructor.from_openai(
                openai_client,
                mode=instructor.Mode.JSON,
            )
            self.clients.append(inst_client)

        logger.info(f"Initialized LLMClient with {len(self.clients)} Groq API key(s).")

    def create_completion(self, response_model, messages, max_retries=1, **kwargs):
        """
        Creates a structured chat completion using Instructor. 
        Automatically falls back/rotates to alternative Groq keys if a rate limit (429) or connection error occurs.
        """
        if not self.clients:
            raise ValueError("No Groq clients initialized.")

        last_exception = None
        num_clients = len(self.clients)

        for attempt in range(num_clients):
            client_idx = (self.current_client_idx + attempt) % num_clients
            client = self.clients[client_idx]
            
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    response_model=response_model,
                    messages=messages,
                    max_retries=max_retries,
                    **kwargs
                )
                self.current_client_idx = client_idx
                return response
            except Exception as e:
                logger.warning(
                    f"Groq API call failed using client key index {client_idx}. Error: {e}"
                )
                last_exception = e
                continue

        logger.error("All available Groq API keys failed or rate-limited.")
        if last_exception is not None:
            raise last_exception
        raise ValueError("No Groq clients successfully completed the request.")


llm_client = LLMClient()