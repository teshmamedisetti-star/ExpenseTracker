
from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
from datetime import date

app = Flask(__name__)
app.secret_key = "expense_tracker_secret_key"

DATA_FILE = "expenses.json"


def load_expenses():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_expenses(expenses):
    with open(DATA_FILE, "w") as file:
        json.dump(expenses, file, indent=4)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        amount_text = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip()
        expense_date = request.form.get("expense_date", "").strip()

        try:
            amount = float(amount_text)
            if amount <= 0 or not amount < float("inf"):
                raise ValueError
        except (ValueError, OverflowError):
            flash("Please enter a valid positive amount.")
            return redirect(url_for("home"))

        if not title or not category or not expense_date:
            flash("Please fill in all fields.")
            return redirect(url_for("home"))

        expenses = load_expenses()
        next_id = max(
            (expense.get("id", 0) for expense in expenses),
            default=0
        ) + 1

        expenses.append({
            "id": next_id,
            "title": title,
            "amount": amount,
            "category": category,
            "date": expense_date
        })

        save_expenses(expenses)
        flash("Expense added successfully!")
        return redirect(url_for("home"))

    expenses = load_expenses()
    total = sum(expense["amount"] for expense in expenses)

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        today=date.today().isoformat()
    )


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    expenses = load_expenses()
    updated_expenses = [
        expense for expense in expenses
        if expense.get("id") != expense_id
    ]

    if len(updated_expenses) == len(expenses):
        flash("Expense not found.")
    else:
        save_expenses(updated_expenses)
        flash("Expense deleted successfully!")

    return redirect(url_for("home"))


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    expenses = load_expenses()

    expense = next(
        (item for item in expenses if item.get("id") == expense_id),
        None
    )

    if expense is None:
        flash("Expense not found.")
        return redirect(url_for("home"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        amount_text = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip()
        expense_date = request.form.get("expense_date", "").strip()

        try:
            amount = float(amount_text)
            if amount <= 0 or not amount < float("inf"):
                raise ValueError
        except (ValueError, OverflowError):
            flash("Please enter a valid positive amount.")
            return redirect(url_for("edit_expense", expense_id=expense_id))

        if not title or not category or not expense_date:
            flash("Please fill in all fields.")
            return redirect(url_for("edit_expense", expense_id=expense_id))

        expense["title"] = title
        expense["amount"] = amount
        expense["category"] = category
        expense["date"] = expense_date

        save_expenses(expenses)
        flash("Expense updated successfully!")
        return redirect(url_for("home"))

    return render_template("edit.html", expense=expense)



if __name__ == "__main__":
    app.run(debug=True)
