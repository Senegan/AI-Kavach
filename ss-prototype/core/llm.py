import json
import urllib.request


class LocalLLM:

    def __init__(
        self,
        model="qwen2.5-coder:7b",
        endpoint="http://localhost:11434/api/generate"
    ):
        self.model = model
        self.endpoint = endpoint

    def generate_patch(self, finding, source_code):

        prompt = f"""
You are a secure software repair assistant.

Your task is to repair the vulnerability described below.

VULNERABILITY:
{json.dumps(finding, indent=2)}

SOURCE CODE:
{source_code}

Requirements:
1. Fix the identified vulnerability.
2. Preserve the existing intended behavior.
3. Make the smallest reasonable security fix.
4. Do not remove functionality just to hide the vulnerability.
5. Return ONLY the complete corrected source code.
6. Do not return explanations.
7. Do not use Markdown code fences.
"""

        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0
            }
        }).encode("utf-8")

        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json"
            }
        )

        with urllib.request.urlopen(request, timeout=300) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        response_text = result["response"].strip()

        # Remove accidental Markdown fences if the model ignores
        # the instruction and returns ```c ... ```
        if response_text.startswith("```"):
            lines = response_text.splitlines()

            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            response_text = "\n".join(lines).strip()

        return response_text