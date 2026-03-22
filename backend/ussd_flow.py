from pydantic import BaseModel
from typing import Dict, Any
from ai_engines import NdalamaMicroLending, CilimbaGuard

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
            amount = int(text)
            if 0 < amount <= debt:
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
            
    # Default fallback
    return "MAIN_MENU"

def get_menu_text(state: str, session: dict) -> str:
    if state == "MAIN_MENU":
        return (
            "Welcome to NdalamaLite\n"
            "1. Get a Loan\n"
            "2. Savings Group Health\n"
            "3. My Account\n"
        )
    elif state == "ACCOUNT_INFO":
        eval_result = session["data"].get("loan_eval")
        if eval_result:
            score = session["data"].get("updated_score", eval_result["score"])
        else:
            # Generate a mock baseline if they haven't applied yet
            score = 50
            
        return (
            "My Account\n"
            f"AI Credit Score: {score}\n"
            "Airtime usage: Normal\n"
            "Utility pmts: Consistent\n"
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
            return f"Thank you! Your debt of ZMW {amt} has been repaid in full.\nYour AI Credit Score improved significantly to {new_score}!\n[NOTIFY] Debt Cleared! ZMW {amt} paid. New AI Score: {new_score}."

    elif state == "PARTIAL_REPAYMENT_INPUT":
        eval_result = session["data"].get("loan_eval", {})
        debt = eval_result.get("current_debt_zm", 0)
        return (
            f"Enter amount to repay (Max ZMW {debt}):\n"
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
    else:
        return "Invalid menu state.\n0. Back"
