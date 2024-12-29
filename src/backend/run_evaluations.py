from backend.model_evaluation import ModelEvaluator
from itertools import product
import asyncio
import braintrust
from braintrust import Eval
from typing import Dict, Any, List
from backend.scorers import YesNoScorer, ExplanationScorer
import click


class BraintrustEvaluator:
    def __init__(
        self, model_name: str, max_results: int, neural_ratio: float, split: str
    ):
        self.evaluator = ModelEvaluator(
            "notebooks/hasanyone_results_question_yes_no_split.csv", split=split
        )
        self.model_name = model_name
        self.max_results = max_results
        self.neural_ratio = neural_ratio

    async def async_evaluate_question(self, question_data: Dict) -> Dict[str, Any]:
        """
        Wrapper around existing evaluation logic that returns results in format expected by Braintrust
        """
        result = await self.evaluator.evaluate_single_question(
            question=question_data["question"],
            true_answer=question_data["true_answer"],
            max_results=self.max_results,
            hybrid_search=True,
            neural_ratio=self.neural_ratio,
            gemini_model=self.model_name,
        )

        return {
            "input": question_data["question"],
            "output": result["predicted_answer"],
            "expected": question_data["true_answer"],
            "explanation": result["full_explanation"],
            "search_results": result["search_results"],
            "metadata": {
                "is_correct": result["is_correct"],
                "num_results": len(result["search_results"]),
            },
        }


async def run_evaluation(
    model_name: str,
    max_results: int,
    neural_ratio: float,
    dataset_split: str,
    questions: List[Dict],
) -> None:
    """
    Run evaluation using Braintrust to track results and scores
    """
    # Initialize Braintrust experiment
    experiment_name = f"{model_name}_{max_results}_{neural_ratio}_{dataset_split}"

    evaluator = BraintrustEvaluator(
        model_name, max_results, neural_ratio, dataset_split
    )

    await Eval(
        "Novelty Checker",  # Project name
        experiment_name=experiment_name,
        data=questions,
        task=evaluator.async_evaluate_question,  # Use the evaluator's method
        scorers={
            "Binary Accuracy": YesNoScorer,
        },
        metadata={
            "model": model_name,
            "max_results": max_results,
            "neural_ratio": neural_ratio,
            "dataset_split": dataset_split,
        },
    )


@click.command()
@click.option(
    "--split",
    type=click.Choice(["validation", "test"]),
    default="validation",
    help="Dataset split to evaluate on",
)
@click.option(
    "--max-results",
    type=int,
    default=20,
    help="Maximum number of search results to use",
)
@click.option(
    "--neural-ratio",
    type=float,
    default=0.2,
    help="Ratio of neural search results to use",
)
@click.option(
    "--model",
    type=str,
    default="openai/gpt-4o",
    help="Model to use for evaluation",
)
async def main(split: str, max_results: int, neural_ratio: float, model: str):
    """Run model evaluation on specified dataset split"""
    print(f"\nRunning evaluation on {split} set with configuration:")
    print(f"max_results: {max_results}")
    print(f"neural_ratio: {neural_ratio}")
    print(f"model: {model}")

    # Initialize evaluator with specified split
    evaluator = ModelEvaluator(
        "notebooks/hasanyone_results_question_yes_no_split.csv", split=split
    )

    metrics = await evaluator.run_evaluation(
        max_results=max_results,
        hybrid_search=True,
        neural_ratio=neural_ratio,
        gemini_model=model,
        batch_size=50,
        concurrent_limit=50,
    )

    print(f"\nResults on {split} set:")
    print(f"Accuracy: {metrics['accuracy']:.2%}")


if __name__ == "__main__":
    asyncio.run(main())
