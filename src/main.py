import time

from nexus_knowledge.tasks import persist_feedback


def submit_job() -> None:
    print("Submitting feedback persistence task...")
    task = persist_feedback.delay(
        "00000000-0000-0000-0000-000000000000",
        {"feedback_type": "demo", "message": "Sample", "user_id": None},
        correlation_id="demo-corr-id",
    )
    print(f"Task submitted with ID: {task.id}")
    print("Main application continues to be responsive.")


if __name__ == "__main__":
    submit_job()
    print("Waiting for 20 seconds to allow worker to process the task...")
    time.sleep(20)
    print("You can check the worker logs to see the task execution.")
