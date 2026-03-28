import random
import re

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

class DataGatheringAgent:
    @staticmethod
    def get_lusaka_price_from_web(commodity: str):
        """Uses an AI web agent to search for current commodity prices."""
        if not DDGS:
            return None
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{commodity} price per kg in Lusaka Zambia ZMW", max_results=3))
                if not results:
                    return None
                for res in results:
                    text = res.get('body', "")
                    # Extract ZMW amounts if possible
                    matches = re.findall(r'(?:ZMW|K)\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
                    if matches:
                        return float(matches[0])
                    if "price" in text.lower():
                        nums = re.findall(r'\b(\d{2,3}(?:\.\d{1,2})?)\b', text)
                        if nums:
                            return float(nums[0])
            return None
        except Exception:
            return None

class BankVerificationAgent:
    @staticmethod
    def verify_transaction(transaction_id: str, amount: float) -> dict:
        """
        Simulates an agent that goes to the bank API and checks if money was received.
        Returns a dict with verification details.
        """
        # Demo predictive logic: Anything >= 500 triggers the Fraud Shield
        is_verified = amount < 500
        
        if is_verified:
            return {
                "status": "VERIFIED",
                "message": f"✅ SAFE: The bank confirms ZMW {amount} is securely in your account. The customer's SMS is REAL. You may release the goods.",
                "timestamp": "Just now"
            }
        else:
            return {
                "status": "UNVERIFIED",
                "message": f"🚨 SCAM PREVENTED: The bank has NO record of ZMW {amount}. The customer's SMS receipt is FAKE. Do NOT hand over your goods!",
                "timestamp": "Just now"
            }
            
    @staticmethod
    def get_recent_transactions(pin: str) -> list:
        """
        Simulates retrieving recent transactions after PIN verification.
        """
        types = ["DEPOSIT", "WITHDRAWAL", "PAYMENT"]
        txns = []
        for _ in range(3):
            txns.append({
                "type": random.choice(types),
                "amount": random.randint(50, 1000),
                "date": f"Mar {random.randint(10,22)}",
                "status": "COMPLETED"
            })
        return txns



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

class MarketAnalyzer:
    # Base realistic price ranges per kg in ZMW 
    PRICE_DB_PER_KG = {
        # Staples
        "maize": {"lusaka_price": 8.0, "transport_cost": 1.0},
        "soya": {"lusaka_price": 16.0, "transport_cost": 1.5},
        "groundnuts": {"lusaka_price": 18.0, "transport_cost": 1.6},
        "sunflower": {"lusaka_price": 12.0, "transport_cost": 1.2},
        # Fruits
        "mangoes": {"lusaka_price": 10.0, "transport_cost": 2.0},
        "bananas": {"lusaka_price": 15.0, "transport_cost": 3.0},
        # Herbs
        "mint": {"lusaka_price": 40.0, "transport_cost": 5.0},
        "basil": {"lusaka_price": 45.0, "transport_cost": 5.0},
        # Spices
        "paprika": {"lusaka_price": 120.0, "transport_cost": 10.0},
        "pepper": {"lusaka_price": 150.0, "transport_cost": 12.0},
        # Seeds
        "pumpkin seeds": {"lusaka_price": 50.0, "transport_cost": 4.0},
        "chia seeds": {"lusaka_price": 80.0, "transport_cost": 6.0}
    }

    @classmethod
    def is_valid_commodity(cls, commodity: str) -> bool:
        return commodity.lower().strip() in cls.PRICE_DB_PER_KG

    @classmethod
    def get_market_data(cls, commodity: str, quantity_kg: float = 50.0) -> dict:
        """
        Simulates real-time commodity data analysis.
        Provides Lusaka price and a recommended floor price based on quantity.
        """
        commodity_key = commodity.lower().strip()
        data = cls.PRICE_DB_PER_KG.get(commodity_key)
        
        # Agent goes to gather info on the web
        web_price = DataGatheringAgent.get_lusaka_price_from_web(commodity)
        
        if web_price is not None:
            base_lusaka_price = web_price
            base_transport_cost = 2.0 # Default fallback transport cost
            source = "AI Web Search Agent"
        elif data:
            base_lusaka_price = data["lusaka_price"]
            base_transport_cost = data["transport_cost"]
            source = "Offline DB Analyst"
        else:
            # Random fallback per kg if commodity not in DB
            base_lusaka_price = random.randint(5, 50)
            base_transport_cost = random.randint(1, 10)
            source = "Offline DB Analyst (Estimated)"
            
        lusaka_price = base_lusaka_price * quantity_kg
        transport_cost = base_transport_cost * quantity_kg
        floor_price = lusaka_price - transport_cost
        
        return {
            "commodity": commodity.capitalize(),
            "quantity_kg": quantity_kg,
            "lusaka_price": round(lusaka_price, 2),
            "transport_cost": round(transport_cost, 2),
            "recommended_floor_price": round(floor_price, 2),
            "data_source": source
        }
