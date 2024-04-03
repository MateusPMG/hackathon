import os
from utils import *
from openai import AzureOpenAI
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)

# Initialize AzureOpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("API_VERSION"),
)


@app.route("/")
def index():
    return render_template("index.html", response=None)


@app.route("/response", methods=["POST"])
def response():
    user_input = request.form["user_input"]
    response = get_azure_response(user_input)
    successT, failureT = parseinput(response)
    responsep = {"successT": successT, "failureT": failureT}
    print("Response:", responsep)
    responsep = {
        "successT": {
            "REQ-UCC06-010": {
                "requirname": "REQ-UCC06-010 Privacy policy consent",
                "tests": [
                    "Verify that on application start or resume, the Privacy Policy overlay or modal window is displayed.",
                    "Verify that the Privacy Policy content is correctly displayed within the modal.",
                    'Verify that "Accept and Close" button functions correctly and allows the user to proceed with the application upon acceptance.',
                    "Verify that the system records the user's consent along with the date and time stamp when the user accepts the Privacy Policy.",
                ],
            },
            "REQ-UCC06-020": {
                "requirname": "REQ-UCC06-020 Cookies policy",
                "tests": [
                    "Verify that on application start or resume, the Cookies policy header/footer overlay is displayed.",
                    "Verify that the Cookies policy content is correctly displayed within the overlay.",
                    'Verify that there is only an option to "Allow cookies" and no option to block them.',
                    'Verify that clicking on "Allow cookies" allows the user to proceed with the application.',
                    "Verify that the system records the user's consent to the Cookies policy along with the date and time stamp when the user allows cookies.",
                ],
            },
        },
        "failureT": {
            "REQ-UCC06-010": {
                "requirname": "REQ-UCC06-010 Privacy policy consent",
                "tests": [
                    'Verify that the user cannot proceed with the application if the "Accept and Close" button is not clicked.',
                    "Verify that the system does not record consent if the user does not accept the Privacy Policy.",
                    "Verify that the user remains on the initial step of the application if the Privacy Policy is not accepted.",
                ],
            },
            "REQ-UCC06-020": {
                "requirname": "REQ-UCC06-020 Cookies policy",
                "tests": [
                    'Verify that the user cannot proceed with the application if the "Allow cookies" option is not selected.',
                    "Verify that the system does not record consent to the Cookies policy if the user does not allow cookies.",
                    "Verify that the user remains on the initial step of the application if the Cookies policy is not accepted.",
                ],
            },
        },
    }
    return render_template("middle.html", responsep=responsep)


@app.route("/testCases", methods=["POST"])
def middleResponse():
    pass


# @app.route("/response", methods=["POST"])
# def response():
#     user_input = request.form["user_input"]
#     response = get_azure_response(user_input)
#     response_text = get_developed_tests(response)

#     # Attempt to parse the response
#     parsed_response = parse_response(response_text)

#     print("Parsed Response:", parsed_response)  # Add this line

#     if parse_response:
#         # Render the response template with extracted variables "
#         return render_template("response.html", response=parsed_response)
#     else:
#         return render_template("response.html", response=None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
