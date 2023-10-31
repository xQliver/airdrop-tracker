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

    evm_blockchains = [blockchain for blockchain in blockchains if blockchain.evm == 1]
    non_evm_blockchains = [blockchain for blockchain in blockchains if blockchain.evm == 0]

    # EVM Wallets Matrix
    evm_matrix = []
    for wallet in wallets:
        row = []
        has_interaction = False
        for blockchain in evm_blockchains:
            data = _get_wallet_blockchain_data(wallet, blockchain)
            row.extend(data)
            if data[0][1] > 0:  # If there's any volume, it indicates an interaction
                has_interaction = True
        if has_interaction:  # Only add to the matrix if there was an interaction
            evm_matrix.append((wallet.name, row))

    evm_wallet_names = [entry[0] for entry in evm_matrix]
    evm_wallets = [wallet for wallet in wallets if wallet.name in evm_wallet_names]

    # Non-EVM Wallets Matrix (one per blockchain)
    non_evm_matrices = {}
    for blockchain in non_evm_blockchains:
        matrix = []
        for wallet in wallets:
            row = _get_wallet_blockchain_data(wallet, blockchain)
            if any(data[1] for data in row):  # Check if there's any volume, indicating interaction
                matrix.append((wallet.name, row))
        non_evm_matrices[blockchain.name] = matrix

    return render_template(
        "home.html",
        wallets=wallets,  # For adding new transactions
        evm_wallets=evm_wallets,  # EVM compatible wallets
        evm_matrix=evm_matrix,  # EVM blockchain matrix
        non_evm_matrices=non_evm_matrices,  # Matrices of all non-EVM based blockchains
        transactions=transactions,  # List of all transactions
        non_evm_blockchains=non_evm_blockchains,  # All non-EVM blockchains
        within_same_day=within_same_day,
        within_same_week=within_same_week,
        within_same_month=within_same_month,
    )


def _get_wallet_blockchain_data(wallet, blockchain):
    # Helper function to get wallet-blockchain interaction data
    wallet_blockchain_transactions = [
        transaction for transaction in wallet.transactions if transaction.blockchain == blockchain
    ]

    volume = sum(transaction.volume for transaction in wallet_blockchain_transactions)
    last_date = (
        max(transaction.date for transaction in wallet_blockchain_transactions)
        if wallet_blockchain_transactions
        else None
    )

    unique_months = set(
        (transaction.date.year, transaction.date.month)
        for transaction in wallet_blockchain_transactions
    )
    num_unique_months = len(unique_months)
    total_transactions = len(wallet_blockchain_transactions)

    return [(blockchain.name, volume, last_date, num_unique_months, total_transactions)]


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
