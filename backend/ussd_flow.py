from pydantic import BaseModel
from typing import Dict, Any
import random
from ai_engines import NdalamaMicroLending, CilimbaGuard, MarketAnalyzer, BankVerificationAgent

# In-memory session store for simulation
# Structure: { phone_number: { "state": "MAIN_MENU", "data": {} } }
sessions: Dict[str, Dict[str, Any]] = {}

def process_ussd_request(phone_number: str, text: str) -> str:
    # Initialize session if empty text or new session
    if text == "" or phone_number not in sessions:
        sessions[phone_number] = {"state": "MAIN_MENU", "data": {}}
        return get_menu_text("MAIN_MENU", sessions[phone_number])
    
    session = sessions[phone_number]
    current_state = session["state"]
    
    # Process user input and calculate next state
    next_state = handle_input(current_state, text, session, phone_number)
    session["state"] = next_state
    
    return get_menu_text(next_state, session)

def handle_input(state: str, text: str, session: dict, phone_number: str) -> str:
    # Global navigation back to main menu
    if text == "0":
        return "MAIN_MENU"
        
    if state == "MAIN_MENU":
        if text == "1":
            return "MICRO_LENDING_START"
        elif text == "2":
            return "CILIMBA_GUARD_START"
        elif text == "3":
            return "ACCOUNT_INFO"
        elif text == "4":
            return "MARKET_MENU"
        elif text == "5":
            return "BANK_VERIFY_MENU"
        else:
            return "MAIN_MENU"
            
    elif state == "MICRO_LENDING_START":
        if text == "1":
            # Process loan using AI engine
            eval_result = NdalamaMicroLending.evaluate_credit(phone_number)
            session["data"]["loan_eval"] = eval_result
            return "MICRO_LENDING_RESULT"
        else:
            return "MICRO_LENDING_START"
            
    elif state == "MICRO_LENDING_RESULT":
        eval_result = session["data"].get("loan_eval", {})
        debt = eval_result.get("current_debt_zm", 0)
        
        if eval_result.get("approved"):
            if text == "1":
                return "LOAN_ACCEPTED"
            elif text == "2" and debt > 0:
                session["data"]["repaid_amount"] = debt
                return "LOAN_REPAID"
            elif text == "3" and debt > 0:
                return "PARTIAL_REPAYMENT_INPUT"
        else:
            if text == "1" and debt > 0:
                session["data"]["repaid_amount"] = debt
                return "LOAN_REPAID"
            elif text == "2" and debt > 0:
                return "PARTIAL_REPAYMENT_INPUT"
        return "MAIN_MENU"
        
    elif state == "PARTIAL_REPAYMENT_INPUT":
        eval_result = session["data"].get("loan_eval", {})
        debt = eval_result.get("current_debt_zm", 0)
        try:
            amount = float(text)
            if amount > 0:
                session["data"]["repaid_amount"] = amount
                return "LOAN_REPAID"
        except ValueError:
            pass
        return "PARTIAL_REPAYMENT_INPUT"
            
    elif state == "CILIMBA_GUARD_START":
        if text == "1":
            # Check group status using AI engine
            # Hardcoded group ID for simulation purposes
            eval_result = CilimbaGuard.evaluate_group_resilience("GRP-ZAM-001")
            session["data"]["group_eval"] = eval_result
            return "CILIMBA_GUARD_RESULT"
        else:
            return "CILIMBA_GUARD_START"
            
    elif state == "MARKET_MENU":
        if not MarketAnalyzer.is_valid_commodity(text):
            return "MARKET_NOT_FOUND"
        session["data"]["market_commodity"] = text
        return "MARKET_QUANTITY_INPUT"
        
    elif state == "MARKET_QUANTITY_INPUT":
        try:
            qty = float(text)
            if qty > 100:
                return "MARKET_QUANTITY_TOO_HIGH"
            if qty <= 0:
                raise ValueError
        except ValueError:
            return "MARKET_QUANTITY_INPUT" # Ask again or default
            
        commodity = session["data"]["market_commodity"]
        market_data = MarketAnalyzer.get_market_data(commodity, quantity_kg=qty)
        session["data"]["market_data"] = market_data
        return "MARKET_RESULT"


    elif state == "MARKET_RESULT":
        data = session["data"]["market_data"]
        return "MAIN_MENU" # This isn't actually used this way, it just continues if they type 0.
        
    elif state == "BANK_VERIFY_MENU":
        if text == "0":
            return "MAIN_MENU"
        elif len(text) >= 4 and text.isdigit():
            return "BANK_ACTION_MENU"
        else:
            return "BANK_VERIFY_MENU" # Invalid PIN, stay here

    elif state == "BANK_ACTION_MENU":
        if text == "1":
            txns = BankVerificationAgent.get_recent_transactions("1234")
            session["data"]["recent_txns"] = txns
            return "BANK_RECENT_TRANSACTIONS"
        elif text == "2":
            return "BANK_VERIFY_AMOUNT"
        
    elif state == "BANK_VERIFY_AMOUNT":
        if text == "0": return "MAIN_MENU"
        try:
            amt = float(text)
            res = BankVerificationAgent.verify_transaction("TXN", amt)
            session["data"]["verify_res"] = res
            return "BANK_VERIFY_RESULT"
        except ValueError:
            return "BANK_VERIFY_AMOUNT"

    elif state == "BANK_VERIFY_RESULT":
        return "MAIN_MENU"
        
    elif state == "BANK_RECENT_TRANSACTIONS":
        return "MAIN_MENU"
            
    # Default fallback
    return "MAIN_MENU"

def get_menu_text(state: str, session: dict) -> str:
    if state == "MAIN_MENU":
        return (
            "Welcome to NdalamaLite\n"
            "1. Get a Loan\n"
            "2. Savings Group Health\n"
            "3. My Account\n"
            "4. Market Prices\n"
            "5. Bank Verification Agent\n"
        )
    elif state == "ACCOUNT_INFO":
        eval_result = session["data"].get("loan_eval")
        if eval_result:
            score = session["data"].get("updated_score", eval_result["score"])
            debt = eval_result.get("current_debt_zm", 0)
        else:
            score = 50
            debt = 0
            
        # Simulated account data based on phone number
        balance = random.randint(120, 980)
        # Store balance so it stays consistent in session
        if "account_balance" not in session["data"]:
            session["data"]["account_balance"] = balance
        else:
            balance = session["data"]["account_balance"]
        
        debt_line = f"Outstanding Loan: ZMW {debt}\n" if debt > 0 else "Outstanding Loan: None\n"
        
        return (
            "━━ My Account ━━\n"
            "Name: Mwila Tembo\n"
            "Phone: +260 97 000 0000\n"
            "Network: Airtel Zambia\n"
            f"Wallet Balance: ZMW {balance}\n"
            "━━━━━━━━━━━━━━━━\n"
            f"AI Credit Score: {score}/99\n"
            f"{debt_line}"
            "Airtime Usage: Normal\n"
            "Utility Payments: Consistent\n"
            "Savings Group: GRP-ZAM-001\n"
            "0. Back"
        )
    elif state == "MICRO_LENDING_START":
        return (
            "NdalamaLite Loans\n"
            "1. Apply for Loan\n"
            "0. Back"
        )
    elif state == "MICRO_LENDING_RESULT":
        eval_result = session["data"]["loan_eval"]
        debt = eval_result.get("current_debt_zm", 0)
        score = eval_result.get("score", 0)
        
        if eval_result["approved"]:
            base_text = (
                f"Score: {score}. Approved! Qualify for ZMW {eval_result['max_amount_zm']}.\n"
                f"Repay ZMW {eval_result['repayment_amount_zm']} in 30 days.\n"
                "1. Accept Loan\n"
            )
            if debt > 0:
                base_text += f"2. Repay Full Debt (ZMW {debt})\n"
                base_text += "3. Repay Partial Amount\n"
            base_text += "0. Main Menu"
            return base_text
        else:
            base_text = (
                f"Score: {score}. Declined.\n"
                f"{eval_result['reason']}\n"
            )
            if debt > 0:
                base_text += f"1. Repay Full Balance (ZMW {debt})\n"
                base_text += "2. Repay Partial Amount\n"
            base_text += "0. Main Menu"
            return base_text
    elif state == "LOAN_ACCEPTED":
        eval_result = session["data"].get("loan_eval", {})
        amt = eval_result.get("max_amount_zm", 0)
        return f"Transaction Complete.\n[NOTIFY] Success! ZMW {amt} has been deposited to your mobile money account."
    elif state == "LOAN_REPAID":
        amt = session["data"].get("repaid_amount", 50)
        eval_result = session["data"].get("loan_eval", {})
        debt = eval_result.get("current_debt_zm", amt)
        old_score = eval_result.get("score", 50)
        remaining = debt - amt
        
        # Calculate AI score boost based on repayment amount
        if debt > 0:
            boost = int((amt / debt) * 15) # Max +15 points for clearing debt
        else:
            boost = 5
            
        new_score = min(99, old_score + boost)
        session["data"]["updated_score"] = new_score
        
        if remaining > 0:
            return f"Thank you! A partial payment of ZMW {amt} was applied. Remaining balance: ZMW {remaining}.\nYour AI Credit Score improved to {new_score}.\n[NOTIFY] Payment Processed! ZMW {amt} paid. New AI Score: {new_score}."
        else:
            overpay = abs(remaining)
            extra_msg = f" (ZMW {overpay} saved to your wallet)" if overpay > 0 else ""
            return f"Thank you! Your debt has been repaid in full{extra_msg}.\nYour AI Credit Score improved significantly to {new_score}!\n[NOTIFY] Debt Cleared! ZMW {amt} paid. New AI Score: {new_score}."

    elif state == "PARTIAL_REPAYMENT_INPUT":
        eval_result = session["data"].get("loan_eval", {})
        debt = eval_result.get("current_debt_zm", 0)
        return (
            f"Enter amount to repay (Current debt: ZMW {debt}):\n"
            "0. Cancel"
        )
    elif state == "CILIMBA_GUARD_START":
        return (
            "CilimbaGuard AI Protection\n"
            "Your Active Group: GRP-ZAM-001\n"
            "1. Check Group Health & Payout Status\n"
            "0. Back"
        )
    elif state == "CILIMBA_GUARD_RESULT":
        eval_result = session["data"]["group_eval"]
        if eval_result["trigger_payout"]:
            return (
                f"ALERT: {eval_result['risk_level']} Risk Detected!\n"
                f"Reason: {eval_result['reason']}\n"
                f"Auto-payout of ZMW {eval_result['payout_amount_zm']} to group vault deployed.\n"
                "0. Main Menu"
                f"[NOTIFY] NdalamaLite Emergency Payout: ZMW {eval_result['payout_amount_zm']} deposited to Cilimba Group Vault due to {eval_result['risk_level']} Risk alert."
            )
        else:
            return (
                f"Status: Safe ({eval_result['risk_level']} Risk)\n"
                f"Remarks: {eval_result['reason']}\n"
                "Group is resilient.\n"
                "0. Main Menu"
            )
    elif state == "MARKET_MENU":
        return (
            "Market Data AI\n"
            "Enter item (e.g., Maize, Mint, Paprika):\n"
            "0. Back"
        )
    elif state == "MARKET_NOT_FOUND":
        return (
            "Item not found. Try typing it again (e.g., Maize, Mint):\n"
            "0. Back"
        )
    elif state == "MARKET_QUANTITY_INPUT":
        return (
            "Enter quantity in kg (Max 100):\n"
            "0. Back"
        )
    elif state == "MARKET_QUANTITY_TOO_HIGH":
        return (
            "Maximum capacity is 100kg.\n"
            "Please enter a smaller amount:\n"
            "0. Back"
        )
    elif state == "MARKET_RESULT":
        data = session["data"]["market_data"]
        return (
            f"[{data.get('data_source', 'Agent')}]\n"
            f"Fair Price: {data['commodity']} ({data['quantity_kg']}kg)\n"
            f"Lusaka: ZMW {data['lusaka_price']}\n"
            f"Transport Adjust: -ZMW {data['transport_cost']}\n"
            f"Do not accept less than ZMW {data['recommended_floor_price']} today.\n"
            "0. Main Menu"
        )
    elif state == "BANK_VERIFY_MENU":
        return (
            "Agent Bank Verification\n"
            "Please enter your 4-digit PIN:\n"
            "0. Back"
        )
    elif state == "BANK_ACTION_MENU":
        return (
            "Ndalama Anti-Fraud Shield\n"
            "Protect yourself from Fake SMS Scams.\n"
            "1. My Recent Transactions\n"
            "2. Verify Customer's Payment\n"
            "0. Main Menu"
        )
    elif state == "BANK_VERIFY_AMOUNT":
        return (
            "Did a customer show you an SMS receipt?\n"
            "Enter the deposit amount they claim (e.g. 800):\n"
            "0. Cancel"
        )
    elif state == "BANK_VERIFY_RESULT":
        res = session["data"]["verify_res"]
        if res["status"] == "VERIFIED":
            return f"VERIFIED: {res['message']}\n0. Main Menu"
        else:
            return f"{res['message']}\n0. Main Menu\n[NOTIFY] 🚨 SCAM ALERT DETECTED"
    elif state == "BANK_RECENT_TRANSACTIONS":
        txns = session["data"]["recent_txns"]
        output = "Recent Transactions:\n"
        for i, t in enumerate(txns):
            output += f"{i+1}. {t['date']} {t['type']} ZMW {t['amount']}\n"
        output += "0. Main Menu"
        return output
    else:
        return "Invalid menu state.\n0. Back"
