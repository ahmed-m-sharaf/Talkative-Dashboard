from datetime import datetime
from typing import Any

from pydantic import BaseModel

from core.intents import Intent
from schemas.request import RouteParameters


class Metadata(BaseModel):
    user_prompt: str

    timestamp_processed: datetime



class IntentMapping(BaseModel):
    target_endpoint: Intent

    confidence_score: float

    extracted_parameters: RouteParameters



class ExecutionResult(BaseModel):
    status: str

    raw_data: dict[str, Any]



class DashboardResponse(BaseModel):
    metadata: Metadata

    intent_mapping: IntentMapping

    execution_result: ExecutionResult

    visualization_instruction: str