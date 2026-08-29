import sys
import shutil
from pathlib import Path

from core.profiler import EnvironmentProfiler
from core.analyzer import StaticAnalyzer
from core.uem import Finding
from core.llm import LocalLLM
from core.verifier import Verifier


class SelfHealingSentinel:

    def __init__(self):

        self.profiler = EnvironmentProfiler()
        self.analyzer = StaticAnalyzer()
        self.llm = LocalLLM()
        self.verifier = Verifier()

    def run(self, target):

        target = Path(target)

        print("\n======================================")
        print(" SS — SELF-HEALING SENTINEL")
        print(" Adaptive Evidence-Driven CRS")
        print("======================================\n")

        # --------------------------------------------------
        # STEP 1 — PROFILE
        # --------------------------------------------------

        print("[1] Environment Profiling")

        profile = self.profiler.profile(target)

        print(f"    Languages : {profile['languages']}")
        print(f"    Build     : {profile['build_system']}")
        print(f"    Files     : {len(profile['source_files'])}")

        # --------------------------------------------------
        # STEP 2 — STATIC ANALYSIS
        # --------------------------------------------------

        print("\n[2] Static Analysis")

        findings = self.analyzer.analyze(
            profile["source_files"]
        )

        if not findings:

            print("    No candidate vulnerabilities found.")
            return

        print(f"    Candidates found: {len(findings)}")

        raw = findings[0]

        print(
            f"    {raw['type']} "
            f"at {raw['file']}:{raw['line']}"
        )

        # --------------------------------------------------
        # STEP 3 — UEM
        # --------------------------------------------------

        finding = Finding(
            finding_id=raw["rule_id"],
            vulnerability_type=raw["type"],
            severity=raw["severity"],
            file=raw["file"],
            line=raw["line"]
        )

        finding.add_evidence(
            source="static-analyzer",
            evidence_type="pattern",
            description=raw["description"],
            strength=0.20
        )

        print("\n[3] Unified Evidence Model")

        print(
            f"    Initial Evidence Score: "
            f"{finding.evidence_score():.2f}"
        )

        # --------------------------------------------------
        # STEP 4 — RUNTIME VERIFICATION
        # --------------------------------------------------

        print("\n[4] Dynamic Verification")

        source = Path(raw["file"])

        binary = Path("workspace/original")

        success, error = self.verifier.compile_c(
            str(source),
            str(binary)
        )

        if not success:

            print("    Build failed.")
            print(error)

            return

        exploit = self.verifier.run(
            str(binary),
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        )

        if exploit["asan_error"]:

            print("    ✓ AddressSanitizer reproduced overflow")

            finding.add_evidence(
                source="asan",
                evidence_type="runtime",
                description="AddressSanitizer reproduced memory corruption.",
                strength=0.30
            )

        else:

            print("    Runtime vulnerability not reproduced.")

        print(
            f"    Evidence Score: "
            f"{finding.evidence_score():.2f}"
        )

        # --------------------------------------------------
        # STEP 5 — LLM REPAIR
        # --------------------------------------------------

        print("\n[5] Local LLM Repair")

        source_code = source.read_text()

        repaired_code = self.llm.generate_patch(
            finding.to_dict(),
            source_code
        )

        candidate = Path(
            "workspace/patched.c"
        )

        candidate.write_text(repaired_code)

        print(f"    Candidate patch written to {candidate}")

        # --------------------------------------------------
        # STEP 6 — PATCH FIREWALL / BUILD
        # --------------------------------------------------

        print("\n[6] Patch Verification")

        patched_binary = Path(
            "workspace/patched"
        )

        success, error = self.verifier.compile_c(
            str(candidate),
            str(patched_binary)
        )

        if not success:

            print("    ✗ PATCH REJECTED")
            print("    Build failed.")
            return

        print("    ✓ Build PASS")

        # --------------------------------------------------
        # STEP 7 — EXPLOIT REPLAY
        # --------------------------------------------------

        exploit_result = self.verifier.verify_exploit_defeated(
            str(patched_binary)
        )

        if not exploit_result["passed"]:

            print("    ✗ PATCH REJECTED")
            print("    Original exploit still succeeds.")

            return

        print("    ✓ Original exploit defeated")

        # --------------------------------------------------
        # STEP 8 — REGRESSION
        # --------------------------------------------------

        regression = self.verifier.regression_test(
            str(patched_binary)
        )

        if not regression["passed"]:

            print("    ✗ PATCH REJECTED")
            print("    Regression test failed.")

            return

        print("    ✓ Regression PASS")

        # --------------------------------------------------
        # STEP 9 — RESCAN
        # --------------------------------------------------

        rescan = self.analyzer.analyze(
            [str(candidate)]
        )

        dangerous = [
            x for x in rescan
            if x["type"] == raw["type"]
        ]

        if dangerous:

            print("    ✗ PATCH REJECTED")
            print("    Vulnerability pattern still detected.")

            return

        print("    ✓ Rescan PASS")

        # --------------------------------------------------
        # FINAL ACCEPTANCE
        # --------------------------------------------------

        print("\n======================================")
        print(" PATCH VERIFIED ✓")
        print("======================================")

        print("\nProof:")
        print("  ✓ Build PASS")
        print("  ✓ Exploit defeated")
        print("  ✓ Regression PASS")
        print("  ✓ Rescan PASS")
        print("\nDecision: ACCEPT")


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            "Usage: python3 main.py <target>"
        )

        sys.exit(1)

    SelfHealingSentinel().run(sys.argv[1])
