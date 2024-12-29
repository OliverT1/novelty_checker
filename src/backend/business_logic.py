from typing import Dict
from backend.models import NoveltyCheckResponse
from backend.exa_integration import ExaAPI
from backend.gemini_integration import GeminiAPI
from backend.logger import logger


class NoveltyChecker:
    def __init__(self):
        self.exa_api = ExaAPI()
        self.gemini_api = GeminiAPI()

    async def check_novelty(self, research_question: str) -> NoveltyCheckResponse:
        """
        Main business logic to check novelty of a research question
        """
        try:
            # 1. Search for relevant papers
            papers = await self.exa_api.search_papers(research_question)

            # 2. Use Gemini to analyze papers and determine novelty
            result = await self.gemini_api.check_novelty(research_question, papers)

            # 3. Construct response
            response = NoveltyCheckResponse(
                novelty=result["novelty"],
                explanation=result["explanation"],
                papers=papers,
            )

            logger.info(
                f"Novelty check completed for question: {research_question[:50]}..."
            )
            return response

        except Exception as e:
            logger.error(f"Error in novelty check: {str(e)}")
            raise
