import time

from nexus_knowledge.tasks import long_running_api_call


def submit_job():
    print("Submitting long-running task...")
    task = long_running_api_call.delay("sample input data")
    print(f"Task submitted with ID: {task.id}")
    print("Main application continues to be responsive.")
    # In a real application, you might store task.id to check status later
    # For demonstration, we'll just print it.


if __name__ == "__main__":
    submit_job()
    print("Waiting for 20 seconds to allow worker to process the task...")
    time.sleep(20)
    print("You can check the worker logs to see the task execution.")
