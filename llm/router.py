from llm.client import llm_client
from llm.prompts import SYSTEM_PROMPT
from schemas import RouterRequest


class Router:
    def route(self, user_prompt: str) -> RouterRequest:
        """
        Analyze the user's prompt and return the detected intent
        with the extracted parameters.
        """

        response: RouterRequest = llm_client.create_completion(
            response_model=RouterRequest,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        return response


router = Router()