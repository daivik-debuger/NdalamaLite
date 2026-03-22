import random

class NdalamaMicroLending:
    @staticmethod
    def evaluate_credit(phone_number: str) -> dict:
        """
        Mocks a credit evaluation based on simulated user history.
        Evaluates based on airtime and utility consistency.
        """
        # Simulated logic
        score = random.randint(30, 95)
        approved = score >= 50
        current_debt = random.choice([0, 10, 20, 50])
        max_amount = (score - 30) * 10 if approved else 0
        
        if approved:
            reason = "Consistent utility payments & airtime use."
            repayment_amount = int(max_amount * 1.15) # 15% interest
        else:
            reason = f"Your NdalamaLite score is too low."
            if current_debt > 0:
                reason += f" Please repay your ZMW {current_debt} balance."
            repayment_amount = 0
        
        return {
            "score": score,
            "approved": approved,
            "max_amount_zm": max_amount,
            "repayment_amount_zm": repayment_amount,
            "current_debt_zm": current_debt,
            "reason": reason
        }

class CilimbaGuard:
    @staticmethod
    def evaluate_group_resilience(group_id: str) -> dict:
        """
        Assesses group stability for traditional savings circles.
        If environmental or economic markers predict involuntary default,
        triggers a micro-insurance payout.
        """
        # Simulated risk levels based on mock environmental markers (e.g., drought, inflation)
        risk_level = random.choice(["Low", "Medium", "High", "Critical"])
        trigger_payout = risk_level in ["High", "Critical"]
        
        # Micro-insurance payout amount to the group vault
        payout_amount = random.randint(500, 2000) if trigger_payout else 0
        
        reason = "Drought indicators detected in region." if trigger_payout else "Group indicators stable."
        
        return {
            "group_id": group_id,
            "risk_level": risk_level,
            "trigger_payout": trigger_payout,
            "payout_amount_zm": payout_amount,
            "reason": reason
        }
