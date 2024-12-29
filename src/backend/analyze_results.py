import json
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import List, Dict
import numpy as np
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


def load_evaluation_results(results_dir: str) -> List[Dict]:
    """Load all evaluation results from the results directory"""
    results = []
    for filename in os.listdir(results_dir):
        if filename.startswith("evaluation_results_"):
            with open(os.path.join(results_dir, filename), "r") as f:
                result = json.load(f)
                # Extract parameters and detailed results
                params = result["parameters"]
                for detail in result["detailed_results"]:
                    results.append(
                        {
                            "accuracy": result["accuracy"],
                            "max_results": params["max_results"],
                            "hybrid_search": params["hybrid_search"],
                            "neural_ratio": params["neural_ratio"],
                            "gemini_model": params["gemini_model"],
                            "question": detail["question"],
                            "true_answer": detail["true_answer"],
                            "predicted_answer": detail["predicted_answer"],
                            "is_correct": detail["is_correct"],
                        }
                    )
    return results


def create_comparison_df(results: List[Dict]) -> pd.DataFrame:
    """Convert results to a DataFrame for analysis"""
    return pd.DataFrame(results)


def analyze_parameter_impact(df: pd.DataFrame):
    """Analyze the impact of each parameter on accuracy"""

    # Calculate mean accuracy for each parameter value
    parameter_impacts = {}

    for param in ["max_results", "hybrid_search", "neural_ratio"]:
        impact = df.groupby(param)["accuracy"].agg(["mean", "std", "count"]).round(4)
        parameter_impacts[param] = impact

        print(f"\nImpact of {param}:")
        print(impact)
        print("\nAbsolute difference in accuracy:")
        print(f"Max difference: {(impact['mean'].max() - impact['mean'].min()):.4f}")

    return parameter_impacts


def plot_parameter_impacts(df: pd.DataFrame, save_dir: str = "results"):
    """Create visualizations of parameter impacts"""

    # Set up the plotting style
    sns.set_style("whitegrid")

    # Create a figure with subplots for each parameter
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Plot for max_results
    sns.boxplot(x="max_results", y="accuracy", data=df, ax=axes[0])
    axes[0].set_title("Impact of max_results")
    axes[0].set_ylabel("Accuracy")

    # Plot for hybrid_search
    sns.boxplot(x="hybrid_search", y="accuracy", data=df, ax=axes[1])
    axes[1].set_title("Impact of hybrid_search")
    axes[1].set_ylabel("")

    # Plot for neural_ratio
    sns.boxplot(x="neural_ratio", y="accuracy", data=df, ax=axes[2])
    axes[2].set_title("Impact of neural_ratio")
    axes[2].set_ylabel("")

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "parameter_impacts.png"))
    plt.close()


def create_interaction_heatmap(df: pd.DataFrame, save_dir: str = "results"):
    """Create heatmaps showing parameter interactions"""

    # Create heatmaps for different parameter combinations
    param_pairs = [
        ("max_results", "neural_ratio"),
        ("max_results", "hybrid_search"),
        ("neural_ratio", "hybrid_search"),
    ]

    for param1, param2 in param_pairs:
        plt.figure(figsize=(10, 6))
        pivot_table = df.pivot_table(
            values="accuracy", index=param1, columns=param2, aggfunc="mean"
        )

        sns.heatmap(pivot_table, annot=True, fmt=".3f", cmap="YlOrRd")
        plt.title(f"Interaction between {param1} and {param2}")
        plt.savefig(os.path.join(save_dir, f"heatmap_{param1}_{param2}.png"))
        plt.close()


def create_confusion_matrix(df: pd.DataFrame, config: Dict, save_dir: str = "results"):
    """Create and save confusion matrix visualization for a specific configuration"""
    # Convert yes/no to 1/0 for confusion matrix
    label_map = {"yes": 1, "no": 0}
    y_true = [label_map[ans.lower()] for ans in df["true_answer"]]
    y_pred = [label_map[ans.lower()] for ans in df["predicted_answer"]]

    # Calculate confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Create figure and axis
    plt.figure(figsize=(8, 6))

    # Create confusion matrix display
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["No", "Yes"])

    # Plot confusion matrix
    disp.plot(cmap="Blues", values_format="d")

    # Create title with configuration details
    title = f"Confusion Matrix\n"
    title += f"Model: {config['gemini_model']}\n"
    title += (
        f"Max Results: {config['max_results']}, Neural Ratio: {config['neural_ratio']}"
    )
    plt.title(title)

    # Calculate metrics
    accuracy = (cm[0, 0] + cm[1, 1]) / cm.sum()
    precision = cm[1, 1] / (cm[1, 1] + cm[0, 1]) if (cm[1, 1] + cm[0, 1]) > 0 else 0
    recall = cm[1, 1] / (cm[1, 1] + cm[1, 0]) if (cm[1, 1] + cm[1, 0]) > 0 else 0
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    plt.figtext(
        0.02,
        0.02,
        f"Accuracy: {accuracy:.3f}\nPrecision: {precision:.3f}\nRecall: {recall:.3f}\nF1: {f1:.3f}",
        fontsize=10,
        ha="left",
    )

    # Create filename from configuration
    filename = f"confusion_matrix_{config['gemini_model'].replace('/', '_')}_{config['max_results']}_{config['neural_ratio']}.png"

    # Save plot
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, filename))
    plt.close()

    # Print metrics
    print(f"\nConfusion Matrix Metrics for {config['gemini_model']}:")
    print(
        f"Max Results: {config['max_results']}, Neural Ratio: {config['neural_ratio']}"
    )
    print(f"Accuracy: {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1 Score: {f1:.3f}")

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": cm,
    }


def analyze_results_by_config(df: pd.DataFrame, save_dir: str = "results"):
    """Analyze results separately for each unique configuration"""
    # Get unique configurations
    configs = (
        df.groupby(["gemini_model", "max_results", "neural_ratio"]).size().reset_index()
    )

    all_metrics = []
    for _, config in configs.iterrows():
        # Filter data for this configuration
        mask = (
            (df["gemini_model"] == config["gemini_model"])
            & (df["max_results"] == config["max_results"])
            & (df["neural_ratio"] == config["neural_ratio"])
        )
        config_df = df[mask]

        # Create confusion matrix for this configuration
        metrics = create_confusion_matrix(
            config_df,
            {
                "gemini_model": config["gemini_model"],
                "max_results": config["max_results"],
                "neural_ratio": config["neural_ratio"],
            },
            save_dir,
        )

        metrics.update(
            {
                "gemini_model": config["gemini_model"],
                "max_results": config["max_results"],
                "neural_ratio": config["neural_ratio"],
            }
        )
        all_metrics.append(metrics)

        # Analyze error cases for this configuration
        print(f"\nError Analysis for {config['gemini_model']}:")
        print(
            f"Max Results: {config['max_results']}, Neural Ratio: {config['neural_ratio']}"
        )
        analyze_error_cases(config_df)

    return all_metrics


def analyze_error_cases(df: pd.DataFrame):
    """Analyze cases where the model made incorrect predictions"""
    error_cases = df[~df["is_correct"]]

    print("\nError Analysis:")
    print(f"Total errors: {len(error_cases)}")

    # Group errors by true/predicted answer combinations
    error_types = error_cases.groupby(["true_answer", "predicted_answer"]).size()
    print("\nError types:")
    print(error_types)

    # Sample some error cases
    print("\nSample error cases:")
    for _, case in error_cases.sample(min(5, len(error_cases))).iterrows():
        print(f"\nQuestion: {case['question']}")
        print(f"True answer: {case['true_answer']}")
        print(f"Predicted answer: {case['predicted_answer']}")


def main():
    # Load results
    results = load_evaluation_results("results")
    df = create_comparison_df(results)

    # Print basic statistics
    print("\nOverall Statistics:")
    print(f"Number of evaluations: {len(df)}")
    print(f"Average accuracy: {df['accuracy'].mean():.4f}")
    print(f"Best accuracy: {df['accuracy'].max():.4f}")
    print(f"Worst accuracy: {df['accuracy'].min():.4f}")

    # Analyze results by configuration
    metrics_by_config = analyze_results_by_config(df)

    # Create comparison table of metrics
    metrics_df = pd.DataFrame(metrics_by_config)
    print("\nMetrics Comparison:")
    print(metrics_df.to_string())

    # Analyze parameter impacts
    parameter_impacts = analyze_parameter_impact(df)

    # Create visualizations
    plot_parameter_impacts(df)
    create_interaction_heatmap(df)

    # Find best configuration
    best_config = metrics_df.loc[metrics_df["accuracy"].idxmax()]
    print("\nBest Configuration:")
    print(f"Model: {best_config['gemini_model']}")
    print(f"Max Results: {best_config['max_results']}")
    print(f"Neural Ratio: {best_config['neural_ratio']}")
    print(f"Accuracy: {best_config['accuracy']:.4f}")
    print(f"F1 Score: {best_config['f1']:.4f}")


if __name__ == "__main__":
    main()
