# CareRing Health

> **Clinical Post-Discharge Triage & Patient Medication Adherence Voice Concierge powered by CALL-E**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Telephony: CALL--E](https://img.shields.io/badge/Telephony-CALL--E%20SDK-emerald.svg)](https://heycall-e.com)
[![Tests Passing](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg)]()

![CareRing Health Master Editorial Thumbnail](media/carering_thumbnail.png)

---

## The Problem: Preventable Readmissions & Post-Op Complications

According to healthcare clinical studies, nearly **20% of discharged surgical patients** experience an adverse event within 30 days of leaving the hospital:
1. **Missed Critical Medications:** Patients forget complex dosing schedules for vital therapies like blood thinners (antiplatelets/anticoagulants) or antibiotics.
2. **Ignored Early Warning Signs:** Patients dismiss severe warning indicators (shortness of breath, chest heaviness, sudden fever) until it turns into a life-threatening emergency.
3. **Severe Clinical Understaffing:** Hospitals and specialty outpatient clinics do not have the nursing bandwidth to place 150+ personalized follow-up calls every morning.

Traditional SMS reminders are passive and lack clinical diagnostic interaction, especially for elderly patients.

---

## The Solution: CareRing Health

**CareRing Health** connects hospital EHR discharge registries with autonomous outbound PSTN telephony powered by **CALL-E**:

- 🩺 **24-Hour Automated Follow-Up:** Autonomously dials discharged post-op patients over PSTN carrier networks without staff overhead.
- 💊 **Medication Adherence Gate (DTMF):** Verifies daily prescription intake via keypad confirmation (*"Did you take your prescribed blood thinner today? Press 1 for Yes, Press 2 for No"*).
- 🚨 **Autonomous Clinical Symptom Triage:** Rates surgical pain on a 1–5 scale and analyzes verbal symptoms.
- 🚑 **Emergency Nurse Escalation:** If pain >= 4 or dangerous symptoms (dyspnea, dizziness) are detected, immediately dispatches an urgent Red Alert to the on-call triage desk.
- 📅 **Follow-Up Appointment Confirmation:** Confirms scheduled post-operative clinic consultations via touchtone Key [1].
- 🔒 **HIPAA-Compliant SHA-256 Audit Trail:** Computes deterministic cryptographic hash chains across all clinical triage state transitions.
- 📊 **Real-Time Clinical Station Dashboard:** Dark-mode console for nursing staff displaying patient vitals, active red alerts, and adherence trends.

---

## Quickstart & Verification

### 1. Installation

```bash
git clone https://github.com/hackersclub111/carering-health.git
cd carering-health
pip install -r requirements.txt
```

### 2. Run Test Suite (100% Passing in <1s)

```bash
py -3.12 -B -m pytest tests/ -v
```

### 3. Run Zero-Cost Judge Evaluation CLI Demo

```bash
py -3.12 -B src/client.py --demo
```

### 4. Run Forensic Cryptographic Audit

```bash
py -3.12 -B src/client.py --verify-evidence
```

### 5. Launch Interactive Clinical Dashboard

```bash
py -3.12 -B src/client.py --serve
# Navigate to http://localhost:8002
```

---

## Architecture & CALL-E Contract

```
┌─────────────────────────┐
│ Hospital EHR / Clinic   │
│ Patient Discharge Event │
└────────────┬────────────┘
             │ Webhook POST /api/v1/patients
             ▼
┌─────────────────────────┐
│    CareRing Engine      │◄─── SHA-256 Cryptographic Audit Ledger
└────────────┬────────────┘
             │ Outbound PSTN Dial via HeyCall-E API
             ▼
┌─────────────────────────┐
│ CALL-E Telephony Agent  │
│ - Medication DTMF Check │
│ - Pain Scale (1-5)      │
│ - Dyspnea / Fever Triage│
│ - Clinic Visit Confirm  │
└────────────┬────────────┘
             │ Structured result_schema
             ▼
┌────────────────────────────────────────────────────────┐
│ Clinical Verdict:                                      │
│  [Normal]   -> NORMAL RECOVERY (Log to EHR)            │
│  [Missed]   -> MODERATE_FOLLOWUP (Alert Care Coordinator)
│  [Pain 4-5] -> CRITICAL_EMERGENCY_ESCALATION           │
│                (Immediate Red Alert to On-Call Nurse)  │
└────────────────────────────────────────────────────────┘
```

---

## Production Safeguards, High-Stakes Limits & Simulation Notice

In compliance with community and clinical evaluation standards, CareRing Health enforces clear architectural safeguards:

1. **Clinical Scoping & No Primary Diagnosis:** CareRing Health is an administrative and triage routing concierge, NOT a medical diagnostic device. It collects post-operative feedback (DTMF medication adherence, patient-reported numeric pain scores 1-5, presence of red-flag symptoms) and deterministically escalates out-of-range findings to registered clinical personnel.
2. **Deterministic Fallback & Never Fabricating Results:** If a telephony call is pending, queued, or disconnected before extraction completes, the system transitions to `CALL_PENDING` or `UNRESOLVED`. It never fabricates a completed checkup or false-negative clearance.
3. **HIPAA & Patient Privacy Controls:** In demonstration mode, patient telephone destinations are strictly validated against ASCII E.164 syntax while synthetic default numbers (`555-01xx`) are blocked from live carrier ingress. UI dashboards and telemetry payloads mask phone numbers (`+91 •••• •••896`) and enforce strict HTML escaping and DOM event delegation to eliminate stored XSS.
4. **Transport Security & Local Isolation:** Remote endpoints enforce Bearer authentication (`CARERING_API_KEY`), while local evaluation loops (`127.0.0.1`, `localhost`, `testclient`) are permitted for automated zero-cost judge replay. All remote telephony endpoints require approved HTTPS connections.
5. **Zero-Cost Offline Evaluation:** Offline tests (`--demo`, `--verify-evidence`, `pytest tests/`) run completely deterministically with zero live API calls or paid credit consumption.

---

## Devpost Submission Package
See [`docs/READY_TO_COPY_DEVPOST.md`](docs/READY_TO_COPY_DEVPOST.md) for the exact copy-paste form fields, video timestamps, and upstream PR details.
