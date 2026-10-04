from flask import Flask, render_template, request
import pandas as pd
import joblib
import sqlite3

app = Flask(__name__)

# Load the trained machine-learning model
model = joblib.load("fraud_model.pkl")


# Save transaction details into SQLite database
def save_transaction(amount, transaction_type, location, result):
    connection = sqlite3.connect("fraud_transactions.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (amount, transaction_type, location, result)
        VALUES (?, ?, ?, ?)
    """, (amount, transaction_type, location, result))

    connection.commit()
    connection.close()


@app.route("/", methods=["GET", "POST"])
def home():

    result = ""
    reason = ""

    if request.method == "POST":

        amount_text = request.form.get("amount")
        transaction_type = request.form.get("transaction_type")
        location = request.form.get("location")

        try:
            amount = float(amount_text)

            if amount <= 0:
                result = "⚠️ Please enter a valid amount."
                reason = "The transaction amount must be greater than zero."

            else:
                # Prepare the transaction data
                transaction = pd.DataFrame([
                    {
                        "amount": amount,
                        "transaction_type": transaction_type,
                        "location": location
                    }
                ])

                # Predict using the trained model
                prediction = model.predict(transaction)[0]

                if prediction == 1:
                    result = "⚠️ Suspicious Transaction Detected!"
                    reason = "The machine-learning model classified this transaction as suspicious."

                else:
                    result = "✅ Transaction Appears Safe."
                    reason = "The machine-learning model classified this transaction as safe."

                # Save the checked transaction into SQLite
                save_transaction(
                    amount,
                    transaction_type,
                    location,
                    result
                )

        except ValueError:
            result = "⚠️ Invalid Amount"
            reason = "Please enter a valid number."

    return render_template(
        "index.html",
        result=result,
        reason=reason
    )


if __name__ == "__main__":
    app.run(debug=True)