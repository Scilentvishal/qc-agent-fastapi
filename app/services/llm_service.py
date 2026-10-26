# app/services/llm_service.py
import json
from app.core.ai_client import generate_completion


def explain_qc_findings_with_llm(batch_id: str, compound_name: str, audit_report: dict) -> dict:
    """
    Calls unified AI gateway to generate an educational audit summary.
    Works seamlessly across Ollama and Gemini.
    """
    system_instruction = (
        "You are an educational Pharmaceutical QC Assistant. "
        "Analyze the provided batch audit report. "
        "Explain the deviations in clear scientific terms and recommend human investigation steps. "
        "SAFETY MANDATE: Never authorize release. State clearly that human quality review is required. "
        "Output MUST be a single valid JSON object matching this schema:\n"
        "{\n"
        '  "summary": "High-level summary of batch quality status",\n'
        '  "critical_concerns": ["list of specific deviations"],\n'
        '  "recommended_actions": ["list of concrete investigation steps"],\n'
        '  "requires_human_signoff": true\n'
        "}"
    )

    user_prompt = (
        f"Batch Identifier: {batch_id}\n"
        f"Compound: {compound_name}\n"
        f"Deterministic Audit Report:\n"
        f"{json.dumps(audit_report, indent=2)}\n\n"
        "Generate the structured JSON evaluation."
    )

    result = generate_completion(
        system_prompt=system_instruction,
        user_prompt=user_prompt,
        response_format="json"
    )

    return {
        "success": result["success"],
        "model_used": f"{result['provider']}:{result['model']}",
        "analysis": result["content"],
        "error": result["error"]
    }