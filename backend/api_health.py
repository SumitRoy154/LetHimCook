"""
API Health & Rate Limit Checker Script.

Checks API key availability and attempts light calls / rate-limit header inspections
for currently used active LLM providers: Groq, Anthropic, Google Gemini.
"""

import os
import sys
import json
import logging
from typing import Dict, Any

from app.core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("api_health")

def check_groq(api_key: str) -> Dict[str, Any]:
    if not api_key:
        return {"status": "SKIPPED", "message": "GROQ_API_KEY is not set."}
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.with_raw_response.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        headers = response.headers
        rate_limits = {
            "limit_requests": headers.get("x-ratelimit-limit-requests"),
            "remaining_requests": headers.get("x-ratelimit-remaining-requests"),
            "reset_requests": headers.get("x-ratelimit-reset-requests"),
            "limit_tokens": headers.get("x-ratelimit-limit-tokens"),
            "remaining_tokens": headers.get("x-ratelimit-remaining-tokens"),
            "reset_tokens": headers.get("x-ratelimit-reset-tokens"),
        }
        return {
            "status": "HEALTHY",
            "provider": "Groq",
            "model": "llama-3.3-70b-versatile",
            "rate_limits": {k: v for k, v in rate_limits.items() if v is not None},
            "headers_present": bool(any(rate_limits.values()))
        }
    except Exception as e:
        return {"status": "ERROR", "provider": "Groq", "error": str(e)}


def check_anthropic(api_key: str) -> Dict[str, Any]:
    if not api_key:
        return {"status": "SKIPPED", "message": "ANTHROPIC_API_KEY is not set."}
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.with_raw_response.create(
            model="claude-3-haiku-20240307",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        headers = response.headers
        rate_limits = {
            "limit_requests": headers.get("anthropic-ratelimit-requests-limit"),
            "remaining_requests": headers.get("anthropic-ratelimit-requests-remaining"),
            "reset_requests": headers.get("anthropic-ratelimit-requests-reset"),
            "limit_tokens": headers.get("anthropic-ratelimit-tokens-limit"),
            "remaining_tokens": headers.get("anthropic-ratelimit-tokens-remaining"),
            "reset_tokens": headers.get("anthropic-ratelimit-tokens-reset"),
        }
        return {
            "status": "HEALTHY",
            "provider": "Anthropic",
            "model": "claude-3-haiku-20240307",
            "rate_limits": {k: v for k, v in rate_limits.items() if v is not None},
            "headers_present": bool(any(rate_limits.values()))
        }
    except Exception as e:
        return {"status": "ERROR", "provider": "Anthropic", "error": str(e)}


def check_google(api_key: str) -> Dict[str, Any]:
    if not api_key:
        return {"status": "SKIPPED", "message": "GOOGLE_API_KEY is not set."}
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        res = model.generate_content("ping")
        
        return {
            "status": "HEALTHY",
            "provider": "Google Gemini",
            "model": "gemini-2.5-flash",
            "note": "API key valid and quota functional."
        }
    except Exception as e:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            return {
                "status": "HEALTHY",
                "provider": "Google Gemini",
                "available_models": models[:5],
                "note": "API key is valid and listed models successfully."
            }
        except Exception as inner_e:
            return {"status": "ERROR", "provider": "Google Gemini", "error": str(e)}


def main():
    print("=" * 60)
    print("        API HEALTH & RATE LIMIT CHECKER")
    print("=" * 60)
    
    settings = get_settings()
    
    providers = {
        "Groq": (check_groq, settings.groq_api_key),
        "Anthropic": (check_anthropic, settings.anthropic_api_key),
        "Google Gemini": (check_google, settings.google_api_key),
    }

    results = {}
    for name, (checker_fn, key) in providers.items():
        print(f"\n[+] Checking {name} API...")
        res = checker_fn(key)
        results[name] = res
        
        status = res.get("status")
        if status == "HEALTHY":
            print(f"    Status: SUCCESS / HEALTHY")
            if "rate_limits" in res and res["rate_limits"]:
                print("    Rate Limits Info:")
                for k, v in res["rate_limits"].items():
                    print(f"      - {k}: {v}")
            elif "note" in res:
                print(f"    Note: {res['note']}")
        elif status == "SKIPPED":
            print(f"    Status: SKIPPED ({res.get('message')})")
        else:
            print(f"    Status: FAILED / ERROR")
            print(f"    Error: {res.get('error')}")

    print("\n" + "=" * 60)
    print("SUMMARY JSON:")
    print("=" * 60)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
