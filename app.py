import os
from utils import *
from flask import Flask, render_template, request, session, redirect, url_for
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("AZURE_OPENAI_KEY")
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
    session["user_input"] = user_input
    response = get_azure_response(user_input)
    session["responsep"] = response
    successT, failureT = parse_input(response)
    responsep = {"successT": successT, "failureT": failureT}
    session["responsep"] = response
    session["listsplit"] = responsep
    return render_template("middle.html", responsep=responsep)


@app.route("/testCases", methods=["POST"])
def middleResponse():
    pass


@app.route("/final", methods=["POST"])
def response_page():
    responsep = session.get("responsep")
    if responsep is None:
        clear_session()
        return render_template("index.html")
    testsall = get_developed_tests(responsep)
    # final = parse_response(testsall)

    return render_template("response.html", finald=testsall)


@app.route("/remake")
def remake():
    previous_response = session.get("responsep")
    user_input = session.get("user_input")
    if previous_response is None or user_input is None:
        clear_session()
        return render_template("index.html")
    new_response = get_remake_response(previous_response, user_input)
    successT, failureT = parse_input(new_response)
    session["responsep"] = new_response
    responsep = {"successT": successT, "failureT": failureT}
    return render_template("middle.html", responsep=responsep)


@app.route("/clean")
def clean():
    # logica para limpiar la base de datos
    clear_session()
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
