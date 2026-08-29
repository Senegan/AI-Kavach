# SS — Self-Healing Sentinel

### Lightweight, Evidence-Driven Cyber-Reasoning System

SS (Self-Healing Sentinel) is an autonomous cyber-reasoning prototype designed to detect software vulnerabilities, collect independent evidence, generate a security patch using a local LLM, and verify that the proposed patch actually fixes the vulnerability.

The system follows a simple principle:

> **Never trust the AI-generated patch. Verify it.**

Instead of allowing an LLM to directly modify and accept code, SS creates a closed-loop pipeline:

```text
Target Project
      │
      ▼
Environment Profiling
      │
      ▼
Static Analysis
      │
      ▼
Unified Evidence Model (UEM)
      │
      ▼
Dynamic Verification
      │
      ▼
Local LLM Reasoning
      │
      ▼
Patch Candidate
      │
      ▼
Build Verification
      │
      ▼
Exploit Replay
      │
      ▼
Regression Testing
      │
      ▼
Security Rescan
      │
      ├── FAIL ──► Reject Patch
      │
      └── PASS ──► Accept Patch
```

---

## Current Prototype

The current prototype focuses on **C/C++ vulnerability detection and autonomous repair**.

Current demonstrated vulnerability:

```c
char buffer[16];
strcpy(buffer, input);
```

SS detects the unsafe `strcpy()` usage, reproduces the vulnerability using AddressSanitizer, sends the evidence to a local Qwen coding model, generates a repair candidate, and independently verifies the patch.

### Current pipeline

```text
C Source
   │
   ▼
Environment Profiler
   │
   ▼
Static Analyzer
   │
   ▼
Finding + Evidence
   │
   ▼
AddressSanitizer
   │
   ▼
Qwen2.5-Coder
   │
   ▼
Patched Source
   │
   ├── Build Test
   ├── Exploit Test
   ├── Regression Test
   └── Rescan
          │
          ▼
       ACCEPT
```

---

# Features

* Automatic target environment profiling
* C/C++ source detection
* Static vulnerability detection
* AddressSanitizer-based runtime verification
* Unified Evidence Model (UEM)
* Local LLM-based patch generation
* Ollama integration
* Automatic patch compilation
* Exploit replay
* Regression testing
* Post-patch security rescan
* Patch acceptance/rejection gate
* Local-first architecture
* No external LLM API required

---

# Why SS does not blindly trust the LLM

An LLM-generated patch is treated only as a **candidate repair**.

SS does not accept a patch simply because the model claims it is secure.

The patch must pass:

```text
             PATCH CANDIDATE
                    │
                    ▼
              BUILD PASS?
               /       \
             NO         YES
             │           │
          REJECT    EXPLOIT DEFEATED?
                         /       \
                       NO         YES
                       │           │
                    REJECT     REGRESSION
                                  │
                                  ▼
                               RESCAN
                                  │
                            ┌─────┴─────┐
                            ▼           ▼
                          FAIL        PASS
                            │           │
                         REJECT       ACCEPT
```

This prevents the LLM from being the final authority.

---

# Requirements

## Operating System

The prototype is designed for Linux.

Tested development environment:

```text
Ubuntu / WSL2
Python 3.10+
GCC
Ollama
```

The prototype can also be adapted to native Linux systems.

---

# Hardware

A GPU is **not required** for the basic prototype.

The local LLM runs through Ollama.

Recommended:

```text
RAM:     8 GB+
CPU:     Modern multi-core CPU
Storage: 5 GB+ free
```

A GPU can significantly improve LLM inference speed but is optional.

---

# Software Requirements

Install:

* Python 3
* GCC
* Git
* Ollama

---

# 1. Install Git

Ubuntu / Debian:

```bash
sudo apt update
sudo apt install git -y
```

Verify:

```bash
git --version
```

---

# 2. Install Python

```bash
sudo apt install python3 python3-pip python3-venv -y
```

Verify:

```bash
python3 --version
pip3 --version
```

Python 3.10+ is recommended.

---

# 3. Install GCC

```bash
sudo apt install build-essential -y
```

Verify:

```bash
gcc --version
```

AddressSanitizer support is required for the current C prototype.

Check:

```bash
gcc -fsanitize=address --version
```

---

# 4. Install Ollama

Install Ollama using the official installation method for your operating system.

After installation, verify:

```bash
ollama --version
```

Start the Ollama service if it is not already running:

```bash
ollama serve
```

Keep this terminal running.

Open another terminal for SS.

---

# 5. Download the local coding model

The prototype supports Qwen2.5-Coder through Ollama.

Recommended lightweight model:

```bash
ollama pull qwen2.5-coder:3b
```

Verify:

```bash
ollama list
```

Expected:

```text
NAME
qwen2.5-coder:3b
```

You can test the model:

```bash
ollama run qwen2.5-coder:3b
```

Then:

```text
Fix this C vulnerability:

char buffer[16];
strcpy(buffer, input);

Return the corrected code.
```

Exit:

```text
/bye
```

---

# Alternative Model

If the 3B model is unavailable or insufficient for a particular environment, a larger local coding model can be used.

For example:

```bash
ollama pull qwen2.5-coder:7b
```

The SS model adapter can be configured to use the locally available model.

The design intentionally keeps the LLM layer separate from the security verification layer.

---

# 6. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ss-prototype
```

If you already have the repository locally:

```bash
cd ss-prototype
```

---

# 7. Create a Python virtual environment

Recommended:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

You should now see something similar to:

```text
(.venv)
```

in your terminal.

---

# 8. Python Dependencies

The current prototype intentionally uses mostly Python standard-library modules.

The current implementation uses:

```text
json
urllib
subprocess
pathlib
dataclasses
re
shutil
sys
```

Therefore, **no external Python package is required for the current prototype**.

This is intentional because the project is designed around lightweight deployment.

---

# Project Structure

```text
ss-prototype/
│
├── main.py
│
├── core/
│   ├── __init__.py
│   ├── profiler.py
│   ├── analyzer.py
│   ├── uem.py
│   ├── llm.py
│   └── verifier.py
│
├── samples/
│   └── vulnerable.c
│
└── workspace/
```

### Components

| Component     | Purpose                                          |
| ------------- | ------------------------------------------------ |
| `main.py`     | Main orchestration pipeline                      |
| `profiler.py` | Detects target language/build environment        |
| `analyzer.py` | Performs initial static vulnerability detection  |
| `uem.py`      | Normalizes vulnerability evidence                |
| `llm.py`      | Communicates with local Ollama model             |
| `verifier.py` | Compilation, exploit and regression verification |
| `samples/`    | Vulnerable demonstration programs                |
| `workspace/`  | Generated binaries and patches                   |

---

# Running the Prototype

From the project directory:

```bash
python3 main.py samples
```

---

# Expected Output

A successful run should look similar to:

```text
======================================
 SS — SELF-HEALING SENTINEL
 Adaptive Evidence-Driven CRS
======================================

[1] Environment Profiling
    Languages : ['C']
    Build     : unknown
    Files     : 1

[2] Static Analysis
    Candidates found: 1
    buffer-overflow at samples/vulnerable.c:9

[3] Unified Evidence Model
    Initial Evidence Score: 0.20

[4] Dynamic Verification
    ✓ AddressSanitizer reproduced overflow
    Evidence Score: 0.50

[5] Local LLM Repair
    Candidate patch written to workspace/patched.c

[6] Patch Verification
    ✓ Build PASS
    ✓ Original exploit defeated
    ✓ Regression PASS
    ✓ Rescan PASS

======================================
 PATCH VERIFIED ✓
======================================

Proof:
  ✓ Build PASS
  ✓ Exploit defeated
  ✓ Regression PASS
  ✓ Rescan PASS

Decision: ACCEPT
```

The exact output may vary depending on the compiler and local LLM response.

---

# Testing the Vulnerable Program Manually

Before running SS, you can independently verify the vulnerability.

Compile:

```bash
gcc -g -O0 \
    -fsanitize=address \
    -fno-omit-frame-pointer \
    samples/vulnerable.c \
    -o workspace/original
```

Run normal input:

```bash
./workspace/original HELLO
```

Expected:

```text
Processed: HELLO
```

Now provide oversized input:

```bash
./workspace/original AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
```

AddressSanitizer should report a memory-safety violation such as:

```text
AddressSanitizer: stack-buffer-overflow
```

The exact diagnostic may vary by compiler/platform.

---

# Inspect the Generated Patch

After SS completes:

```bash
cat workspace/patched.c
```

Compare it with the original:

```bash
diff -u samples/vulnerable.c workspace/patched.c
```

For the demonstration vulnerability, the generated repair may replace:

```c
strcpy(buffer, input);
```

with a bounded operation such as:

```c
strncpy(buffer, input, sizeof(buffer) - 1);
buffer[sizeof(buffer) - 1] = '\0';
```

The LLM output is **not automatically trusted**.

The generated source must pass the verification pipeline.

---

# Testing the Generated Patch

Compile:

```bash
gcc -g -O0 \
    -fsanitize=address \
    -fno-omit-frame-pointer \
    workspace/patched.c \
    -o workspace/patched
```

Normal input:

```bash
./workspace/patched HELLO
```

Then test oversized input:

```bash
./workspace/patched AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
```

The patched program should no longer trigger the original AddressSanitizer overflow.

---

# Evidence Model

SS uses a Unified Evidence Model to combine evidence from different security tools.

Example:

```json
{
  "finding_id": "C-STRCPY-001",
  "vulnerability_type": "buffer-overflow",
  "severity": "high",
  "file": "samples/vulnerable.c",
  "line": 9,
  "evidence": [
    {
      "source": "static-analyzer",
      "type": "pattern",
      "strength": 0.20
    },
    {
      "source": "asan",
      "type": "runtime",
      "strength": 0.30
    }
  ],
  "evidence_score": 0.50
}
```

The evidence score is an engineering heuristic for deciding how much additional investigation is needed.

It is **not a statistical probability**.

Most importantly:

> Evidence score does not directly accept a patch.

Only independent verification can accept a patch.

---

# Security Verification Philosophy

SS separates:

### Reasoning

```text
What might be wrong?
What could fix it?
```

from:

### Verification

```text
Does it compile?
Does the exploit still work?
Does expected behavior remain?
Does the vulnerability remain after rescan?
```

This separation prevents an LLM hallucination from becoming an automatically trusted security patch.

---

# Failure Handling

If the generated patch fails compilation:

```text
LLM Patch
   ↓
Build FAIL
   ↓
REJECT
```

If the exploit still works:

```text
LLM Patch
   ↓
Build PASS
   ↓
Exploit PASS
   ↓
REJECT
```

If regression tests fail:

```text
LLM Patch
   ↓
Security PASS
   ↓
Regression FAIL
   ↓
REJECT
```

This provides the foundation for future counterexample-guided repair.

---

# Current Limitations

This repository is currently a **prototype**, not a production security platform.

Current limitations include:

* C/C++ static detection is currently rule-based.
* The current sample workflow uses AddressSanitizer.
* Regression tests are basic.
* Behavioral equivalence checking is not yet comprehensive.
* The current PoC is focused on memory-safety testing.
* Tool selection is still being expanded.
* Python analysis is planned as the next adapter.
* Additional languages and analysis engines are planned.
* The current evidence weights are heuristic and not statistically calibrated.

These limitations are intentional areas for further development.

---

# Planned Architecture

The intended architecture is language- and tool-independent:

```text
                 TARGET
                   │
                   ▼
          ENVIRONMENT PROFILER
                   │
                   ▼
             TOOL ROUTER
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
    Static      Dynamic      Fuzzer
    Analysis    Analysis
       │           │           │
       └───────────┼───────────┘
                   ▼
                  UEM
                   │
                   ▼
             LOCAL LLM
                   │
                   ▼
             PATCH CANDIDATE
                   │
                   ▼
           VERIFICATION GATE
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
     Build      Security    Regression
       │           │           │
       └───────────┼───────────┘
                   ▼
                 Rescan
                   │
              ┌────┴────┐
              ▼         ▼
            ACCEPT     REJECT
```

Future adapters can include:

```text
C / C++
Python
Java
Go
Rust
JavaScript / TypeScript
REST APIs
gRPC
Firmware
```

and analysis tools such as:

```text
Semgrep
Tree-sitter
AddressSanitizer
Fuzzers
Dependency scanners
Dynamic analysis engines
Regression harnesses
```

---

# Design Principles

## 1. Local First

Security-sensitive source code should not need to leave the execution environment for reasoning.

```text
Source Code
    ↓
Local Analysis
    ↓
Local LLM
    ↓
Local Verification
```

---

## 2. Tool-Agnostic Evidence

Different tools detect different classes of vulnerabilities.

Therefore, SS normalizes tool results into a common evidence representation instead of assuming that one scanner is sufficient.

---

## 3. LLM as Reasoner, Not Authority

The LLM proposes:

```text
Repair Candidate
```

The verification system decides:

```text
Accept / Reject
```

---

## 4. Fail Closed

When verification cannot prove that the patch is safe:

```text
UNKNOWN
   ↓
DO NOT ACCEPT
```

The system should prefer escalation/rejection over silently accepting an uncertain patch.

---

# Development Roadmap

### v0.1

* C vulnerability detection
* Static rules
* AddressSanitizer
* UEM
* Local Qwen model
* Patch generation
* Build verification
* Exploit replay
* Regression
* Rescan

### v0.2

* Behavioral regression testing
* Counterexample-guided repair
* Multiple vulnerability findings
* Better patch isolation
* Tool fallback mechanisms

### v0.3

* Python adapter
* Python AST analysis
* pytest-based verification

### v0.4

* Semgrep integration
* Tree-sitter integration
* Multi-tool evidence fusion

### v0.5

* Resource-aware model selection
* Fuzzer integration
* Improved adaptive orchestration

### Future

* Java / Go / Rust / JavaScript adapters
* API security analysis
* Firmware analysis
* Distributed sandbox execution
* Air-gapped deployment
* Large-scale regression corpus

---

# Responsible Use

This project is intended for:

* Authorized security testing
* Software vulnerability research
* Defensive cybersecurity research
* Secure software development
* Controlled sandbox environments
* Hackathon and educational experimentation

Do not run automated vulnerability discovery or exploitation against systems without authorization.

---

# License

Add your chosen license here.

For example:

```text
MIT License
```

if appropriate for your project.

---

# Project Status

**Prototype / Proof of Concept**

Current demonstrated capability:

```text
C vulnerability
      ↓
Static detection
      ↓
Runtime confirmation
      ↓
Local LLM repair
      ↓
Independent verification
      ↓
Verified patch
```

The long-term objective is an extensible cyber-reasoning system capable of autonomously adapting its analysis and verification strategy to unfamiliar software environments.
