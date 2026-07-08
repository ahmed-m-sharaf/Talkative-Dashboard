import os
import sys
import time
import pytest
from numpy import mean, percentile

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import dashboard_engine
from core import Intent

EVAL_DATASET = [
    # AVERAGE_AGE
    {"prompt": "what is the average age of Software Engineers?", "expected_intent": Intent.AVERAGE_AGE, "expected_role": "Software Engineer"},
    {"prompt": "average age of backend engineers in Cairo", "expected_intent": Intent.AVERAGE_AGE, "expected_role": "Backend Engineer"},
    {"prompt": "how old are data scientists on average?", "expected_intent": Intent.AVERAGE_AGE, "expected_role": "Data Scientist"},
    
    # APPLICATION_COUNT
    {"prompt": "how many applications are currently Accepted?", "expected_intent": Intent.APPLICATION_COUNT, "expected_status": "Accepted"},
    {"prompt": "count applications from LinkedIn source", "expected_intent": Intent.APPLICATION_COUNT, "expected_source": "LinkedIn"},
    {"prompt": "number of pending applications", "expected_intent": Intent.APPLICATION_COUNT, "expected_status": "Pending"},
    
    # TOP_SKILLS
    {"prompt": "what are the top skills of Frontend Engineers?", "expected_intent": Intent.TOP_SKILLS, "expected_role": "Frontend Engineer"},
    {"prompt": "key skills for AI Engineers in Cairo", "expected_intent": Intent.TOP_SKILLS, "expected_role": "AI Engineer"},
    
    # REJECTION_RATE
    {"prompt": "what is the rejection rate of Website applications?", "expected_intent": Intent.REJECTION_RATE, "expected_source": "Website"},
    {"prompt": "rejection rate from Indeed", "expected_intent": Intent.REJECTION_RATE, "expected_source": "Indeed"},
    
    # SALARY_EXPECTATION
    {"prompt": "average salary expectation of Product Managers", "expected_intent": Intent.SALARY_EXPECTATION, "expected_role": "Product Manager"},
    {"prompt": "salary expectations for software engineers in Alexandria", "expected_intent": Intent.SALARY_EXPECTATION, "expected_role": "Software Engineer"},

    # UNKNOWN (Out-of-scope)
    {"prompt": "what is the weather in Cairo today?", "expected_intent": Intent.UNKNOWN},
    {"prompt": "who is the prime minister of Egypt?", "expected_intent": Intent.UNKNOWN}
]

def test_routing_latency_and_accuracy():
    """
    Programmatically run the dashboard engine on a test dataset
    to measure routing accuracy, parameter extraction, and processing latency.
    """
    print("\n" + "="*50)
    print("RUNNING LATENCY & ACCURACY ROUTING TEST")
    print("="*50)

    latencies = []
    intent_correct = 0
    params_correct = 0
    total_cases = len(EVAL_DATASET)

    for idx, case in enumerate(EVAL_DATASET, 1):
        prompt = case["prompt"]
        expected_intent = case["expected_intent"]
        
        start_time = time.perf_counter()
        try:
            response = dashboard_engine.run(prompt)
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "rate limit" in err_msg.lower() or "rate-limited" in err_msg.lower():
                pytest.skip(f"Groq API rate limit reached (TPD limit exceeded). Skipping test. Details: {err_msg}")
            raise e
        latency = time.perf_counter() - start_time
        
        latencies.append(latency)

        # 1. Evaluate Intent Classification
        actual_intent = response.intent_mapping.target_endpoint
        is_intent_ok = (actual_intent == expected_intent)
        if is_intent_ok:
            intent_correct += 1

        # 2. Evaluate Entity extraction if intent matched
        is_param_ok = True
        if is_intent_ok:
            extracted_params = response.intent_mapping.extracted_parameters
            # Check expected role if defined
            if "expected_role" in case:
                extracted_role = getattr(extracted_params, "role", None)
                if str(extracted_role).lower() != str(case["expected_role"]).lower():
                    is_param_ok = False
            # Check expected status if defined
            if "expected_status" in case:
                extracted_status = getattr(extracted_params, "status", None)
                # status can be an enum or string
                val = getattr(extracted_status, "value", str(extracted_status))
                if str(val).lower() != str(case["expected_status"]).lower():
                    is_param_ok = False
            # Check expected source if defined
            if "expected_source" in case:
                extracted_source = getattr(extracted_params, "source", None)
                val = getattr(extracted_source, "value", str(extracted_source))
                if str(val).lower() != str(case["expected_source"]).lower():
                    is_param_ok = False
        else:
            is_param_ok = False

        if is_param_ok:
            params_correct += 1

        print(f"[{idx}/{total_cases}] Prompt: '{prompt}' | Intent Match: {is_intent_ok} | Params Match: {is_param_ok} | Latency: {latency:.4f}s")
        time.sleep(0.2)  # Avoid token limit burst

    # Calculate statistics
    avg_latency = mean(latencies)
    p95_latency = percentile(latencies, 95)
    intent_accuracy = (intent_correct / total_cases) * 100
    param_accuracy = (params_correct / total_cases) * 100

    print("\n" + "="*50)
    print("ROUTING TEST SUMMARY")
    print(f"Total Test Cases:          {total_cases}")
    print(f"Intent Routing Accuracy:   {intent_accuracy:.2f}%")
    print(f"Entity Extraction Accuracy: {param_accuracy:.2f}%")
    print(f"Average Processing Latency: {avg_latency:.4f}s")
    print(f"P95 Processing Latency:     {p95_latency:.4f}s")
    print("="*50 + "\n")

    # Assert basic health threshold
    assert intent_accuracy >= 50.0, f"Intent routing accuracy dropped to {intent_accuracy:.2f}%"
    assert avg_latency < 10.0, f"Average processing latency is too high: {avg_latency:.2f}s"
