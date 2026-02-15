import pytest
from fastapi.testclient import TestClient
from fastapi import status
import uuid

# Import the FastAPI app instance
from app.main import app


@pytest.mark.asyncio
async def test_read_root():
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Aegis Agent Marketplace POC"}


@pytest.mark.asyncio
async def test_create_and_get_task():
    task_data = {
        "title": "Test Task",
        "description": "A task for testing",
        "required_capabilities": ["python", "fastapi"],
        "reward_amount": 100.0,
    }
    with TestClient(app) as client:
        # Create task
        create_response = client.post("/tasks/", json=task_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_task = create_response.json()
        assert created_task["title"] == task_data["title"]
        task_id = created_task["task_id"]

        # Get task
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["title"] == task_data["title"]


@pytest.mark.asyncio
async def test_full_workflow():
    with TestClient(app) as client:
        # 1. Create Agent
        agent_data = {
            "capabilities": ["python", "fastapi", "testing"],
            "reputation_score": 90.0
        }
        agent_response = client.post("/agents/", json=agent_data)
        assert agent_response.status_code == status.HTTP_201_CREATED
        agent = agent_response.json()
        agent_id = agent["agent_id"]

        # 2. Create Task
        task_data = {
            "title": "Full Workflow Task",
            "description": "A task to test the full workflow",
            "required_capabilities": ["python", "testing"],
            "reward_amount": 250.0,
        }
        task_response = client.post("/tasks/", json=task_data)
        assert task_response.status_code == status.HTTP_201_CREATED
        task = task_response.json()
        task_id = task["task_id"]

        # 3. Submit Bid
        bid_data = {
            "task_id": task_id,
            "agent_id": agent_id,
            "bid_amount": 200.0
        }
        bid_response = client.post("/bids/", json=bid_data)
        assert bid_response.status_code == status.HTTP_201_CREATED
        
        # 4. Select Winner
        select_winner_response = client.post(f"/tasks/{task_id}/select_winner/")
        assert select_winner_response.status_code == status.HTTP_200_OK
        winning_bid = select_winner_response.json()
        assert winning_bid["agent_id"] == agent_id

        # 5. Submit Work
        work_data = {
            "task_id": task_id,
            "agent_id": agent_id,
            "deliverable": {"result": "This is the completed work."}
        }
        work_response = client.post("/work_products/", json=work_data)
        assert work_response.status_code == status.HTTP_201_CREATED
        work_product = work_response.json()
        work_id = work_product["work_id"]
        
        # 6. Verify Work
        verify_response = client.post(f"/work_products/{work_id}/verify/?score=95")
        assert verify_response.status_code == status.HTTP_200_OK
        verified_work = verify_response.json()
        assert verified_work["verification_status"] == "PASSED"

        # 7. Check Agent Reputation Update
        get_agent_response = client.get(f"/agents/{agent_id}")
        assert get_agent_response.status_code == status.HTTP_200_OK
        updated_agent = get_agent_response.json()
        assert updated_agent["completed_tasks"] == 1
        assert updated_agent["reputation_score"] > agent["reputation_score"]

