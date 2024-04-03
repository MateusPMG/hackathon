import os
from flask import Flask, render_template, request
from openai import AzureOpenAI
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)

# Initialize AzureOpenAI client
client = AzureOpenAI(
    azure_endpoint="https://escola42.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview"
)

@app.route('/')
def index():
    return render_template('index.html', response=None)

@app.route('/response', methods=['POST'])
def response():
    user_input = request.form['user_input']
    response_text = get_azure_response(user_input)
       
    # Attempt to parse the response
    parsed_response = parse_response(response_text)
    
    print("Parsed Response:", parsed_response)  # Add this line
    
    if parsed_response:
        # Render the response template with extracted variables
        return render_template('response.html', response=parsed_response)
    else:
        return render_template('response.html', response=None)

import re

def parse_response(response_text):
    print("Response Text:", response_text)  # Print the response text for debugging
    
    # Define patterns for each section of the test case
    test_case_pattern = r"(?:Test Case ID:|A test case:|Test Case)?\s*(.*?)\n?Title: (.*?)\n?Description: (.*?)\n?Preconditions: (.*?)\n?Requirements: (.*?)\n?Actions:\n?(.*?)(?=\n\n|$)"

    # Use the combined pattern to search for matches in the response text
    match = re.search(test_case_pattern, response_text, re.DOTALL)
    print("Match:", match)  # Print the match object for debugging
    
    if match:
        # Extract the matched groups for each section
        test_case = match.group(1).strip()
        title = match.group(2).strip()
        description = match.group(3).strip()
        preconditions = match.group(4).strip()
        requirements = match.group(5).strip()
        actions_text = match.group(6).strip()

        print("Test Case:", test_case)  # Print the test case ID for debugging
        print("Title:", title)  # Print the title for debugging
        print("Description:", description)  # Print the description for debugging
        print("Preconditions:", preconditions)  # Print the preconditions for debugging
        print("Requirements:", requirements)  # Print the requirements for debugging
        print("Actions Text:", actions_text)  # Print the actions text for debugging

        # Split actions_text into individual actions and expected results
        actions_matches = re.findall(r"(\d+\.\s.*?)\n\s*- Expected result:\s*(.*?)(?=\d+\.\s|\Z)", actions_text, re.DOTALL)
        print("Actions Matches:", actions_matches)  # Print the actions matches for debugging
        
        actions = [{"description": action[0].strip(), "expected_result": action[1].strip() if action[1] else ""} for action in actions_matches]
        print("Actions:", actions)  # Print the parsed actions for debugging

        return {
            "test_case": test_case,
            "title": title,
            "description": description,
            "preconditions": preconditions,
            "requirements": requirements,
            "actions": actions
        }
    else:
        print("No match found for response text:", response_text)  # Print if no match found for debugging
        return None

def get_azure_response(input_text):
    message_text = [{"role": "system", "content": systemmessage},
	{"role": "user", "content": input_text}]
    completion = client.chat.completions.create(
        model="gpt4",
        messages=message_text,
        temperature=0.7,
        max_tokens=4096,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    
    # Check if completion has choices and return the content of the first choice
    if completion.choices:
        return completion.choices[0].message.content
    else:
        return "Error: No response received from Azure AI"

systemmessage = """
You are a QA expert.
You generate a single appropriate test case you can for a given user story.
You musnt use #, ##, ###, or #### in the test case.
A test case must only have the following sections in the following order:
- A test case, section with a appropriately generated test case code.
- A title section with a name for the current test case.
- A description section with a short summary of what the test describes and what it tests.
- A preconditions section with the preconditions necessary for this test case.
- A Requirements section with the code name of the requirement being tested, there must be only one per test case.
- A Actions section with as many steps as possible to perform the test and for each step the expected result.
"""

if __name__ == '__main__':
    app.run(debug=True)
