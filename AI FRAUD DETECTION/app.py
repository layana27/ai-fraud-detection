import os
import sqlite3
from functools import wraps

import joblib
import pandas as pd
from flask import (
    Flask, render_template, request,
    redirect, url_for, session
)
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_database

app = Flask(__name__)

# Secret key for login sessions.
# Configure FLASK_SECRET_KEY in Render before deployment.
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "local-development-only-change-before-deployment"
)

# Create database tables.
create_database()

# Load the trained machine-learning model.
model = joblib.load("fraud_model.pkl")


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


def save_transaction(amount, transaction_type, location, result):
    connection = sqlite3.connect("fraud_transactions.db")
    try:
        connection.execute("""
            INSERT INTO transactions
            (amount, transaction_type, location, result)
            VALUES (?, ?, ?, ?)
        """, (amount, transaction_type, location, result))
        connection.commit()
    finally:
        connection.close()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            error = "Please complete all fields."
        elif len(name) > 100 or len(email) > 254:
            error = "The name or email is too long."
        elif len(password) < 8:
            error = "Password must contain at least 8 characters."
        else:
            password_hash = generate_password_hash(password)
            connection = sqlite3.connect("fraud_transactions.db")

            try:
                connection.execute("""
                    INSERT INTO users (name, email, password_hash)
                    VALUES (?, ?, ?)
                """, (name, email, password_hash))
                connection.commit()
                return redirect(url_for("login", registered="1"))

            except sqlite3.IntegrityError:
                error = "An account with this email already exists."
            finally:
                connection.close()

    return render_template("signup.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    message = ""

    if request.args.get("registered") == "1":
        message = "Registration successful. Please log in."

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = sqlite3.connect("fraud_transactions.db")
        connection.row_factory = sqlite3.Row

        try:
            user = connection.execute(
                "SELECT id, name, email, password_hash "
                "FROM users WHERE email = ?",
                (email,)
            ).fetchone()
        finally:
            connection.close()

        if user and check_password_hash(
            user["password_hash"], password
        ):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("fraud_detection"))

        error = "Invalid email or password."

    return render_template(
        "login.html", error=error, message=message
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/fraud-detection", methods=["GET", "POST"])
@login_required
def fraud_detection():
    result = ""
    reason = ""

    if request.method == "POST":
        amount_text = request.form.get("amount", "").strip()
        transaction_type = request.form.get(
            "transaction_type", ""
        ).strip()
        location = request.form.get("location", "").strip()

        try:
            amount = float(amount_text)

            if amount <= 0:
                result = "Please enter a valid amount."
                reason = "The transaction amount must be greater than zero."

            elif not transaction_type or not location:
                result = "Missing Information"
                reason = "Please enter all transaction details."

            else:
                transaction = pd.DataFrame([{
                    "amount": amount,
                    "transaction_type": transaction_type,
                    "location": location
                }])

                prediction = model.predict(transaction)[0]

                if prediction == 1:
                    result = "Suspicious Transaction Detected!"
                    reason = (
                        "The machine-learning model classified "
                        "this transaction as suspicious."
                    )
                else:
                    result = "Transaction Appears Safe."
                    reason = (
                        "The machine-learning model classified "
                        "this transaction as safe."
                    )

                save_transaction(
                    amount, transaction_type, location, result
                )

        except (ValueError, TypeError):
            result = "Invalid Amount"
            reason = "Please enter a valid number."

    return render_template(
        "index.html",
        result=result,
        reason=reason,
        user_name=session.get("user_name", "")
    )


if __name__ == "__main__":
    app.run(debug=True)
