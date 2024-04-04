from app import client
import os
import re
from flask import session

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

import re


def trim_input(input_text):
    # Split the input text into lines
    lines = input_text.split("\n")

    # Define a regex pattern to match '#', '*', and spaces at the beginning of each line
    pattern = r"^[\s*#]+"

    # Iterate through each line and apply the regex pattern to trim unwanted characters
    trimmed_lines = [re.sub(pattern, "", line) for line in lines]

    # Join the trimmed lines back together to form the modified input text
    trimmed_input_text = "\n".join(trimmed_lines)

    return trimmed_input_text


import re

import re


def parse_response(response_text):
    test_cases = []
    print(response_text)
    # Split response text into individual test case blocks
    test_case_blocks = re.split(
        r"(?m)^(?:.*?Test Case:\s*|## Test Case:)\s*", response_text.strip()
    )
    for block in test_case_blocks:
        if not block.strip():
            continue

        test_case = {}

        # Extract test case ID
        match_test_case = re.search(r"^[#\*]+\s*Test\s*Case\s*(\d+)", block)
        if match_test_case:
            test_case["test_case"] = match_test_case.group(1).strip()

        # Extract test case details
        match_title = re.search(r"[#\*]+\s*Title:\s*(.+?)\n", block)
        if match_title:
            test_case["title"] = match_title.group(1).strip()

        match_description = re.search(
            r"(?:#+\s*)?Description\s*(?::|\*\*)\s*(.+)", block
        )
        if match_description:
            test_case["description"] = match_description.group(1).strip()

        match_preconditions = re.search(r"\*\*Preconditions:\*\*\s*(.+)", block)
        if match_preconditions:
            test_case["preconditions"] = match_preconditions.group(1).strip()

        match_requirements = re.search(r"\*\*Requirements:\*\*\s*(.+)", block)
        if match_requirements:
            test_case["requirements"] = match_requirements.group(1).strip()

        # Extract actions
        actions = []
        action_matches = re.finditer(
            r"\*\*Actions:\s*\n((?:\d+|\*)\.\s*(?:.+?)\n\s*-\s*Expected Result:\s*(?:.+)(?:\n|$))+",
            block,
            re.DOTALL,
        )
        for match in action_matches:
            step = match.group(1)
            description = match.group(2)
            expected_result = match.group(3)
            actions.append(
                {
                    "step": step,
                    "description": description.strip(),
                    "expected_result": expected_result.strip(),
                }
            )

        if actions:
            test_case["actions"] = actions

        test_cases.append(test_case)
    print(test_cases)
    return test_cases


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


def get_developed_tests(previous_response: str) -> str:
    messages = [
        {"role": "system", "content": systemmessage},
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


def parse_input(input_str: str):
    success_tests, failure_tests = {}, {}

    sections = input_str.split("#")

    for section in sections:
        if "Success Test Cases" in section:
            success_cases = section.split("Success Test Cases")[1].strip()
            parse_test_cases(success_tests, success_cases)
        elif "Failure Test Cases" in section:
            failure_cases = section.split("Failure Test Cases")[1].strip()
            parse_test_cases(failure_tests, failure_cases)

    return success_tests, failure_tests


def parse_test_cases(test_dict, test_cases_str):
    current_req = None
    test_cases = [test.strip() for test in test_cases_str.split("\n") if test.strip()]

    for test_case in test_cases:
        if test_case.startswith("*"):
            req_id_name = test_case.split("*")[1].strip()
            current_req = req_id_name
            test_dict[current_req] = []
        elif test_case.startswith("-"):
            if current_req:
                test_dict[current_req].append(test_case.strip())


def clear_session():
    # Clear the session data
    session.pop("responsep", None)
    session.pop("user_input", None)


def get_remake_response(previous_response: str, user_input: str) -> str:
    messages = [
        {"role": "system", "content": systemmessage},
        {
            "role": "assistant",
            "content": "Of course! Please provide me with the user story, and I'll generate possible test cases for both success and failure scenarios.",
        },
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": previous_response},
        {
            "role": "user",
            "content": "I didn't like this list, please make another different one taking into the account the user story that i gave you.",
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
