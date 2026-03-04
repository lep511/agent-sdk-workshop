#!/usr/bin/env python3
"""
Pre-workshop health check. Run this before the workshop starts to catch
setup problems early — before the timed exercises begin.

    python check_setup.py

Exits 0 if everything's good, 1 if something needs fixing.
"""

import os
import sys
from pathlib import Path


# Keep this file importable on old Pythons so we can report the version error
# nicely instead of SyntaxError-ing on modern syntax.

REPO_ROOT = Path(__file__).parent
ENV_FILE = REPO_ROOT / ".env"
ENV_EXAMPLE = REPO_ROOT / ".env.example"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
GRAY = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"

if os.environ.get("NO_COLOR") == "1":
    GREEN = RED = YELLOW = GRAY = RESET = BOLD = ""


def ok(msg):
    print("  {}✓{} {}".format(GREEN, RESET, msg))


def fail(msg, hint=None):
    print("  {}✗{} {}".format(RED, RESET, msg))
    if hint:
        print("    {}→ {}{}".format(GRAY, hint, RESET))


def warn(msg):
    print("  {}!{} {}".format(YELLOW, RESET, msg))


def check_python_version():
    """Python 3.10+ is required for the SDK's modern type syntax."""
    v = sys.version_info
    version_str = "{}.{}.{}".format(v.major, v.minor, v.micro)
    if v.major == 3 and v.minor >= 10:
        ok("Python {} (need 3.10+)".format(version_str))
        return True
    fail(
        "Python {} is too old — need 3.10 or newer".format(version_str),
        "Try 'python3.10 check_setup.py' or 'python3.11 check_setup.py' if you have multiple versions installed",
    )
    return False


def check_env_file():
    """Verify .env exists (not just .env.example) and has a real-looking key."""
    if not ENV_FILE.exists():
        # Most common mistake: edited .env.example instead of copying it.
        example_content = ""
        if ENV_EXAMPLE.exists():
            example_content = ENV_EXAMPLE.read_text()
        if "sk-ant-api" in example_content:
            fail(
                ".env file not found — but it looks like you edited .env.example",
                "Run: cp .env.example .env  (then edit .env, not the example)",
            )
        else:
            fail(
                ".env file not found",
                "Run: cp .env.example .env  then edit .env and paste your API key",
            )
        return False

    content = ENV_FILE.read_text()
    if "ANTHROPIC_API_KEY" not in content:
        fail(".env exists but has no ANTHROPIC_API_KEY line")
        return False

    # Pull the key value without importing dotenv (which may not be installed yet)
    key_value = ""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("ANTHROPIC_API_KEY"):
            parts = line.split("=", 1)
            if len(parts) == 2:
                key_value = parts[1].strip().strip('"').strip("'")
            break

    if not key_value or key_value == "sk-ant-..." or len(key_value) < 20:
        fail(
            ".env has ANTHROPIC_API_KEY but it looks like a placeholder",
            "Edit .env and paste your real key after ANTHROPIC_API_KEY=",
        )
        return False

    ok(".env file exists with API key")
    return True


def check_sdk_import():
    """Verify claude_agent_sdk is installed and importable."""
    try:
        import claude_agent_sdk  # noqa: F401

        ok("claude_agent_sdk is installed")
        return True
    except ImportError as e:
        fail(
            "claude_agent_sdk is not installed: {}".format(e),
            "Run: pip install -r requirements.txt",
        )
        return False


def check_dotenv_import():
    """Verify python-dotenv is installed (needed to load .env)."""
    try:
        import dotenv  # noqa: F401

        ok("python-dotenv is installed")
        return True
    except ImportError:
        fail(
            "python-dotenv is not installed",
            "Run: pip install -r requirements.txt",
        )
        return False


def check_api_connectivity():
    """Make a tiny request to the API to confirm the key works."""
    try:
        from dotenv import load_dotenv

        load_dotenv(ENV_FILE)
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            fail("API key didn't load from .env")
            return False

        # Smallest possible request — just confirm the key is valid.
        import anthropic

        client = anthropic.Anthropic(api_key=key)
        client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1,
            messages=[{"role": "user", "content": "hi"}],
        )
        ok("API key works (test request succeeded)")
        return True
    except ImportError:
        # anthropic package might not be a direct dep — SDK wraps it.
        # Fall back to skipping the live test but not failing.
        warn("Skipping live API test (anthropic package not directly available)")
        return True
    except Exception as e:
        err_str = str(e)
        if "authentication" in err_str.lower() or "401" in err_str:
            fail(
                "API request failed — key is invalid or expired",
                "Double-check the key in .env matches what you were given",
            )
        elif "connection" in err_str.lower() or "timeout" in err_str.lower():
            fail(
                "API request failed — network issue",
                "Check your internet connection and try again",
            )
        else:
            fail("API test request failed: {}".format(err_str[:100]))
        return False


def main():
    print("\n{}Checking workshop setup...{}\n".format(BOLD, RESET))

    results = []

    # Python version first — if this fails, other checks may error.
    py_ok = check_python_version()
    results.append(py_ok)
    if not py_ok:
        # Still run the env check (doesn't need modern syntax) but skip imports.
        results.append(check_env_file())
        print()
        print("{}Fix the Python version first, then re-run this check.{}".format(
            YELLOW, RESET
        ))
        sys.exit(1)

    results.append(check_env_file())
    results.append(check_dotenv_import())
    results.append(check_sdk_import())
    results.append(check_api_connectivity())

    print()
    if all(results):
        print("{}{}✓ Ready for workshop{}".format(BOLD, GREEN, RESET))
        print("{}  Run: ./workshop demo{}".format(GRAY, RESET))
        sys.exit(0)
    else:
        failed = sum(1 for r in results if not r)
        print("{}{}✗ {} check(s) failed — fix the issues above and re-run{}".format(
            BOLD, RED, failed, RESET
        ))
        sys.exit(1)


if __name__ == "__main__":
    main()
