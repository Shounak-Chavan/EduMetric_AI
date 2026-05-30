from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import (
    gemini_llm,
    groq_llm,
)
from app.schemas.grading_result import (
    LLMGradingResult,
)

grading_prompt = ChatPromptTemplate.from_template(
    """
You are an expert academic evaluator.

Reference Solution:
{reference_solution}

Student Submission:
{submission}

Compare the student submission against the
reference solution.

Award marks between 0 and 10.

Return:
- marks
- feedback
"""
)


async def grade_text(
    reference_solution: str,
    submission: str,
):
    data = {
        "reference_solution": reference_solution,
        "submission": submission,
    }

    try:

        chain = (
            grading_prompt
            | groq_llm.with_structured_output(
                LLMGradingResult
            )
        )

        result = await chain.ainvoke(data)

        return result, "groq"

    except Exception:

        chain = (
            grading_prompt
            | gemini_llm.with_structured_output(
                LLMGradingResult
            )
        )

        result = await chain.ainvoke(data)

        return result, "gemini"