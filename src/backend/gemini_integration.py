from typing import List
from backend.models import ResearchPaper
from backend.config import get_settings
from backend.logger import logger
from backend.utils import braintrust_acompletion

settings = get_settings()


class GeminiAPI:
    def __init__(self):
        self.model = settings.GEMINI_MODEL
        self.max_tokens = settings.GEMINI_MAX_TOKENS

    def _construct_prompt(self, question: str, papers: List[ResearchPaper]) -> str:
        """Construct the prompt for Gemini"""
        papers_text = "\n\n".join(
            [
                f"Paper: {p.title}\n"
                f"Author: {p.author if p.author else 'Unknown'}\n"
                f"Published Date: {p.published_date.strftime('%Y-%m-%d') if p.published_date else 'Unknown'}\n"
                f"Summary: {p.summary if p.summary else 'No summary available'}\n"
                f"URL: {p.url}"
                for p in papers
            ]
        )

        return f"""
    Your task is to check whether anyone has done the proposed research question. To aid you, you will also be provided with the results of a query of academic papers for this topic. You will be provided with the titles of any returned papers and a summary of each of them. Note, that you will always be provided with papers from the search term, even if the research query is novel. 
    Research Question: {question}

Relevant Papers:
{papers_text}

Please provide:
1. A clear YES/NO answer indicating if the research has been done before. 
2. A detailed explanation of your reasoning, citing specific papers
3. Include relevant paper URLs in your explanation
Only include papers that are relevant to the research question. Do not cite a paper that is not relevant to the research question.
Format your response as:
ANSWER: [YES/NO]
EXPLANATION: [Your detailed explanation with citations]"""

    async def check_novelty(self, question: str, papers: List[ResearchPaper]) -> dict:
        """
        Check if the research question is novel using Gemini
        """
        try:
            prompt = self._construct_prompt(question, papers)
            messages = [{"role": "user", "content": prompt}]

            # Use the braintrust_acompletion function
            response = await braintrust_acompletion(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
            )

            # Parse the response
            content = response.choices[0].message.content

            # Extract novelty and explanation
            novelty = "YES" if "ANSWER: YES" in content.upper() else "NO"
            explanation = (
                content.split("EXPLANATION:", 1)[1].strip()
                if "EXPLANATION:" in content
                else content
            )

            logger.info(f"Gemini response processed for question: {question[:50]}...")
            return {"novelty": novelty, "explanation": explanation}

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
