import os
from datetime import datetime
from flask import Flask, render_template, request, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# Set the UPLOAD_FOLDER relative to the project root
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files")
ALLOWED_EXTENSIONS = {"db"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///airdrop.db"
db = SQLAlchemy(app)


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    transactions = db.relationship("Transaction", backref="wallet", lazy=True)


class Blockchain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    evm = db.Column(db.Integer, nullable=False)
    transactions = db.relationship("Transaction", backref="blockchain", lazy=True)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    blockchain_id = db.Column(db.Integer, db.ForeignKey("blockchain.id"), nullable=False)


def within_same_day(date):
    if date is None:
        return False
    else:
        today_utc = datetime.utcnow().date()
        return today_utc == date.date()


def within_same_week(date):
    if date is None:
        return False
    else:
        current_date = datetime.utcnow()
        return (
            current_date.isocalendar()[1] == date.isocalendar()[1]
            and current_date.year == date.year
        )


def within_same_month(date):
    if date is None:
        return False
    else:
        current_date = datetime.utcnow()
        return current_date.month == date.month and current_date.year == date.year


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    wallets = Wallet.query.all()
    blockchains = Blockchain.query.all()
    transactions = Transaction.query.all()

    matrix = []
    for wallet in wallets:
        row = []
        for blockchain in blockchains:
            # Get the transactions for this wallet and blockchain
            wallet_blockchain_transactions = [
                transaction
                for transaction in wallet.transactions
                if transaction.blockchain == blockchain
            ]

            # Calculate the total volume
            volume = sum(transaction.volume for transaction in wallet_blockchain_transactions)

            # Get the date of the last transaction
            last_date = (
                max(transaction.date for transaction in wallet_blockchain_transactions)
                if wallet_blockchain_transactions
                else None
            )

            # Count unique months transacted
            unique_months = set()
            for transaction in wallet_blockchain_transactions:
                year_month = (transaction.date.year, transaction.date.month)
                unique_months.add(year_month)
            num_unique_months = len(unique_months)

            # Count total number of transactions
            total_transactions = len(wallet_blockchain_transactions)

            # Append the blockchain name, volume, last transaction date, unique months, and total transactions to the row
            row.append((blockchain.name, volume, last_date, num_unique_months, total_transactions))

        matrix.append((wallet.name, row))

    return render_template(
        "home.html",
        wallets=wallets,
        blockchains=blockchains,
        transactions=transactions,
        matrix=matrix,
        within_same_day=within_same_day,
        within_same_week=within_same_week,
        within_same_month=within_same_month,
    )


@app.route("/add_wallet", methods=["POST"])
def add_wallet():
    name = request.form.get("name")
    new_wallet = Wallet(name=name)
    db.session.add(new_wallet)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add_blockchain", methods=["POST"])
def add_blockchain():
    name = request.form.get("name")
    new_blockchain = Blockchain(name=name)
    db.session.add(new_blockchain)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    wallet_id = request.form.get("wallet_id")
    blockchain_id = request.form.get("blockchain_id")
    volume = request.form.get("volume")
    date = request.form.get("date")
    date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M")

    new_transaction = Transaction(
        volume=volume, wallet_id=wallet_id, blockchain_id=blockchain_id, date=date_obj
    )
    db.session.add(new_transaction)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete_transaction/<int:id>", methods=["POST"])
def delete_transaction(id):
    transaction = Transaction.query.get(id)
    if transaction:
        db.session.delete(transaction)
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/upload_db", methods=["POST"])
def upload_db():
    # Check if a valid file has been uploaded
    if "file" not in request.files:
        return "No file part"
    file = request.files["file"]
    if file.filename == "":
        return "No selected file"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        # replace the current db file with the uploaded one
        os.replace(os.path.join(app.config["UPLOAD_FOLDER"], filename), UPLOAD_FOLDER)
        return "File successfully uploaded"
    else:
        return "Allowed file types are .db"


@app.route("/download_db", methods=["GET"])
def download_db():
    # Specify the path to the db file
    db_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "instance", "airdrop.db"
    )
    return send_file(db_file_path, as_attachment=True)


if __name__ == "__main__":
    with app.app_context():
        if not os.path.exists("airdrop.db"):
            db.create_all()
    app.run(debug=True)
