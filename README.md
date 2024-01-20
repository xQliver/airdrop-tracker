# Airdrop Tracker Web Application

## Introduction
"Airdrop Tracker" is a web application for cryptocurrency enthusiasts and investors, focusing on tracking transactions and identifying potential airdrops across various wallets and blockchains.

## Features
The application includes several features, organized into different sections:

- **Navbar**
  - Buttons for stats and settings.
  - Options to upload or download a copy of the database.

- **Settings Modal**
  - Add wallets and blockchains (with EVM compatibility option).
  - Delete blockchains.

- **Stats Modal**
  - Displays total volume, total gas spent, total transactions, amount of potential airdrops, and unique airdrop hunting days.

- **Add Transaction**
  - Form for adding transactions, here you can choose the wallet that was used, the blockchain or protocol, if it was an approval or free mint (i.e. no volume) and the date of the transaction. Optionally you can also add gas costs and a comment.

- **EVM Compatible Blockchains**
  - Table displaying transactions on EVM compatible blockchains or dApps. The columns represent the blockchain or dApp, the rows display the wallet. The total volume is displayed, if the last transaction was last day, last week and/or last month, as well as active months and gas spent.

- **Non-EVM Blockchains**
  - Tables displaying transactions for each EVM compatible blockchain or dApp. The columns represent the blockchain or dApp, the rows display the wallet. The total volume is displayed, if the last transaction was last day, last week and/or last month, as well as active months and gas spent.

- **Transactions Section**
  - Lists transactions for each wallet arranged in tabs, with pagination and single transaction delete functionality.

## Getting Started

1. **Install Python**
   - Download and install Python from [python.org](https://www.python.org/downloads/).

2. **Clone Repository**
   - Clone or download the GitHub repository to your local machine.

3. **Install Dependencies**
   - Navigate to the script directory and run `pip install -r requirements.txt`.

4. **Run the Application**
   - Execute the script by clicking on `app.py`, to start the web server. Lastly, access the application through a web browser by entering the address `localhost:5000` or `127.0.0.1:5000`.

5. **Add wallet(s) and blockchain(s)**
    - Press the cogwheel icon to open a dialog where blockchains and wallets can be added to the table. Check the `EVM` checkbox if the blockchain is an Ethereum Virtual Machine compatible blockchain and should be grouped in the same table.

6. **Add transactions**
    - Add new transactions by filling out the information in the transaction fields. Check the checkbox if the transaction was a free mint or an approval with no volume, if you want to track the amount of transactions and total gas costs. The current date and time is automatically selected, but can also be chosen from the date and time picker control. `Gas` and `Comment` are optional fields.

7. **Activity tables**
    - The table(s) will now display the wallet and blockchain activity.

## Screenshots
- **Navbar**
  ![Screenshot of the Navbar](path-to-navbar-screenshot.jpg)

- **Settings Modal**
  ![Screenshot of the Settings Modal](path-to-settings-modal-screenshot.jpg)

- **Info Modal**
  ![Screenshot of the Information Modal](path-to-info-modal-screenshot.jpg)

- **Add Transaction Form**
  ![Screenshot of the Add Transaction section](path-to-add-transaction-form-screenshot.jpg)

- **EVM Compatible Blockchains Table**
  ![Screenshot of the EVM compatible blockchains table](path-to-evm-table-screenshot.jpg)

- **Non-EVM Chains Tables**
  ![Screenshot of the Non-EVM chains tables](path-to-non-evm-tables-screenshot.jpg)

- **Transactions Section**
  ![Screenshot of the Transactions section](path-to-transactions-section-screenshot.jpg)

## Disclaimer
This script is still under development. It is provided "as is" without any guarantees. Users should use it at their own risk.

## Support
If you find this script useful, consider supporting the development by donating to the following EVM (Ethereum, Arbitrum, Optimism, Base, etc.) address: `[Your Ethereum Address Here]`.

## Contribution
Contributions, issues, and feature requests are welcome. Feel free to check [issues page](link-to-issues-page) for open issues or to create a new issue.
