# NdalamaLite Changelog

All notable changes to the NdalamaLite project will be documented in this file. We will append all new changes or modifications here moving forward.

## [Unreleased]
### Added
- Created `CHANGELOG.md` to track all future and historical codebase changes.
- Added comprehensive project pitch and problem/solution definitions to `README.md`.
- Implemented iPhone-style native dialer UI components (bottom tab bar, bold dial numbers, sleek green dial button) in frontend.
- Added proportional debt repayment feature to the USSD flow so users can submit partial loan payments.
- Added real-time AI credit score updates directly into the USSD text overlay based on the percentage of debt repaid.
- Unified the backend and frontend onto a single port (`8000`) using FastAPI StaticFiles configuration to bypass strict local network firewall blocks.
- Open network ports (`8000`, `5000`) on the Windows Defender Firewall via PowerShell.
