"""Unit tests validating Community Demo Policy safeguards for CareRing Health."""

import pytest
from fastapi.testclient import TestClient

from src.models import (
    DischargedPatientCase,
    MedicationAdherence,
    PatientDetails,
    PrescribedMedication,
    TriageStatus,
    mask_phone,
    validate_ascii_e164,
)
from src.calle_bridge import CalleBridge, CalleBridgeError
from src.triage_engine import CareRingTriageEngine
from src.server import app


def test_phone_masking():
    assert mask_phone("+919876543210") == "+91 •••• •••210"
    assert mask_phone("+14155552671") == "+14 •••• •••671"
    assert mask_phone(None) == "••••••••"
    assert mask_phone("") == "••••••••"


def test_validate_ascii_e164():
    # Valid ASCII E.164
    assert validate_ascii_e164("+919876543210") == "+919876543210"
    assert validate_ascii_e164("+14155552671") == "+14155552671"

    # Non-ASCII rejection
    with pytest.raises(ValueError, match="non-ASCII"):
        validate_ascii_e164("+91９８７６５４３２１０")

    # Invalid pattern
    with pytest.raises(ValueError, match="ASCII E.164"):
        validate_ascii_e164("9876543210")

    with pytest.raises(ValueError, match="ASCII E.164"):
        validate_ascii_e164("+123")

    # Synthetic default rejection in live mode
    with pytest.raises(ValueError, match="Synthetic default destination"):
        validate_ascii_e164("+15555550199", allow_synthetic=False)

    # Allowed in test/mock mode
    assert validate_ascii_e164("+15555550199", allow_synthetic=True) == "+15555550199"


def test_https_base_url_enforcement():
    # Approved HTTPS
    b = CalleBridge(base_url="https://api.heycall-e.com/v1")
    assert b.base_url == "https://api.heycall-e.com/v1"

    # Local development loopback allowed
    b_local = CalleBridge(base_url="http://127.0.0.1:8000")
    assert b_local.base_url == "http://127.0.0.1:8000"

    # Insecure plaintext remote HTTP rejected
    with pytest.raises(ValueError, match="approved HTTPS protocol"):
        CalleBridge(base_url="http://api.heycall-e.com/v1")


@pytest.mark.asyncio
async def test_pending_call_stops_at_call_pending():
    bridge = CalleBridge()
    engine = CareRingTriageEngine(bridge=bridge)
    case = DischargedPatientCase(
        patient=PatientDetails(
            patient_id="PAT-TEST-01",
            name="Rohan Mehra",
            phone="+919876543210",
            age=45,
            procedure_name="Appendectomy",
            primary_doctor="Dr. Gupta",
            clinic_name="City Hospital"
        ),
        medications=[PrescribedMedication(drug_name="Ibuprofen", dosage="400mg")]
    )
    engine.register_patient_case(case)

    # Execute pending call scenario
    res = await engine.run_followup_call("PAT-TEST-01", scenario="pending")

    assert res.triage_level == TriageStatus.CALL_PENDING
    assert res.medication_status == MedicationAdherence.PENDING_RESPONSE
    assert engine.triage_states["PAT-TEST-01"] == TriageStatus.CALL_PENDING
    # Ensure emergency nurse alert is NOT fabricated for pending status
    assert len(engine.nurse_alerts) == 0


def test_loopback_and_patient_masking_via_api():
    client = TestClient(app)
    # Loopback (testclient) should succeed without auth
    resp = client.get("/api/v1/patients")
    assert resp.status_code == 200
    patients = resp.json()
    assert len(patients) >= 3

    # Verify phone numbers are masked in API output
    for p in patients:
        assert "••••" in p["phone"]
        assert not p["phone"].startswith("+919876543210")


def test_dashboard_xss_protection():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    # Verify escapeHtml is defined
    assert "function escapeHtml" in html
    # Verify no inline onclicks for triage buttons
    assert 'onclick="triggerCall' not in html
    assert 'data-action="triage"' in html
