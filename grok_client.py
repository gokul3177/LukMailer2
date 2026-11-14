import json
import re
from openai import OpenAI

class GroqClient:
    PREFERRED_MODELS = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = model or self._select_best_model()

    def _select_best_model(self) -> str:
        try:
            available = {m.id for m in self.client.models.list().data}
            for pref in self.PREFERRED_MODELS:
                if pref in available:
                    return pref
            candidates = [
                m for m in available 
                if not any(x in m.lower() for x in ["whisper", "guard", "audio"])
            ]
            if candidates:
                return candidates[0]
        except Exception:
            pass
        return "openai/gpt-oss-120b"

    def test_connection(self) -> tuple[bool, str]:
        """Validates the Groq API key with a minimal request."""
        models_to_try = [self.model] + [m for m in self.PREFERRED_MODELS if m != self.model]
        last_error = ""
        for mod in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=mod,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "ping"}
                    ],
                    max_tokens=5
                )
                self.model = mod
                return True, f"Connection successful using model '{self.model}'"
            except Exception as e:
                last_error = str(e)
                # If model is not found, continue to next candidate
                if "model_not_found" in last_error or "does not exist" in last_error:
                    continue
                return False, last_error
        return False, last_error

    def process_and_draft(self, row_dict: dict, candidate_name: str, target_role: str) -> dict:
        """
        Inspects arbitrary spreadsheet columns from a row.
        Extracts recipient details and drafts an email.
        If required details are missing, marks valid=False with a clear reason.
        """
        # Convert row values to clean strings, ignoring NaN/None
        cleaned_row = {
            str(k): ("" if v is None or str(v).lower() == "nan" else str(v).strip())
            for k, v in row_dict.items()
        }

        system_prompt = (
            "You are an expert HR outreach coordinator. Your task is to analyze raw contact data "
            "from a user's spreadsheet, validate whether required recruiter info is present, "
            "and draft a high-converting, personalized cold email pitch.\n\n"
            "CRITICAL RULES:\n"
            "1. Identify the Recruiter/Contact Name, Email Address, Company Name, and Job Role.\n"
            "2. Validation requirement: A valid email address and an identifiable company/organization name MUST be present.\n"
            "3. If either the email address is missing/invalid, or company cannot be identified, or if critical info is absent, you MUST set \"valid\": false and explain the reason.\n"
            "4. If valid, draft:\n"
            "   - 'subject': Concise, professional subject line (e.g. 'Application: {role} - {candidate_name}').\n"
            "   - 'body': A compelling 3-4 sentence cold email. Reference the company and role. Explicitly state that the candidate's resume is attached. Include a polite call-to-action and sign off with candidate_name. Do NOT leave placeholder brackets like [Company] or [Your Name].\n"
            "5. You MUST respond with ONLY a valid JSON object in this exact schema:\n"
            "{\n"
            "  \"valid\": true or false,\n"
            "  \"reason\": \"explanation if valid is false, else empty string\",\n"
            "  \"recipient_name\": \"Name or Hiring Team\",\n"
            "  \"recipient_email\": \"clean email address\",\n"
            "  \"company\": \"Company Name\",\n"
            "  \"role\": \"Role Title\",\n"
            "  \"subject\": \"Subject line\",\n"
            "  \"body\": \"Full email body text\"\n"
            "}"
        )

        user_content = (
            f"Candidate Name: {candidate_name}\n"
            f"Target Role: {target_role}\n\n"
            f"Raw Spreadsheet Row Data:\n{json.dumps(cleaned_row, indent=2)}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            raw_result = response.choices[0].message.content
            parsed = json.loads(raw_result)

            # Extra validation: check if email looks somewhat valid
            email = parsed.get("recipient_email", "").strip()
            email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
            if not email or not re.match(email_pattern, email):
                return {
                    "valid": False,
                    "reason": f"No valid email found in row (extracted: '{email}')",
                    "raw_data": cleaned_row
                }

            return parsed
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Groq API error or parse failure: {str(e)}",
                "raw_data": cleaned_row
            }

# Backward compatibility alias
GrokClient = GroqClient

