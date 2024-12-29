from typing import Dict, Any
from braintrust import LLMClassifier


def yes_no_scorer(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score exact match between predicted and expected yes/no answers
    """
    return {
        "name": "YesNo Match",
        "score": 1.0 if args["output"].lower() == args["expected"].lower() else 0.0,
    }


def explanation_quality_scorer(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score quality of explanation using LLM classifier
    """
    prompt = f"""Rate the quality of this explanation for why the answer is {args['expected']}:

{args['explanation']}

Consider:
1. Does it cite specific papers and their findings?
2. Does it explain how those findings answer the question?
3. Are the citations relevant to the question?

Choose one:
A) High quality - Cites multiple relevant papers and clearly explains their findings (Score: 1.0)
B) Medium quality - Cites papers but explanation could be clearer (Score: 0.5) 
C) Low quality - Missing citations or unclear explanation (Score: 0.0)
"""

    classifier = LLMClassifier(
        name="Explanation Quality",
        prompt=prompt,
        choices={"A": 1.0, "B": 0.5, "C": 0.0},
    )

    return classifier(args)
