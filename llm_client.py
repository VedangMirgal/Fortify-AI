# llm_client.py

import os
import json
from typing import Any, Dict, List

from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()


class LLMClient:
    """
    Wrapper around Gemini LLM.

    - Loads API key from .env (GEMINI_API_KEY).
    - Model name can be overridden via GEMINI_MODEL_NAME.
      Defaults to: gemini-2.5-flash-lite
    """

    def __init__(self, model_name: str | None = None) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not found. Please add it to your .env file."
            )

        genai.configure(api_key=api_key)

        # Allow override from env, otherwise default to gemini-2.5-flash-lite
        if model_name is None:
            model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash-lite")

        self.model_name = model_name
        self.model = genai.GenerativeModel(self.model_name)

    # ---------- AI summary generation ----------

    def generate_system_summary(self, report_dict: Dict[str, Any]) -> str:
        """
        Use Gemini to generate an executive-style summary of the system report.
        """

        prompt = f"""
You are an expert Site Reliability Engineer and Security Architect.

You are given the JSON representation of an automated resilience & security analysis
for a software system.

Tasks:
1. Give a short overall assessment.
2. Highlight the top critical failure scenarios and why they matter.
3. Summarize the security posture.
4. Recommend 2–3 high-impact improvements.

Write a clear, structured executive summary for an engineering lead.
Do NOT repeat the raw JSON.

JSON:
{report_dict}
"""

        response = self.model.generate_content(prompt)
        text = getattr(response, "text", "") or ""
        return text.strip()

    # ---------- AI remediation suggestions ----------

    def generate_remediation_suggestions(
        self,
        report_dict: Dict[str, Any],
        base_suggestions: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Ask Gemini to propose additional remediation suggestions.

        Returns a list of dicts with keys:
        - category  (e.g. 'resilience' or 'security')
        - target    (e.g. 'Payment Service')
        - priority  ('high' | 'medium' | 'low')
        - title
        - details
        """

        prompt = f"""
You are an experienced Site Reliability Engineer and Security Architect.

You are given:
1) A JSON report about a system's resilience and security:
{report_dict}

2) A list of existing remediation suggestions (base_suggestions):
{base_suggestions}

Task:
- Propose 2–4 additional remediation suggestions that are NOT trivial duplicates.
- Focus on impactful, practical, architecture-level or configuration-level changes.
- Each suggestion MUST be a JSON object with the keys:
  - "category": "resilience" or "security"
  - "target": short component or system name
  - "priority": "high" or "medium" or "low"
  - "title": short descriptive title
  - "details": 1–3 sentences

Return ONLY a JSON array of these suggestion objects.
Do NOT include any explanation, markdown, or extra text.
"""

        response = self.model.generate_content(prompt)
        text = (getattr(response, "text", "") or "").strip()

        try:
            data = json.loads(text)
            if isinstance(data, list):
                return [d for d in data if isinstance(d, dict)]
        except Exception:
            # If the model didn't follow the JSON-only instruction, just ignore AI extras.
            return []

        return []
