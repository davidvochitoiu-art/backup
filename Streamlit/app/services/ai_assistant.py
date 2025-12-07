import requests
import json

class AIAssistant:
    """Handles communication with the local AI engine."""

    def __init__(self, model="phi3:mini"):
        self._model = model

    def ask(self, prompt: str):
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": self._model, "prompt": prompt},
            stream=True
        )

        reply = ""
        for line in res.iter_lines():
            if line:
                data = json.loads(line.decode())
                if "response" in data:
                    reply += data["response"]
        return reply
