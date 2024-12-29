import json
import glob
import os


def flip_results(file_path):
    # Read the JSON file
    with open(file_path, "r") as f:
        data = json.load(f)

    # Flip answers and recalculate correctness
    correct_count = 0
    for result in data["detailed_results"]:
        # Flip the predicted answer
        result["predicted_answer"] = (
            "yes" if result["predicted_answer"] == "no" else "no"
        )

        # Recalculate if the answer is correct
        result["is_correct"] = result["predicted_answer"] == result["true_answer"]

        # Count correct answers
        if result["is_correct"]:
            correct_count += 1

    # Update overall statistics
    data["correct"] = correct_count
    data["accuracy"] = correct_count / data["total"]

    # Write back to file
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Processed {file_path}")
    print(f"New accuracy: {data['accuracy']:.2f}")


def main():
    # Find all evaluation result JSON files
    result_files = glob.glob("results/evaluation_results_*.json")

    for file_path in result_files:
        print(f"\nProcessing: {file_path}")
        flip_results(file_path)


if __name__ == "__main__":
    main()
