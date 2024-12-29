from typing import List
from exa_py import Exa
from backend.models import ResearchPaper
from backend.config import get_settings
from backend.logger import logger
import math

settings = get_settings()


class ExaAPI:
    def __init__(self):
        self.exa = Exa(api_key=settings.EXA_API_KEY)
        self.max_results = settings.EXA_MAX_RESULTS
        self.use_hybrid = settings.EXA_USE_HYBRID_SEARCH
        self.neural_ratio = settings.EXA_NEURAL_RATIO

    def _parse_result(self, result: dict) -> ResearchPaper:
        """Parse a single result into a ResearchPaper model"""
        return ResearchPaper(
            id=result.id,
            url=result.url,
            title=result.title,
            author=result.author,
            published_date=result.published_date,
            summary=result.summary,
        )

    async def search_papers(self, query: str) -> List[ResearchPaper]:
        """
        Search for papers related to the query using Exa API
        """
        try:
            papers = []

            if self.use_hybrid:
                # Calculate number of results for each search type
                neural_count = math.ceil(self.max_results * self.neural_ratio)
                keyword_count = self.max_results - neural_count

                logger.info(
                    f"Performing hybrid search with {neural_count} neural and {keyword_count} keyword results"
                )

                # Perform hybrid search using search_and_contents
                results_neural = self.exa.search_and_contents(
                    query,
                    type="neural",
                    num_results=neural_count,
                    use_autoprompt=True,
                    category="research paper",
                    summary=True,
                )
                results_keyword = self.exa.search_and_contents(
                    query,
                    type="keyword",
                    num_results=keyword_count,
                    use_autoprompt=True,
                    category="research paper",
                    summary=True,
                )

                processed_neural = [
                    self._parse_result(result) for result in results_neural.results
                ]
                processed_keyword = [
                    self._parse_result(result) for result in results_keyword.results
                ]
                papers = processed_neural + processed_keyword

            else:
                # Perform neural-only search
                results = self.exa.search_and_contents(
                    query,
                    num_results=self.max_results,
                    use_autoprompt=True,
                    category="research paper",
                    summary=True,
                    type="auto",
                )

                # Process results
                for result in results.results:
                    papers.append(self._parse_result(result))

            logger.info(f"Found {len(papers)} papers for query: {query}")
            return papers

        except Exception as e:
            logger.error(f"Exa API error: {str(e)}")
            raise
