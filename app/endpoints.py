from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID

from app.models import Task, Agent, Bid, WorkProduct, VerificationStatus
from app.database import db
from app.components import (
    TaskBoard,
    QualificationEngine,
    BiddingSystem,
    WorkVerificationService,
    ReputationLedger,
)

router = APIRouter()

task_board = TaskBoard()
qualification_engine = QualificationEngine()
bidding_system = BiddingSystem()
work_verification_service = WorkVerificationService()
reputation_ledger = ReputationLedger()

@router.post("/tasks/", response_model=Task, status_code=201)
def create_task(task_in: Task):
    """
    Create a new task on the Task Board.
    """
    return task_board.post_task(task_in)

@router.get("/tasks/", response_model=List[Task])
def list_tasks():
    """
    Get all tasks from the Task Board.
    """
    return task_board.get_all_tasks()


@router.post("/agents/", response_model=Agent, status_code=201)
def register_agent(agent_in: Agent):
    """
    Register a new agent in the marketplace.
    """
    db["agents"][agent_in.agent_id] = agent_in
    return agent_in

@router.post("/bids/", response_model=Bid, status_code=201)
def submit_bid(bid_in: Bid):
    """
    Submit a bid for a task.
    """
    agent = db["agents"].get(bid_in.agent_id)
    task = db["tasks"].get(bid_in.task_id)

    if not agent or not task:
        raise HTTPException(status_code=404, detail="Agent or Task not found")

    if not qualification_engine.is_agent_qualified(agent, task):
        raise HTTPException(status_code=403, detail="Agent not qualified for this task")
    
    try:
        return bidding_system.submit_bid(bid_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tasks/{task_id}/select_winner/", response_model=Bid)
def select_winner_for_task(task_id: UUID):
    """
    Select the winning bid for a task.
    """
    winning_bid = bidding_system.select_winner(task_id)
    if not winning_bid:
        raise HTTPException(status_code=404, detail="No bids found or task not in bidding state")
    return winning_bid

@router.post("/work_products/", response_model=WorkProduct, status_code=201)
def submit_work_for_task(work_in: WorkProduct):
    """
    Submit a work product for a task.
    """
    return work_verification_service.submit_work(work_in)

@router.post("/work_products/{work_id}/verify/")
def verify_submitted_work(work_id: UUID, score: float):
    """
    Verify a submitted work product and update reputation.
    """
    try:
        work_product = work_verification_service.verify_work(work_id, score)
        if work_product.verification_status == VerificationStatus.PASSED:
            reputation_ledger.record_success(work_product.agent_id, score)
        return work_product
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/agents/{agent_id}", response_model=Agent)
def get_agent(agent_id: UUID):
    """
    Get agent details.
    """
    agent = db["agents"].get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: UUID):
    """
    Get task details.
    """
    task = db["tasks"].get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
