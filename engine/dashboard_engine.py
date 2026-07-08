import time
from datetime import datetime

from dispatcher import Dispatcher
from engine.visualization import get_visualization
from llm import router
from validators import RequestValidator
from core import logger, Intent

from schemas import (
    DashboardResponse,
    ExecutionResult,
    IntentMapping,
    Metadata,
)


class DashboardEngine:

    def run(self, user_prompt: str) -> DashboardResponse:
        logger.info(f"Received user prompt: '{user_prompt}'")
        start_time = time.perf_counter()


        routing_start = time.perf_counter()
        router_response = router.route(user_prompt)
        routing_latency = time.perf_counter() - routing_start

        logger.info(
            f"Routed to intent: '{router_response.intent}' with confidence: {router_response.confidence_score:.2f} "
            f"(latency: {routing_latency:.3f}s)"
        )
        CONFIDENCE_THRESHOLD = 0.6

        if (
            router_response.intent == Intent.UNKNOWN
            or router_response.confidence_score < CONFIDENCE_THRESHOLD
            or router_response.needs_clarification
        ):
            logger.warning(
                f"Out of scope, low confidence ({router_response.confidence_score:.2f}), or unmapped prompt: '{user_prompt}'"
            )
            return DashboardResponse(
                metadata=Metadata(
                    user_prompt=user_prompt,
                    timestamp_processed=datetime.now(),
                ),
                intent_mapping=IntentMapping(
                    target_endpoint=Intent.UNKNOWN,
                    confidence_score=router_response.confidence_score,
                    extracted_parameters=router_response.parameters,
                ),
                execution_result=ExecutionResult(
                    status="UNKNOWN_INTENT",
                    raw_data={
                        "message": "This query is out of scope or could not be mapped to any recruitment metrics. Please ask questions related to candidates, average age, application counts, top skills, rejection rates, or salary expectations."
                    },
                ),
                visualization_instruction="TEXT_RESPONSE",
            )

        REQUIRED_PARAMS = {
            Intent.AVERAGE_AGE: ["role"],
            Intent.APPLICATION_COUNT: [],
            Intent.TOP_SKILLS: ["role"],
            Intent.REJECTION_RATE: ["source"],
            Intent.SALARY_EXPECTATION: [],
        }

        required = REQUIRED_PARAMS.get(router_response.intent, [])
        missing = [p for p in required if getattr(router_response.parameters, p) is None]

        if missing:
            logger.warning(
                f"Missing required parameters for intent '{router_response.intent}': {missing}"
            )
            return DashboardResponse(
                metadata=Metadata(
                    user_prompt=user_prompt,
                    timestamp_processed=datetime.now(),
                ),
                intent_mapping=IntentMapping(
                    target_endpoint=router_response.intent,
                    confidence_score=router_response.confidence_score,
                    extracted_parameters=router_response.parameters,
                ),
                execution_result=ExecutionResult(
                    status="MISSING_PARAMETERS",
                    raw_data={
                        "missing_parameters": missing
                    },
                ),
                visualization_instruction="TEXT_RESPONSE",
            )

        is_valid, error_message = RequestValidator.validate(
            router_response
        )

        if not is_valid:
            logger.warning(f"Parameter validation failed: {error_message}")
            return DashboardResponse(
                metadata=Metadata(
                    user_prompt=user_prompt,
                    timestamp_processed=datetime.now(),
                ),
                intent_mapping=IntentMapping(
                    target_endpoint=router_response.intent,
                    confidence_score=router_response.confidence_score,
                    extracted_parameters=router_response.parameters,
                ),
                execution_result=ExecutionResult(
                    status="INVALID_PARAMETER",
                    raw_data={
                        "error": error_message
                    },
                ),
                visualization_instruction="TEXT_RESPONSE",
            )

        dispatch_start = time.perf_counter()
        result = Dispatcher.dispatch(
            router_response.intent,
            router_response.parameters.model_dump(
                exclude_none=True
            ),
        )
        dispatch_latency = time.perf_counter() - dispatch_start
        logger.info(f"Backend execution successful (latency: {dispatch_latency:.3f}s)")


        total_latency = time.perf_counter() - start_time
        logger.info(f"Total prompt processing completed in {total_latency:.3f}s")

        return DashboardResponse(
            metadata=Metadata(
                user_prompt=user_prompt,
                timestamp_processed=datetime.now(),
            ),
            intent_mapping=IntentMapping(
                target_endpoint=router_response.intent,
                confidence_score=router_response.confidence_score,
                extracted_parameters=router_response.parameters,
            ),
            execution_result=ExecutionResult(
                status="SUCCESS",
                raw_data=result,
            ),
            visualization_instruction=get_visualization(
                router_response.intent
            ),
        )


dashboard_engine = DashboardEngine()