# app/services/rag_service.py
from app.services.vector_store import search_sops
from app.core.ai_client import generate_completion


def answer_sop_question(question: str) -> dict:
    """
    Executes grounded RAG:
    1. Retrieves top-k matching SOP passages from Qdrant.
    2. Builds an evidence-backed prompt with strict anti-hallucination rules.
    3. Calls local LLM to produce a cited response.
    """
    # 1. Retrieve evidence from Qdrant
    retrieved_chunks = search_sops(query=question, top_k=2)

    # If nothing retrieved or low similarity
    if not retrieved_chunks or retrieved_chunks[0]["score"] < 0.40:
        return {
            "answer": "Insufficient evidence found in Standard Operating Procedures to answer this question.",
            "evidence_sufficient": False,
            "citations": [],
            "retrieved_evidence": []
        }

    # 2. Construct context blocks
    evidence_text = ""
    for idx, chunk in enumerate(retrieved_chunks, 1):
        evidence_text += (
            f"\n[EVIDENCE #{idx}] Document: {chunk['sop_id']} | {chunk['section']}\n"
            f"Content: {chunk['text']}\n"
        )

    # 3. System instructions with anti-hallucination guardrail
    system_instruction = (
        "You are an educational Pharmaceutical Quality Compliance Auditor. "
        "Answer the user's question using ONLY the provided evidence passages. "
        "MANDATES:\n"
        "1. Do not use outside knowledge. Do not invent numbers or specifications.\n"
        "2. If the evidence does not clearly contain the answer, set 'evidence_sufficient' to false.\n"
        "3. Every factual statement must cite the document section from the evidence.\n"
        "Output MUST be valid JSON with this schema:\n"
        "{\n"
        '  "answer": "Clear factual answer with citations",\n'
        '  "citations": ["List of cited sections, e.g. SOP-701 Section 4.2"],\n'
        '  "evidence_sufficient": true,\n'
        '  "confidence": "HIGH" | "MEDIUM" | "LOW"\n'
        "}"
    )

    user_prompt = (
        f"EVIDENCE PASSAGES:\n{evidence_text}\n\n"
        f"USER QUESTION: {question}\n\n"
        "Generate the grounded compliance answer in JSON."
    )

    # 4. Generate completion via unified gateway
    llm_result = generate_completion(
        system_prompt=system_instruction,
        user_prompt=user_prompt,
        response_format="json",
        temperature=0.1  # Low temperature for strict factual adherence
    )

    if not llm_result["success"]:
        return {
            "answer": f"AI service error: {llm_result['error']}",
            "evidence_sufficient": False,
            "citations": [],
            "retrieved_evidence": retrieved_chunks
        }

    parsed = llm_result["content"]
    parsed["retrieved_evidence"] = retrieved_chunks
    return parsed