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
    successT, failureT = parse_input(response)
    responsep = {"successT": successT, "failureT": failureT}
    print("Response:", responsep)
    return render_template("middle.html", responsep=responsep)


@app.route("/testCases", methods=["POST"])
def middleResponse():
    pass


@app.route("/accept", methods=["POST"])
def accept():
    return render_template("index.html")


@app.route("/clean")
def clean():
    # logica para limpiar la base de datos
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
