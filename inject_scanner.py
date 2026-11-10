
import os
import sys

SYSTEM_PROMPT_PATTERNS = [
    "SYSTEM_PROMPT =",
    "system_message =",
    '"role": "system"',
    "'role': 'system'"
]

INJECTION_PHRASES = [
    "ignore previous instructions",
    "you are now",
    "pretend you are",
    "act as if you have no restrictions"
]

def scan_repository():
    findings = []

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d != "venv" and d != ".git" and d != "__pycache__"]

        for filename in files:
            if not filename.endswith(".py"):
                continue

            path = os.path.join(root, filename)

            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read().lower()

                for pattern in SYSTEM_PROMPT_PATTERNS + INJECTION_PHRASES:
                    if pattern.lower() in content:
                        findings.append(f"{path}: detected pattern: {pattern}")

            except Exception as error:
                print(f"Could not scan {path}: {error}")

    return findings

if __name__ == "__main__":
    results = scan_repository()

    if results:
        print("AI PROMPT SECURITY SCAN FAILED")
        for finding in results:
            print(f"[HIGH] {finding}")
        sys.exit(1)

    print("AI PROMPT SECURITY SCAN PASSED")
    sys.exit(0)
