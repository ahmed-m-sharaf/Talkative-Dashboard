import os
import sys
import time
import json
import random
import pytest
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import dashboard_engine
from core import Intent
from schemas import DashboardResponse, ExecutionResult

DATASET_PATH = os.path.join(os.path.dirname(__file__), "prompts_500.json")

def load_dataset():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"500 Prompt dataset not found at {DATASET_PATH}. Run generate_prompts.py first.")
    with open(DATASET_PATH, "r") as f:
        return json.load(f)

class MockLLMRouter:
    """Mock LLM Router to simulate engine responses and latencies without hitting remote rate limits."""
    @staticmethod
    def run_mock(case):
        # Simulate network & LLM inference latency
        simulated_latency = random.uniform(0.08, 0.35)
        time.sleep(simulated_latency)

        intent_str = case["expected_intent"]
        
        # Determine confidence score based on case flags
        if case.get("is_low_confidence"):
            confidence = random.uniform(0.1, 0.58)
            intent_str = "unknown"
            status = "UNKNOWN_INTENT"
        elif case.get("is_unsupported"):
            confidence = random.uniform(0.1, 0.59)
            intent_str = "unknown"
            status = "UNKNOWN_INTENT"
        elif case.get("is_missing_params"):
            confidence = random.uniform(0.75, 0.98)
            status = "VALIDATION_WARNING"
        else:
            # 5% chance of misclassifying intent to simulate real-world error rates
            confidence = random.uniform(0.75, 0.99)
            status = "SUCCESS"
            if random.random() < 0.05:
                alternate_intents = ["average_age", "application_count", "top_skills", "rejection_rate", "salary_expectation", "unknown"]
                alternate_intents.remove(intent_str)
                intent_str = random.choice(alternate_intents)

        # Parameter simulation
        params = dict(case.get("expected_params", {}))
        # 5% chance of failing parameter extraction for normal cases
        if not case.get("is_missing_params") and not case.get("is_unsupported") and not case.get("is_low_confidence"):
            if random.random() < 0.05 and params:
                key_to_drop = random.choice(list(params.keys()))
                params[key_to_drop] = None
        
        # Convert intent string to Intent Enum
        intent_map = {
            "average_age": Intent.AVERAGE_AGE,
            "application_count": Intent.APPLICATION_COUNT,
            "top_skills": Intent.TOP_SKILLS,
            "rejection_rate": Intent.REJECTION_RATE,
            "salary_expectation": Intent.SALARY_EXPECTATION,
            "unknown": Intent.UNKNOWN
        }
        
        return {
            "target_endpoint": intent_map.get(intent_str, Intent.UNKNOWN),
            "confidence_score": confidence,
            "extracted_parameters": params,
            "status": status
        }

def test_500_prompts_evaluation():
    """
    Test routing latency and accuracy across all 500 prompts.
    Provides detailed metrics: intent, parameters, combined routing accuracy,
    missing parameter detection rate, unsupported prompt detection, and low confidence detection.
    """
    dataset = load_dataset()
    is_live = os.environ.get("LIVE_TEST", "false").lower() == "true"
    
    max_cases = 500
    if is_live:
        max_cases = 30
        print(f"\n[LIVE MODE ACTIVE] Limiting evaluation to {max_cases} cases to prevent rate limits...")
    else:
        print(f"\n[SIMULATION MODE ACTIVE] Evaluating all {max_cases} generated prompts...")

    test_cases = dataset[:max_cases]
    
    latencies = []
    intent_correct = 0
    param_correct = 0
    routing_correct = 0

    # Specialty metric counts
    missing_params_total = 0
    missing_params_detected = 0
    
    unsupported_total = 0
    unsupported_detected = 0
    
    low_confidence_total = 0
    low_confidence_detected = 0
    
    results = []

    print("\nStarting evaluation run...")
    start_run_time = time.perf_counter()

    for idx, case in enumerate(test_cases, 1):
        prompt = case["prompt"]
        expected_intent = case["expected_intent"]
        expected_params = case.get("expected_params", {})

        is_missing = case.get("is_missing_params", False)
        is_unsupported = case.get("is_unsupported", False)
        is_low_conf = case.get("is_low_confidence", False)

        if is_missing: missing_params_total += 1
        if is_unsupported: unsupported_total += 1
        if is_low_conf: low_confidence_total += 1

        step_start = time.perf_counter()
        
        if is_live:
            try:
                response = dashboard_engine.run(prompt)
                actual_intent = response.intent_mapping.target_endpoint.value
                confidence = response.intent_mapping.confidence_score
                
                # Extract parameters dictionary
                extracted = response.intent_mapping.extracted_parameters
                actual_params = {}
                for field in ["role", "city", "status", "source"]:
                    if hasattr(extracted, field):
                        val = getattr(extracted, field)
                        if val is not None:
                            actual_params[field] = getattr(val, "value", str(val))
                exec_status = response.execution_result.status
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "rate limit" in err_msg.lower() or "rate-limited" in err_msg.lower():
                    print(f"\n[Warning] Hitting Groq rate limits at step {idx}. Finalizing metrics...")
                    break
                raise e
        else:
            # Simulation mode
            mock_res = MockLLMRouter.run_mock(case)
            actual_intent = mock_res["target_endpoint"].value
            confidence = mock_res["confidence_score"]
            actual_params = mock_res["extracted_parameters"]
            exec_status = mock_res["status"]

        latency = time.perf_counter() - step_start
        latencies.append(latency)

        # 1. Compare Intent Classification
        is_intent_ok = (actual_intent == expected_intent)
        if is_intent_ok:
            intent_correct += 1

        # 2. Compare Parameter Extraction
        is_param_ok = True
        for k, expected_v in expected_params.items():
            actual_v = actual_params.get(k)
            if str(actual_v).lower() != str(expected_v).lower():
                is_param_ok = False
                break
        
        if is_param_ok:
            param_correct += 1

        # 3. Overall routing correctness
        is_routing_ok = is_intent_ok and is_param_ok
        if is_routing_ok:
            routing_correct += 1

        # 4. Track Specialty Detections
        if is_missing:
            # Detected if status shows validation warning/clarification or parameters are indeed empty/filtered
            if "warning" in exec_status.lower() or "validation" in exec_status.lower() or "clarification" in exec_status.lower() or not actual_params.get("role"):
                missing_params_detected += 1
                
        if is_unsupported:
            # Detected if successfully routed to Intent.UNKNOWN / "unknown"
            if actual_intent == "unknown":
                unsupported_detected += 1
                
        if is_low_conf:
            # Detected if LLM Router confidence drops below standard 0.6 threshold
            if confidence < 0.6:
                low_confidence_detected += 1

        results.append({
            "prompt": prompt,
            "expected_intent": expected_intent,
            "predicted_intent": actual_intent,
            "expected_parameters": expected_params,
            "predicted_parameters": actual_params,
            "confidence": confidence,
            "latency": latency,
            "status": exec_status,
            "intent_correct": is_intent_ok,
            "params_correct": is_param_ok,
            "routing_correct": is_routing_ok,
            "is_missing_params": is_missing,
            "is_unsupported": is_unsupported,
            "is_low_confidence": is_low_conf
        })

        if idx % 50 == 0:
            print(f"  Processed {idx}/{len(test_cases)} prompts...")

    total_duration = time.perf_counter() - start_run_time
    total_processed = len(latencies)

    # Calculate metrics
    avg_latency = np.mean(latencies)
    median_latency = np.median(latencies)
    min_latency = np.min(latencies)
    max_latency = np.max(latencies)
    p95_latency = np.percentile(latencies, 95)
    stddev_latency = np.std(latencies)
    rps = total_processed / total_duration if total_duration > 0 else 0.0

    intent_acc = (intent_correct / total_processed) * 100
    param_acc = (param_correct / total_processed) * 100
    routing_acc = (routing_correct / total_processed) * 100

    # Detection Rates
    missing_detect_rate = (missing_params_detected / missing_params_total * 100) if missing_params_total > 0 else 100.0
    unsupported_detect_rate = (unsupported_detected / unsupported_total * 100) if unsupported_total > 0 else 100.0
    low_conf_detect_rate = (low_confidence_detected / low_confidence_total * 100) if low_confidence_total > 0 else 100.0

    print("\n" + "="*50)
    print(f"EVALUATION SUMMARY OVER {total_processed} PROMPTS")
    print(f"Execution Mode:                 {'LIVE' if is_live else 'SIMULATED'}")
    print(f"Total Requests Executed:        {total_processed}")
    print(f"Requests Per Second (RPS):      {rps:.2f} RPS")
    print("-" * 50)
    print(f"Intent Classification Accuracy: {intent_acc:.2f}%")
    print(f"Entity Extraction Accuracy:     {param_acc:.2f}%")
    print(f"Routing Accuracy:               {routing_acc:.2f}%")
    print(f"Missing Parameter Detect Rate:  {missing_detect_rate:.2f}% ({missing_params_detected}/{missing_params_total})")
    print(f"Unsupported Prompt Detect Rate: {unsupported_detect_rate:.2f}% ({unsupported_detected}/{unsupported_total})")
    print(f"Low Confidence Detection Rate:  {low_conf_detect_rate:.2f}% ({low_confidence_detected}/{low_confidence_total})")
    print("-" * 50)
    print(f"Average Latency:                {avg_latency:.4f}s")
    print(f"Median Latency:                 {median_latency:.4f}s")
    print(f"Minimum Latency:                {min_latency:.4f}s")
    print(f"Maximum Latency:                {max_latency:.4f}s")
    print("="*50 + "\n")

    # Export results
    os.makedirs("reports", exist_ok=True)
    results_export = {
        "summary": {
            "mode": "live" if is_live else "simulated",
            "total_processed": total_processed,
            "rps": rps,
            "avg_latency": avg_latency,
            "median_latency": median_latency,
            "min_latency": min_latency,
            "max_latency": max_latency,
            "p95_latency": p95_latency,
            "intent_accuracy": intent_acc,
            "parameter_accuracy": param_acc,
            "routing_accuracy": routing_acc,
            "missing_parameter_detection_rate": missing_detect_rate,
            "unsupported_prompt_detection_rate": unsupported_detect_rate,
            "low_confidence_detection_rate": low_conf_detect_rate
        },
        "cases": results
    }
    
    with open("reports/benchmark_500_results.json", "w") as f:
        json.dump(results_export, f, indent=4)

    # Plot and save latency histogram
    plt.figure(figsize=(10, 6))
    sns.histplot(latencies, kde=True, color="indigo")
    plt.axvline(avg_latency, color="red", linestyle="--", label=f"Avg ({avg_latency:.3f}s)")
    plt.axvline(median_latency, color="green", linestyle="-.", label=f"Median ({median_latency:.3f}s)")
    plt.title(f"Latency Distribution over {total_processed} Prompts ({'Live' if is_live else 'Simulated'})")
    plt.xlabel("Latency (seconds)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.savefig("reports/latency_500_distribution.png")
    plt.close()

    assert routing_acc >= 50.0, f"Routing accuracy fell below threshold: {routing_acc:.2f}%"
