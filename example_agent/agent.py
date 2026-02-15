import time
import json
import os
import uuid

# Local imports
import marketplace_client as client
from skills import analyze_sales_data

# --- Agent Configuration ---
AGENT_CONFIG_FILE = "agent_config.json"
AGENT_CAPABILITIES = ["data_analysis", "python", "csv"]

class Agent:
    def __init__(self):
        self.agent_id = None
        self.capabilities = AGENT_CAPABILITIES
        self.bids_made = set()
        self.load_or_register()

    def load_or_register(self):
        """Load agent config from file or register a new one."""
        if os.path.exists(AGENT_CONFIG_FILE):
            print("Found existing agent configuration.")
            with open(AGENT_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.agent_id = uuid.UUID(config['agent_id'])
        else:
            print("No agent configuration found. Registering a new agent...")
            agent_info = client.register_agent(self.capabilities)
            if agent_info:
                self.agent_id = uuid.UUID(agent_info['agent_id'])
                with open(AGENT_CONFIG_FILE, 'w') as f:
                    json.dump({"agent_id": str(self.agent_id)}, f)
                print(f"Agent registered with ID: {self.agent_id}")
            else:
                print("Could not register agent. Exiting.")
                exit()
    
    def is_qualified(self, task: dict) -> bool:
        """Check if the agent is qualified for a given task."""
        required = set(task.get('required_capabilities', []))
        return required.issubset(self.capabilities)

    def run(self):
        """The main loop for the agent."""
        print(f"--- Starting Agent {self.agent_id} ---")
        while True:
            print("Checking for new tasks...")
            try:
                tasks = client.get_tasks()
                if not tasks:
                    print("No tasks found.")
                else:
                    for task in tasks:
                        task_id_str = task['task_id']
                        # Check if task is open for bidding and if we haven't already bid
                        if task['status'] == 'POSTED' and task_id_str not in self.bids_made:
                            print(f"Found new task: {task['title']}")
                            if self.is_qualified(task):
                                print("Agent is qualified. Submitting bid.")
                                # Simple bidding strategy: bid 10% less than the reward
                                bid_amount = task['reward_amount'] * 0.9
                                client.submit_bid(
                                    task_id=uuid.UUID(task_id_str),
                                    agent_id=self.agent_id,
                                    bid_amount=bid_amount
                                )
                                self.bids_made.add(task_id_str)
                            else:
                                print("Agent is not qualified for this task.")
            
            except Exception as e:
                print(f"An error occurred in the main loop: {e}")

            # Wait for a bit before the next cycle
            print("--- Cycle finished. Sleeping for 30 seconds. ---")
            time.sleep(30)

if __name__ == "__main__":
    agent = Agent()
    agent.run()
