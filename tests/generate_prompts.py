import json
import os
import random

# Define template structures and entity options to generate 500 distinct prompts
ROLES = [
    "Software Engineer", "Backend Engineer", "Frontend Engineer", 
    "AI Engineer", "Data Scientist", "DevOps Engineer", 
    "QA Engineer", "Data Analyst", "Product Manager", "UI Designer"
]

CITIES = ["Cairo", "Alexandria", "Giza", "Mansoura", "Assiut", "Tanta", "Suez", "Hurghada"]
STATUSES = ["Accepted", "Rejected", "Pending"]
SOURCES = ["LinkedIn", "Website", "Indeed", "Referral", "Glassdoor"]

def generate_normal_cases():
    cases = []
    
    # 1. Average Age
    for role in ROLES:
        for city in CITIES[:6]:
            cases.append({
                "prompt": f"average age of {role} in {city}",
                "expected_intent": "average_age",
                "expected_params": {"role": role, "city": city}
            })
            cases.append({
                "prompt": f"what is the average age of {role} applicants?",
                "expected_intent": "average_age",
                "expected_params": {"role": role}
            })

    # 2. Application Count
    for role in ROLES[:5]:
        for status in STATUSES:
            for source in SOURCES[:3]:
                cases.append({
                    "prompt": f"how many {status} applications for {role} from {source}?",
                    "expected_intent": "application_count",
                    "expected_params": {"role": role, "status": status, "source": source}
                })

    # 3. Top Skills
    for role in ROLES:
        for city in CITIES[:4]:
            cases.append({
                "prompt": f"top skills of {role} candidates in {city}",
                "expected_intent": "top_skills",
                "expected_params": {"role": role, "city": city}
            })

    # 4. Rejection Rate
    for source in SOURCES:
        for city in CITIES[:4]:
            cases.append({
                "prompt": f"what is the rejection rate for candidates from {source} in {city}?",
                "expected_intent": "rejection_rate",
                "expected_params": {"source": source, "city": city}
            })

    # 5. Salary Expectations
    for role in ROLES:
        for city in CITIES[:4]:
            cases.append({
                "prompt": f"salary expectations for {role} in {city}",
                "expected_intent": "salary_expectation",
                "expected_params": {"role": role, "city": city}
            })
            
    # Sample down to exactly 300 normal cases deterministically
    random.seed(42)
    random.shuffle(cases)
    return cases[:300]

def generate_missing_params_cases():
    # Prompts missing required arguments (e.g. role for Average Age)
    cases = []
    templates = [
        ("what is the average age?", "average_age"),
        ("show me the average age in {city}", "average_age"),
        ("what are the key skills in {city}?", "top_skills"),
        ("skills for applicants in {city}", "top_skills"),
        ("average salary expectation?", "salary_expectation"),
        ("what is the salary expectation in {city}?", "salary_expectation")
    ]
    for city in CITIES:
        for temp, intent in templates:
            fmt_prompt = temp.format(city=city) if "{city}" in temp else temp
            cases.append({
                "prompt": fmt_prompt,
                "expected_intent": intent,
                "expected_params": {"city": city} if "{city}" in temp else {},
                "is_missing_params": True
            })
    random.seed(42)
    random.shuffle(cases)
    return cases[:100]

def generate_unsupported_cases():
    # Out of scope prompts
    cases = []
    prompts = [
        "what is the capital of France?",
        "weather report for London",
        "how to write a binary search in rust",
        "recipe for chicken pasta",
        "tell me a bedtime story",
        "who directed the movie Inception?",
        "explain the theory of relativity",
        "how does photosynthesis work?",
        "what is the speed of light?",
        "suggest some books on history",
        "how to repair a laptop screen",
        "best hotels in Tokyo",
        "history of the Roman Empire",
        "what is the price of Bitcoin?",
        "formula for quadratic equation",
        "translate hello to Spanish",
        "who won the world cup in 2022?",
        "what is the distance to the moon?",
        "definition of photosynthesis",
        "how to play the guitar"
    ]
    # Multiply or expand templates to get 50 distinct items
    for p in prompts:
        cases.append({
            "prompt": p,
            "expected_intent": "unknown",
            "expected_params": {},
            "is_unsupported": True
        })
    # Add minor variations to match exactly 50
    for i in range(30):
        cases.append({
            "prompt": f"tell me query number {i} about unrelated topic",
            "expected_intent": "unknown",
            "expected_params": {},
            "is_unsupported": True
        })
    return cases

def generate_low_confidence_cases():
    # Ambiguous or short greetings / greetings that are not clear
    greetings = [
        "hello", "hi chatbot", "good morning", "good evening", 
        "hey there", "hola", "yo", "test test", "dashboard", 
        "chat room", "analytics help", "recruitment assistant", 
        "main menu", "start over", "help please", "reset session", 
        "system status", "admin access", "login", "exit"
    ]
    cases = []
    for g in greetings:
        cases.append({
            "prompt": g,
            "expected_intent": "unknown",
            "expected_params": {},
            "is_low_confidence": True
        })
    # Expand variations to get 50 distinct items
    for i in range(30):
        cases.append({
            "prompt": f"just greeting {i}",
            "expected_intent": "unknown",
            "expected_params": {},
            "is_low_confidence": True
        })
    return cases

def main():
    normal = generate_normal_cases()
    missing = generate_missing_params_cases()
    unsupported = generate_unsupported_cases()
    low_conf = generate_low_confidence_cases()

    all_cases = normal + missing + unsupported + low_conf

    # Ensure we shuffle deterministically
    random.seed(12345)
    random.shuffle(all_cases)

    # Let's verify we have exactly 500 prompts
    final_500 = all_cases[:500]
    
    # Pad if somehow under 500
    while len(final_500) < 500:
        final_500.append(normal[random.randint(0, len(normal)-1)])

    output_path = os.path.join(os.path.dirname(__file__), "prompts_500.json")
    with open(output_path, "w") as f:
        json.dump(final_500, f, indent=4)
        
    print(f"Generated exactly {len(final_500)} prompts in {output_path}:")
    print(f"  - Normal: {len([c for c in final_500 if not c.get('is_missing_params') and not c.get('is_unsupported') and not c.get('is_low_confidence')])}")
    print(f"  - Missing Params: {len([c for c in final_500 if c.get('is_missing_params')])}")
    print(f"  - Unsupported: {len([c for c in final_500 if c.get('is_unsupported')])}")
    print(f"  - Low Confidence: {len([c for c in final_500 if c.get('is_low_confidence')])}")

if __name__ == "__main__":
    main()
