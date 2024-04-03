import os
import re
from utils import *
from flask import Flask, render_template, request
from openai import AzureOpenAI
from dotenv import load_dotenv

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
    responsep = {"successT" : successT, "failureT" : failureT }
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
    app.run(debug=True)
