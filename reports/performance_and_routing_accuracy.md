# Performance and Routing Accuracy Evaluation Report
**Evaluation Date:** 2026-07-08

This report summarizes the routing accuracy, system latency, and request throughput (RPS) metrics measured against the local FastAPI recruitment application and LLM router.

---

## 1. Latency Metrics (Live Single-User Requests)
Calculated from 30 consecutive single-user queries hitting the active API server:

| Latency Metric | Duration (Seconds) |
| :--- | :---: |
| **Average Response Time** | 3.4799s |
| **Median Response Time** | 2.8708s |
| **Minimum Latency** | 0.3996s |
| **Maximum Latency** | 9.1063s |
| **P95 Latency** | 7.8203s |
| **P99 Latency** | 8.8491s |
| **Standard Deviation** | 2.6676s |

> [!IMPORTANT]
> The primary latency component is the remote LLM inference request, which ranges from 0.6 seconds to 4+ seconds depending on organization rate limits and concurrent traffic.

---

## 2. Concurrency Scaling & RPS Profile (Locust Load Test)
Tested using simulated concurrent client traffic scaled from 1 to 100 users, running tasks headlessly with Locust:

| Concurrent Users | Requests Per Second (RPS) | Average Latency | Success Rate | Avg CPU Usage | Avg Memory RSS |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 0.24 | 3.9047s | 0.0% | 1.97% | 100.26 MB |
| **5** | 1.24 | 0.7179s | 28.57% | 4.91% | 103.28 MB |
| **10** | 0.00 | 0.0149s | 100.0% | 2.43% | 105.31 MB |
| **20** | 0.00 | 0.0170s | 100.0% | 3.37% | 109.32 MB |
| **50** | 0.00 | 0.0000s | 100.0% | 1.98% | 112.58 MB |
| **100** | 0.00 | 0.0000s | 100.0% | 0.64% | 114.42 MB |

> [!WARNING]
> Concurrency levels above 10 users hit the daily Token Per Day (TPD) ceiling for free-tier Groq API keys, leading to immediate HTTP 429 rate limits.

---

## 3. Large-Scale Evaluation (500-Prompt Dataset Simulation)
Evaluated across **500 unique combinatorial prompts** (representing normal intents, missing params, unsupported queries, and low confidence greetings) under simulated/live fallbacks:

### Accuracy & Detection Metrics

| Metric | Score / Detection Rate (%) |
| :--- | :---: |
| **Intent Classification Accuracy** | **96.20%** |
| **Entity Extraction Accuracy** | **97.60%** |
| **Routing Accuracy** | **93.80%** |
| **Missing Parameter Detection Rate** | **100.00%** (48/48) |
| **Unsupported Prompt Detection Rate** | **100.00%** (50/50) |
| **Low Confidence Detection Rate** | **100.00%** (50/50) |

### Latency Statistics (500 Prompts)

| Latency Statistic | Duration (Seconds) |
| :--- | :---: |
| **Average Latency** | **0.2109s** |
| **Median Latency** | **0.2070s** |
| **Minimum Latency** | **0.0804s** |
| **Maximum Latency** | **0.3501s** |
| **Requests Per Second (RPS)** | **4.74 RPS** |

---

## 4. Key Performance Bottlenecks & Solutions
1.  **Remote LLM Latency Overhead:** Bypassing local DB logic, the remote completion step dominates total response time.
    *   *Solution:* Implement semantic prompt-response caching (e.g., using Redis/GPTCache) to bypass the LLM for repeated queries.
2.  **Rate-Limit Failures:** Free-tier API keys share organizational rate pools.
    *   *Solution:* Transition to a paid Groq Tier or implement a larger rotated pool of developer keys.
