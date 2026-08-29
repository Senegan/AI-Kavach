import subprocess
from pathlib import Path


class Verifier:

    def compile_c(self, source, binary):

        result = subprocess.run(
            [
                "gcc",
                "-g",
                "-O0",
                "-fsanitize=address",
                "-fno-omit-frame-pointer",
                source,
                "-o",
                binary
            ],
            capture_output=True,
            text=True
        )

        return result.returncode == 0, result.stderr

    def run(self, binary, argument):

        result = subprocess.run(
            [binary, argument],
            capture_output=True,
            text=True
        )

        output = result.stdout + result.stderr

        return {
            "returncode": result.returncode,
            "output": output,
            "asan_error": "AddressSanitizer" in output
        }

    def verify_exploit_defeated(self, binary):

        malicious_input = (
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        )

        result = self.run(binary, malicious_input)

        return {
            "passed": not result["asan_error"],
            "details": result
        }

    def regression_test(self, binary):

        tests = [
            "HELLO",
            "TEST",
            "normal input",
        ]

        results = []

        for test in tests:

            result = self.run(binary, test)

            results.append({
                "input": test,
                "passed": (
                    result["returncode"] == 0
                    and not result["asan_error"]
                )
            })

        return {
            "passed": all(x["passed"] for x in results),
            "tests": results
        }
