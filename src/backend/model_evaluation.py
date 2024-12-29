import pandas as pd
import json
from backend.exa_integration import ExaAPI
from backend.gemini_integration import GeminiAPI
from typing import Dict, List, Tuple
import time
from tqdm import tqdm
from backend.models import ResearchPaper
from datetime import datetime
import asyncio
import os


class ModelEvaluator:
    def __init__(self, test_data_path: str, split: str = "validation"):
        """
        Initialize the evaluator with test data.
        Args:
            test_data_path: Path to the CSV file containing the test data
            split: Which split to use ('validation' or 'test')
        """
        # Load the full dataset and filter for the specified split
        self.test_df = pd.read_csv(test_data_path)
        self.test_df = self.test_df[self.test_df["split"] == split]
        print(f"Using {len(self.test_df)} questions from {split} set")

        self.results_cache = {}
        self.gemini_api = GeminiAPI()
        self.exa_api = ExaAPI()

        # Create results directory if it doesn't exist
        self.results_dir = "results"
        os.makedirs(self.results_dir, exist_ok=True)

    async def evaluate_single_question(self, question: str, true_answer: str) -> Dict:
        """Evaluate a single question"""
        try:
            # Search using Exa API
            papers = await self.exa_api.search_papers(question)

            # Get Gemini's response using the same prompt structure as gemini_integration.py
            response = await self.gemini_api.check_novelty(question, papers)

            # Extract the YES/NO answer
            predicted_answer = "no" if response["novelty"].upper() == "NO" else "yes"

            # Calculate correctness
            is_correct = predicted_answer == true_answer

            return {
                "question": question,
                "true_answer": true_answer,
                "predicted_answer": predicted_answer,
                "is_correct": is_correct,
                "search_results": [
                    {
                        "title": paper.title,
                        "author": paper.author,
                        "published_date": (
                            paper.published_date.isoformat()
                            if paper.published_date
                            else None
                        ),
                        "summary": paper.summary,
                        "url": paper.url,
                    }
                    for paper in papers
                ],
                "full_explanation": response["explanation"],
            }

        except Exception as e:
            print(f"Error processing question: {question}")
            print(f"Error: {str(e)}")
            return None

    async def run_evaluation(
        self,
        max_results: int = 3,
        hybrid_search: bool = True,
        neural_ratio: float = 0.5,
        gemini_model: str = "gemini-pro",
        batch_size: int = 10,
        concurrent_limit: int = 5,  # Limit concurrent API calls
    ) -> Dict:
        """
        Run evaluation with specified parameters.
        Returns metrics including accuracy and detailed results.
        """
        # Configure Exa API settings
        self.exa_api.max_results = max_results
        self.exa_api.use_hybrid = hybrid_search
        self.exa_api.neural_ratio = neural_ratio

        # Create parameter key for caching (replace / with _ in model name)
        param_key = f"{max_results}_{hybrid_search}_{neural_ratio}_{gemini_model.replace('/', '_')}"

        # Prepare all questions
        questions = [
            (row["question"], row["yes_no"].lower())
            for _, row in self.test_df.iterrows()
        ]

        # Process questions in batches to avoid overwhelming the APIs
        results = []
        for i in range(0, len(questions), concurrent_limit):
            batch = questions[i : i + concurrent_limit]

            # Process batch concurrently
            batch_results = await asyncio.gather(
                *[
                    self.evaluate_single_question(question, true_answer)
                    for question, true_answer in batch
                ]
            )

            # Filter out None results (failed evaluations)
            batch_results = [r for r in batch_results if r is not None]
            results.extend(batch_results)

            # Save interim results
            if len(results) % batch_size == 0:
                self._save_interim_results(results, param_key)

        # Calculate metrics
        correct = sum(1 for r in results if r["is_correct"])
        total = len(results)
        accuracy = correct / total if total > 0 else 0

        metrics = {
            "accuracy": accuracy,
            "correct": correct,
            "total": total,
            "parameters": {
                "max_results": max_results,
                "hybrid_search": hybrid_search,
                "neural_ratio": neural_ratio,
                "gemini_model": gemini_model,
            },
            "detailed_results": results,
        }

        # Save final results
        self._save_final_results(metrics, param_key)

        return metrics

    def _save_interim_results(self, results: List[Dict], param_key: str):
        """Save interim results to avoid losing progress."""
        filepath = os.path.join(self.results_dir, f"interim_results_{param_key}.json")
        with open(filepath, "w") as f:
            json.dump(results, f)

    def _save_final_results(self, metrics: Dict, param_key: str):
        """Save final results with timestamps."""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filepath = os.path.join(
            self.results_dir, f"evaluation_results_{param_key}_{timestamp}.json"
        )
        with open(filepath, "w") as f:
            json.dump(metrics, f)
