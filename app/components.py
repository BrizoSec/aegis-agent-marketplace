from typing import Optional, List
from uuid import UUID
from app.models import Task, Agent, Bid, WorkProduct, TaskStatus, VerificationStatus
from app.database import db

class TaskBoard:
    def post_task(self, task: Task) -> Task:
        db["tasks"][task.task_id] = task
        return task

    def get_task(self, task_id: UUID) -> Optional[Task]:
        return db["tasks"].get(task_id)

    def get_all_tasks(self) -> List[Task]:
        return list(db["tasks"].values())

class QualificationEngine:
    def is_agent_qualified(self, agent: Agent, task: Task) -> bool:
        # Simplified qualification logic
        return all(cap in agent.capabilities for cap in task.required_capabilities)

class BiddingSystem:
    def submit_bid(self, bid: Bid) -> Bid:
        if bid.task_id not in db["tasks"]:
            raise ValueError("Task not found")
        if bid.agent_id not in db["agents"]:
            raise ValueError("Agent not found")
        
        if db["tasks"][bid.task_id].status != TaskStatus.POSTED:
            raise ValueError("Task is not open for bidding")

        if bid.task_id not in db["bids"]:
            db["bids"][bid.task_id] = []
        
        db["bids"][bid.task_id].append(bid)
        db["tasks"][bid.task_id].status = TaskStatus.BIDDING_OPEN
        return bid

    def select_winner(self, task_id: UUID) -> Optional[Bid]:
        if task_id not in db["bids"] or not db["bids"][task_id]:
            return None
        
        # Simplified selection: lowest bid wins
        winning_bid = min(db["bids"][task_id], key=lambda b: b.bid_amount)
        
        task = db["tasks"][task_id]
        task.status = TaskStatus.ASSIGNED
        return winning_bid

class WorkVerificationService:
    def submit_work(self, work_product: WorkProduct) -> WorkProduct:
        db["work_products"][work_product.work_id] = work_product
        db["tasks"][work_product.task_id].status = TaskStatus.SUBMITTED
        return work_product

    def verify_work(self, work_id: UUID, score: float) -> WorkProduct:
        work_product = db["work_products"].get(work_id)
        if not work_product:
            raise ValueError("WorkProduct not found")

        if score >= 75:
            work_product.verification_status = VerificationStatus.PASSED
            db["tasks"][work_product.task_id].status = TaskStatus.VERIFIED
        else:
            work_product.verification_status = VerificationStatus.FAILED
            db["tasks"][work_product.task_id].status = TaskStatus.REJECTED
        return work_product

class ReputationLedger:
    def record_success(self, agent_id: UUID, score: float):
        agent = db["agents"].get(agent_id)
        if not agent:
            return

        # Simplified reputation update
        agent.completed_tasks += 1
        agent.reputation_score = (agent.reputation_score + score) / agent.completed_tasks
        # In a real system, success rate would be more nuanced
        agent.success_rate = ((agent.success_rate * (agent.completed_tasks -1)) + 1) / agent.completed_tasks
