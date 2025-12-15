"""
Te Pō Llama3 Routes
Direct LM Studio / Ollama integration via FastAPI
No separate MCP server needed — just HTTP endpoints.
"""

import os
import httpx
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration
LLAMA_URL = os.getenv("LLAMA_URL", "http://localhost:1234")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3")
LLAMA_TIMEOUT = 30.0

router = APIRouter(prefix="/awa/llama3", tags=["llama3-local"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CodeReviewRequest(BaseModel):
    """Request code review from Llama3."""
    code: str = Field(..., description="Code to review")
    language: str = Field(default="python", description="Programming language")
    focus: Optional[str] = Field(
        None, description="Specific areas to focus on (e.g., 'performance', 'security')")


class CodeReviewResponse(BaseModel):
    """Code review results."""
    language: str
    issues: list[str]
    suggestions: list[str]
    overall_score: int  # 1-10


class DocstringRequest(BaseModel):
    """Request docstring generation."""
    code: str = Field(..., description="Code to document")
    language: str = Field(default="python", description="Programming language")
    style: str = Field(
        default="numpy", description="Docstring style (numpy, google, sphinx)")


class DocstringResponse(BaseModel):
    """Generated docstring."""
    docstring: str
    language: str
    style: str


class ErrorAnalysisRequest(BaseModel):
    """Request error analysis from Llama3."""
    error: str = Field(..., description="Error message or traceback")
    context: Optional[str] = Field(
        None, description="Code context or error description")
    language: Optional[str] = Field(None, description="Programming language")


class ErrorAnalysisResponse(BaseModel):
    """Error analysis results."""
    root_cause: str
    explanation: str
    solutions: list[str]
    severity: str  # 'critical', 'warning', 'info'


# ============================================================================
# Helper: Call Llama3
# ============================================================================

async def call_llama3(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Call Llama3 via LM Studio or Ollama.

    Args:
        prompt: User prompt
        system_prompt: Optional system prompt

    Returns:
        Model response text

    Raises:
        HTTPException: If Llama3 is unavailable
    """
    try:
        async with httpx.AsyncClient(timeout=LLAMA_TIMEOUT) as client:
            response = await client.post(
                f"{LLAMA_URL}/api/generate",
                json={
                    "model": LLAMA_MODEL,
                    "prompt": prompt,
                    "system": system_prompt or "You are a helpful code assistant.",
                    "stream": False,
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            return response.json().get("response", "")
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"Llama3 not available at {LLAMA_URL}. Start LM Studio or Ollama first.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Llama3 error: {str(e)}")


# ============================================================================
# Routes: Code Review
# ============================================================================

@router.post("/review", response_model=CodeReviewResponse)
async def review_code(req: CodeReviewRequest) -> CodeReviewResponse:
    """Review code for issues and improvements."""
    prompt = f"""Review this {req.language} code for issues and improvements.
Focus on: {req.focus or 'general quality, performance, and maintainability'}.

Code:
```{req.language}
{req.code}
```

Provide:
1. List of issues found (as bullet points)
2. Suggestions for improvement (as bullet points)
3. Overall score (1-10)

Format your response as:
ISSUES:
- issue 1
- issue 2

SUGGESTIONS:
- suggestion 1
- suggestion 2

SCORE: X/10
"""

    response = await call_llama3(prompt)

    # Parse response (simple parsing)
    issues = []
    suggestions = []
    score = 5

    if "ISSUES:" in response:
        issues_section = response.split("ISSUES:")[1].split("SUGGESTIONS:")[0]
        issues = [line.strip().lstrip("- ")
                  for line in issues_section.strip().split("\n") if line.strip()]

    if "SUGGESTIONS:" in response:
        suggestions_section = response.split(
            "SUGGESTIONS:")[1].split("SCORE:")[0]
        suggestions = [line.strip().lstrip(
            "- ") for line in suggestions_section.strip().split("\n") if line.strip()]

    if "SCORE:" in response:
        try:
            score_text = response.split(
                "SCORE:")[1].strip().split("/")[0].strip()
            score = int(score_text)
        except:
            score = 5

    return CodeReviewResponse(
        language=req.language,
        issues=issues,
        suggestions=suggestions,
        overall_score=score,
    )


# ============================================================================
# Routes: Documentation
# ============================================================================

@router.post("/docstring", response_model=DocstringResponse)
async def generate_docstring(req: DocstringRequest) -> DocstringResponse:
    """Generate docstring for code."""
    prompt = f"""Generate a {req.style} style docstring for this {req.language} code:

```{req.language}
{req.code}
```

Provide ONLY the docstring (no code), properly formatted for {req.style} style.
"""

    response = await call_llama3(prompt)

    return DocstringResponse(
        docstring=response.strip(),
        language=req.language,
        style=req.style,
    )


# ============================================================================
# Routes: Error Analysis
# ============================================================================

@router.post("/analyze-error", response_model=ErrorAnalysisResponse)
async def analyze_error(req: ErrorAnalysisRequest) -> ErrorAnalysisResponse:
    """Analyze an error and suggest solutions."""
    context_text = f"Context:\n{req.context}" if req.context else ""
    lang_text = f"Language: {req.language}" if req.language else ""

    prompt = f"""Analyze this error and suggest solutions:

{lang_text}
{context_text}

Error:
{req.error}

Provide:
1. Root cause explanation
2. Why this error occurs
3. 2-3 solutions (as bullet points)
4. Severity (critical/warning/info)

Format as:
ROOT CAUSE: [explanation]
EXPLANATION: [why it happens]
SOLUTIONS:
- solution 1
- solution 2
SEVERITY: [critical/warning/info]
"""

    response = await call_llama3(prompt)

    # Parse response
    root_cause = ""
    explanation = ""
    solutions = []
    severity = "warning"

    if "ROOT CAUSE:" in response:
        root_cause = response.split("ROOT CAUSE:")[
            1].split("EXPLANATION:")[0].strip()

    if "EXPLANATION:" in response:
        explanation = response.split("EXPLANATION:")[
            1].split("SOLUTIONS:")[0].strip()

    if "SOLUTIONS:" in response:
        solutions_section = response.split(
            "SOLUTIONS:")[1].split("SEVERITY:")[0]
        solutions = [line.strip().lstrip("- ")
                     for line in solutions_section.strip().split("\n") if line.strip()]

    if "SEVERITY:" in response:
        severity_text = response.split(
            "SEVERITY:")[1].strip().split()[0].lower()
        severity = severity_text if severity_text in [
            "critical", "warning", "info"] else "warning"

    return ErrorAnalysisResponse(
        root_cause=root_cause or "Unable to determine root cause",
        explanation=explanation or response[:200],
        solutions=solutions or [
            "Check the error message carefully", "Search for similar issues"],
        severity=severity,
    )


# ============================================================================
# Health Check
# ============================================================================

@router.get("/status")
async def llama3_status():
    """Check if Llama3 is available."""
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            await client.get(f"{LLAMA_URL}/api/tags")
            return {
                "status": "online",
                "url": LLAMA_URL,
                "model": LLAMA_MODEL,
            }
    except:
        return {
            "status": "offline",
            "url": LLAMA_URL,
            "model": LLAMA_MODEL,
            "message": f"Llama3 not reachable at {LLAMA_URL}",
        }
