from pathlib import Path
import re


class StaticAnalyzer:

    RULES = [
        {
            "id": "C-STRCPY-001",
            "pattern": r"\bstrcpy\s*\(",
            "type": "buffer-overflow",
            "severity": "high",
            "description": "Unbounded strcpy may write beyond destination buffer."
        },
        {
            "id": "C-STRCAT-001",
            "pattern": r"\bstrcat\s*\(",
            "type": "buffer-overflow",
            "severity": "high",
            "description": "Unbounded strcat may overflow destination buffer."
        },
        {
            "id": "C-PRINTF-001",
            "pattern": r"\bsprintf\s*\(",
            "type": "buffer-overflow",
            "severity": "high",
            "description": "sprintf does not enforce destination buffer size."
        },
    ]

    def analyze(self, source_files):

        findings = []

        for filename in source_files:

            path = Path(filename)

            if path.suffix.lower() not in {
                ".c", ".h", ".cpp", ".cc", ".cxx"
            }:
                continue

            try:
                content = path.read_text(errors="ignore")
            except Exception:
                continue

            for rule in self.RULES:

                for match in re.finditer(rule["pattern"], content):

                    line_number = content[:match.start()].count("\n") + 1

                    findings.append({
                        "rule_id": rule["id"],
                        "file": str(path),
                        "line": line_number,
                        "type": rule["type"],
                        "severity": rule["severity"],
                        "description": rule["description"],
                        "evidence": match.group(0),
                    })

        return findings
