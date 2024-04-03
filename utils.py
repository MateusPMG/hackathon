from app import client
from dotenv import load_dotenv
import os

systemmessage = """
You are a QA expert.
You will receive an user story and generate all the possible test cases considering the success and the failure and give me a list with the titles
"""


def parse_response(response_text):
    print("Response Text:", response_text)  # Print the response text for debugging

    sections = {
        "test_case": None,
        "title": None,
        "description": None,
        "preconditions": None,
        "requirements": None,
        "actions": [],
    }

    current_section = None
    lines = response_text.split("\n")

    for line in lines:
        line = line.strip()
        if line.lower().startswith("test case"):
            current_section = "test_case"
            sections["test_case"] = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("title"):
            current_section = "title"
            sections["title"] = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("description"):
            current_section = "description"
            sections["description"] = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("preconditions"):
            current_section = "preconditions"
            sections["preconditions"] = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("requirements"):
            current_section = "requirements"
            sections["requirements"] = line.split(":", 1)[-1].strip()
        elif line.lower().startswith("actions"):
            current_section = "actions"
        elif current_section == "actions":
            # Check if the line starts with a digit followed by a period
            if re.match(r"^\d+\.\s", line):
                action_step = line.strip()
                expected_result = ""
                sections["actions"].append(
                    {"description": action_step, "expected_result": expected_result}
                )
            elif sections["actions"]:
                # If not a new action, it's part of the expected result of the current action
                sections["actions"][-1]["expected_result"] += line.strip() + " "

    # Remove the redundant "Expected Result:" string from the expected result
    for action in sections["actions"]:
        action["expected_result"] = (
            action["expected_result"].replace("Expected Result:", "").strip()
        )

    return sections


def get_azure_response(input_text):
    message_text = [
        {"role": "system", "content": systemmessage},
        {
            "role": "assistant",
            "content": "Of course! Please provide me with the user story, and I'll generate possible test cases for both success and failure scenarios.",
        },
        {"role": "user", "content": input_text},
    ]
    completion = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=message_text,
        temperature=0.7,
        max_tokens=4096,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )

    # Check if completion has choices and return the content of the first choice
    if completion.choices:
        return completion.choices[0].message.content
    else:
        return "Error: No response received from Azure AI"


def get_developed_tests(previous_response: str, input_text: str) -> str:
    messages = [
        {"role": "system", "content": systemmessage},
        {
            "role": "assistant",
            "content": "Of course! Please provide me with the user story, and I'll generate possible test cases for both success and failure scenarios.",
        },
        {"role": "user", "content": input_text},
        {"role": "assistant", "content": previous_response},
        {
            "role": "user",
            "content": """ok, now based on the previous answer, develop each test case. Each test case must only have the following sections in the following order:
- A section named "test case" with a appropriately generated test case code.
- A title section with a name for the current test case.
- A description section with a short summary of what the test describes and what it tests.
- A preconditions section with the preconditions necessary for this test case.
- A Requirements section with the code name of the requirement being tested, there must be only one per test case.
- A Actions section with as many numbered steps as possible to perform the test and for each step the expected result.""",
        },
    ]
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.8,
        max_tokens=4096,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )

    # Check if completion has choices and return the content of the first choice
    if completion.choices:
        return completion.choices[0].message.content
    else:
        return "Error: No response received from Azure AI"

        