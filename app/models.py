from pydantic import BaseModel, Field
from typing import List, Dict, Any
from uuid import UUID, uuid4
import enum

class TaskStatus(str, enum.Enum):
    POSTED = "POSTED"
    BIDDING_OPEN = "BIDDING_OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    VERIFIED = "VERIFIED"
    PAID = "PAID"
    REJECTED = "REJECTED"

class QualificationLevel(str, enum.Enum):
    NOVICE = "NOVICE"
    INTERMEDIATE = "INTERMEDIATE"
    EXPERT = "EXPERT"
    MASTER = "MASTER"

class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"

class Task(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    title: str
    description: str
    required_capabilities: List[str]
    reward_amount: float
    status: TaskStatus = TaskStatus.POSTED

class Agent(BaseModel):
    agent_id: UUID = Field(default_factory=uuid4)
    capabilities: List[str]
    reputation_score: float = 0.0
    completed_tasks: int = 0
    success_rate: float = 0.0

class Bid(BaseModel):
    bid_id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    agent_id: UUID
    bid_amount: float

class WorkProduct(BaseModel):
    work_id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    agent_id: UUID
    deliverable: Dict[str, Any]
    verification_status: VerificationStatus = VerificationStatus.PENDING
