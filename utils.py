from app import client
from dotenv import load_dotenv
import os
import re

systemmessage = """
You are a QA expert.
For a given user story give me a list of test case titles.
The list will be divided ONLY into success and failure test case groups.
Each group will be divided ONLY by requirements.
The format will be the following:
-Success Test Cases
-Each requirement followed by its success test cases
-Failure Test cases
-Each requirement followed by its failure test cases
it must also follow these directives:
-group titles will be preceded by a single '#'
-requirement titles will be preceded by a single '*'
-test cases will be preceded by a single '-'

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


def parseinput(input: str):
    successT, failureT = {}, {}
    print("Input str:", input)
    # Split input into success and failure test cases
    try:
        success_tests, failure_tests = input.split("# Failure Test Cases")
    except ValueError:
        print("Error: Input string does not contain the expected delimiter.")
        return {}, {}

    # Check if success_tests contains the delimiter
    if "# Success Test Cases" not in success_tests:
        print(
            "Error: Input string does not contain the delimiter for success test cases."
        )
        return {}, {}

    # Parse success test cases
    success_cases = success_tests.split("# Success Test Cases")[1].strip()
    success_tests = success_cases.split("* ")
    for test_case in success_tests[1:]:
        req_id_name, tests = test_case.split("\n  - ", 1)
        req_id, req_name = req_id_name.split(maxsplit=1)
        tests = [test.strip() for test in tests.split("\n  - ")]
        successT[req_id] = {"requirname": req_id_name, "tests": tests}

    # Parse failure test cases
    failure_cases = failure_tests.strip()
    failure_tests = failure_cases.split("* ")
    for test_case in failure_tests[1:]:
        req_id_name, tests = test_case.split("\n  - ", 1)
        req_id, req_name = req_id_name.split(maxsplit=1)
        tests = [test.strip() for test in tests.split("\n  - ")]
        failureT[req_id] = {"requirname": req_id_name, "tests": tests}

    return successT, failureT
