import requests
import uuid
from typing import List, Dict, Any

# --- Configuration ---
# This should be the address of your running marketplace API
MARKETPLACE_URL = "http://127.0.0.1:8000"

# --- API Client Functions ---

def register_agent(capabilities: List[str]) -> Dict[str, Any]:
    """Registers a new agent with the marketplace."""
    agent_data = {
        "capabilities": capabilities,
        "reputation_score": 0.0,
        "completed_tasks": 0,
        "success_rate": 0.0
    }
    try:
        response = requests.post(f"{MARKETPLACE_URL}/agents/", json=agent_data)
        response.raise_for_status()  # Raise an exception for bad status codes
        print("Agent registered successfully!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error registering agent: {e}")
        return None

def get_tasks() -> List[Dict[str, Any]]:
    """Fetches all tasks from the marketplace."""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/tasks/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tasks: {e}")
        return []

def get_task(task_id: uuid.UUID) -> Dict[str, Any]:
    """Fetches a single task by its ID."""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching task {task_id}: {e}")
        return None

def submit_bid(task_id: uuid.UUID, agent_id: uuid.UUID, bid_amount: float) -> Dict[str, Any]:
    """Submits a bid for a specific task."""
    bid_data = {
        "task_id": str(task_id),
        "agent_id": str(agent_id),
        "bid_amount": bid_amount,
    }
    try:
        response = requests.post(f"{MARKETPLACE_URL}/bids/", json=bid_data)
        response.raise_for_status()
        print(f"Successfully submitted bid for task {task_id} with amount {bid_amount}")
        return response.json()
    except requests.exceptions.RequestException as e:
        # The marketplace might return a 4xx error if the bid is invalid, which is expected
        if e.response is not None and e.response.status_code >= 400 and e.response.status_code < 500:
             print(f"Could not submit bid for task {task_id}: {e.response.json().get('detail')}")
        else:
            print(f"Error submitting bid for task {task_id}: {e}")
        return None

def select_winner(task_id: uuid.UUID) -> Dict[str, Any]:
    """Selects the winning bid for a task."""
    try:
        response = requests.post(f"{MARKETPLACE_URL}/tasks/{str(task_id)}/select_winner/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error selecting winner for task {task_id}: {e}")
        return None
