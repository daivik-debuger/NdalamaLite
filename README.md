# NdalamaLite & CilimbaGuard AI Architecture

This document serves as the core context file for the NdalamaLite project. **AI Assistants: Read this first to quickly understand the architecture.**

## Project Overview
NdalamaLite provides AI-driven financial services (micro-lending and insurance payouts) to rural Zambians via a simulated USSD text interface. This bridges the digital divide for users without smartphones or 3G/4G connectivity.

## Tech Stack
*   **Backend:** Python 3, FastAPI, Uvicorn (Runs on Port 8000)
*   **Frontend:** HTML/CSS/JS (Vanilla), served via standard HTTP (Runs on Port 5000)
    *   Designed as a full-screen web app mimicking the native iOS 18 Phone dialer.

## Directory Structure
*   `backend/main.py`: The FastAPI server. Exposes the `/ussd` POST endpoint. Handles translating text into USSD `CON` (continue) and `END` (end) protocols. Parses `[NOTIFY]` tags into structured JSON.
*   `backend/ussd_flow.py`: The state machine. Manages menu routing (e.g., `MAIN_MENU` -> `MICRO_LENDING_START`), parses user inputs, tracks session data, and holds all the plain text strings.
*   `backend/ai_engines.py`: The artificial intelligence simulation layer. 
    *   `NdalamaMicroLending`: Simulates alternative credit scoring. Approves loans, tracks existing debt, and calculates repayment interest.
    *   `CilimbaGuard`: Simulates risk resilience scoring for savings groups. Triggers emergency auto-payouts if risks (like drought) are too high.
*   `frontend/index.html` & `style.css`: The iOS dialer UI wrapper. Includes the dialpad, USSD gray modal, and the custom iOS-style push notification banner (`#ios-banner`).
*   `frontend/app.js`: The frontend client. Sends text input to the backend, manages the USSD DOM overlay, and drops down the push notification banner if the backend returns `data.notification`.

## Key Mechanisms
1.  **USSD Requests**: Dialing `888` on the frontend starts the USSD session loop with the backend.
2.  **Repayment Flow**: The backend dynamically detects outstanding debt; if the user's `current_debt_zm > 0`, the flow provides a dedicated option to instantly repay it from the menu.
3.  **Mobile Money Notifications**: 
    *   If `ussd_flow.py` appends a `[NOTIFY]` tag to a terminal state (e.g. `[NOTIFY] Success! ZMW 400 deposited`), `main.py` extracts it and sends it via JSON.
    *   `app.js` catches it and triggers the animated iOS push notification at the top of the user's screen. Used for Loan deposits, Repayment confirmations, and CilimbaGuard insurance payouts. 

*Note: Whenever structural or logical features are changed in the codebase, update this document to maintain architectural clarity.*

## The Problem: What Zambia Doesn't Have & How NdalamaLite Solves It

NdalamaLite & CilimbaGuard AI fills that void. While companies like MTN Money and Lupiya have made great strides, they haven't solved everything. Here are the three massive things Zambia still lacks, and exactly how your app solves them:

### 1. The Gap: True Access for the "Hardware Poor"
*   **What Zambia Doesn't Have:** Universal smartphone ownership and reliable 4G/5G internet in rural areas. Many current fintech apps require expensive phones, data plans, and app stores. If a farmer only has a $10 feature phone and 2G cell service, a fancy AI app is completely useless to them.
*   **How Your App Helps:** NdalamaLite bridges the "hardware divide." By putting advanced AI behind a simple USSD text menu (`*888#`), you are bringing state-of-the-art fintech to the most basic phones on the market. You are providing top-tier financial access without forcing the user to upgrade their hardware or buy expensive data.

### 2. The Gap: Formal Credit Histories for SMEs
*   **What Zambia Doesn't Have:** Traditional credit scores (like the FICO scores used in the US). Millions of hardworking Zambians—market traders, small farmers, and street vendors—handle cash and mobile money every day, but because they don't use traditional banks, they are "credit invisible." They cannot get small business (SME) loans to grow.
*   **How Your App Helps:** Your prototype uses an Alternative AI Credit-Scoring Engine. Instead of looking for a bank statement, your AI analyzes the data they do generate: how consistently they buy phone airtime, pay utility bills via mobile money, or receive funds. It instantly turns that alternative data into a "trust score," allowing a previously unbanked business owner to get a micro-loan in five seconds.

### 3. The Gap: A Digital Safety Net for Cultural Systems
*   **What Zambia Doesn't Have:** Formal insurance for traditional savings methods. Many Zambians rely on Chilimba (informal group savings circles where people pool money). The massive flaw is that if one person suffers a local emergency (like a localized drought or illness) and cannot pay their share, the entire circle collapses, hurting the whole community.
*   **How Your App Helps:** This is where CilimbaGuard AI is revolutionary. It doesn't try to replace Zambian culture; it protects it. By using predictive AI to monitor environmental and economic risks in a specific area, your system can automatically trigger a "micro-insurance" payout to cover a struggling member's share. It keeps the community savings circle intact during a crisis.

### The Cheat Sheet for the Judges
| What is Missing in Zambia | How NdalamaLite & CilimbaGuard Fixes It |
| :--- | :--- |
| Apps that work on "brick" phones | USSD interface runs on any phone, no internet required. |
| Ways to score unbanked people | AI analysis of mobile airtime and payment history. |
| Protection for group savings | Predictive micro-insurance triggers before the group fails. |
