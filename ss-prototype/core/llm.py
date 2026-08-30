import difflib
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

    def _single_line(self, value):
        return " ".join(str(value).split()) if value else ""

    def _explain_change(self, old_line, new_line):
        old_text = self._single_line(old_line)
        new_text = self._single_line(new_line)

        if not old_text and new_text:
            if any(token in new_text.lower() for token in ["strlen", "sizeof", "if (", "if("]):
                return "Added a safety guard before the operation to prevent memory corruption and invalid access."
            return "Inserted a validation step to keep the code behavior safe and predictable."

        if not new_text and old_text:
            return "Removed the unsafe operation to avoid unchecked memory access or overflow risk."

        if any(token in old_text.lower() for token in ["strcpy", "strcat", "sprintf", "gets"]) or any(token in new_text.lower() for token in ["strcpy", "strcat", "sprintf", "gets"]):
            if any(token in new_text.lower() for token in ["strlen", "sizeof", "if (", "if("]):
                return "Added a bounds check and length validation before copying data so the fixed-size buffer cannot overflow."
            return "Replaced an unchecked copy with a safer operation to prevent a buffer overflow."

        if any(token in new_text.lower() for token in ["strlen", "sizeof", "<=", "<", "if ("]):
            return "Introduced a bounds check to validate data length before use."

        if "malloc" in old_text.lower() or "malloc" in new_text.lower():
            return "Adjusted allocation logic to keep the value within valid memory bounds."

        return "Updated the logic to enforce safer validation and reduce the chance of memory corruption."

    def describe_changes(self, previous_code, latest_code):
        previous_lines = previous_code.splitlines()
        latest_lines = latest_code.splitlines()

        matcher = difflib.SequenceMatcher(None, previous_lines, latest_lines)
        changes = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue

            old_block = "\n".join(previous_lines[i1:i2]).strip()
            new_block = "\n".join(latest_lines[j1:j2]).strip()

            old_lines = [line.strip() for line in old_block.splitlines() if line.strip()]
            new_lines = [line.strip() for line in new_block.splitlines() if line.strip()]

            if tag == "delete":
                for old_line in old_lines:
                    if not old_line.startswith(("//", "#")):
                        changes.append({
                            "prev": old_line,
                            "latest": "",
                            "explanation": self._explain_change(old_line, "")
                        })
                continue

            if tag == "insert":
                for new_line in new_lines:
                    if not new_line.startswith(("//", "#")):
                        changes.append({
                            "prev": "",
                            "latest": new_line,
                            "explanation": self._explain_change("", new_line)
                        })
                continue

            if tag == "replace":
                if not old_lines and not new_lines:
                    continue

                pair_count = max(len(old_lines), len(new_lines))
                for idx in range(pair_count):
                    prev_line = old_lines[idx] if idx < len(old_lines) else ""
                    latest_line = new_lines[idx] if idx < len(new_lines) else ""
                    if not prev_line.startswith(("//", "#")) and not latest_line.startswith(("//", "#")):
                        changes.append({
                            "prev": prev_line,
                            "latest": latest_line,
                            "explanation": self._explain_change(prev_line, latest_line)
                        })

        return changes

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