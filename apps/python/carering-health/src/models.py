"""Data models and clinical triage schemas for CareRing Health."""

from enum import Enum
import hashlib
import re
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


def mask_phone(phone: Optional[str]) -> str:
    """Mask phone number for patient HIPAA privacy while preserving prefix/suffix for inspection."""
    if not phone:
        return "••••••••"
    clean = phone.strip()
    if clean.startswith("+") and len(clean) >= 10:
        return f"{clean[:3]} •••• •••{clean[-3:]}"
    if len(clean) >= 8:
        return f"•••• •••{clean[-3:]}"
    return "••••••••"


def validate_ascii_e164(phone: str, allow_synthetic: bool = False) -> str:
    """Strictly validate ASCII E.164 destination numbers and reject synthetic defaults in live mode."""
    if not phone or not isinstance(phone, str):
        raise ValueError("Phone destination must be a non-empty string.")
    
    # ASCII printable check
    if not phone.isascii():
        raise ValueError(f"Phone destination '{phone}' contains non-ASCII characters.")
    
    # E.164 pattern: + followed by 7 to 15 digits
    e164_pattern = r"^\+[1-9]\d{6,14}$"
    if not re.match(e164_pattern, phone):
        raise ValueError(
            f"Phone destination '{phone}' must adhere to valid ASCII E.164 format (e.g., +919876543210 or +14155552671)."
        )
    
    # Synthetic default numbers (e.g. 555-01xx) must be rejected for live PSTN routing
    if not allow_synthetic:
        synthetic_patterns = [
            r"^\+155555501\d{2}$",
            r"^\+180055501\d{2}$",
            r"^\+910000000000$",
            r"^\+11234567890$"
        ]
        for pat in synthetic_patterns:
            if re.match(pat, phone):
                raise ValueError(
                    f"Synthetic default destination '{phone}' is disallowed for live PSTN telephony."
                )
    
    return phone


class TriageStatus(str, Enum):
    NORMAL = "NORMAL"
    MODERATE_FOLLOWUP = "MODERATE_FOLLOWUP"
    CRITICAL_EMERGENCY_ESCALATION = "CRITICAL_EMERGENCY_ESCALATION"
    CALL_PENDING = "CALL_PENDING"
    UNRESOLVED = "UNRESOLVED"


class MedicationAdherence(str, Enum):
    TAKEN = "TAKEN"
    MISSED = "MISSED"
    SIDE_EFFECTS = "SIDE_EFFECTS"
    PENDING_RESPONSE = "PENDING_RESPONSE"


class PatientDetails(BaseModel):
    patient_id: str = Field(..., description="EHR Medical Record Number (MRN), e.g. PAT-4081")
    name: str = Field(..., description="Patient full name")
    phone: str = Field(..., description="Patient phone number")
    age: int
    procedure_name: str = Field(..., description="Recent surgical or medical procedure")
    primary_doctor: str = Field("Dr. Aditi Joshi, MD")
    clinic_name: str = Field("Apollo Cardiology Specialty Center")

    @property
    def phone_masked(self) -> str:
        return mask_phone(self.phone)


class PrescribedMedication(BaseModel):
    drug_name: str
    dosage: str
    frequency: str = "Once daily morning"


class DischargedPatientCase(BaseModel):
    patient: PatientDetails
    medications: List[PrescribedMedication]
    followup_appointment: str = "Friday at 10:30 AM"
    discharge_date: str = "2026-09-12"
    created_at: float = Field(default_factory=time.time)


class CalleClinicalResult(BaseModel):
    """Structured clinical extraction returned by CALL-E agent via result_schema."""
    task_id: str = Field(..., description="CALL-E unique task identifier")
    patient_id: str
    medication_status: MedicationAdherence
    pain_score: int = Field(..., ge=1, le=5, description="Self-reported pain score (1-5)")
    symptoms_reported: Optional[str] = Field(None, description="Patient verbal description of symptoms")
    appointment_confirmed: bool = Field(True, description="Whether upcoming appointment was confirmed")
    triage_level: TriageStatus
    escalate_to_nurse: bool = Field(False, description="Whether immediate human nurse escalation is required")
    call_confidence: float = Field(0.96, ge=0.0, le=1.0)
    call_duration_seconds: float = Field(38.2)
    cost_credits_settled: int = Field(26)


class ClinicalAuditRecord(BaseModel):
    """Forensic HIPAA-compliant audit record with SHA-256 hash chaining."""
    patient_id: str
    previous_triage: str
    new_triage: str
    timestamp: float = Field(default_factory=time.time)
    escalated: bool
    summary: str
    audit_hash: str = ""

    def calculate_hash(self, prev_hash: str = "0" * 64) -> str:
        payload = f"{prev_hash}|{self.patient_id}|{self.previous_triage}|{self.new_triage}|{self.timestamp}|{self.escalated}"
        self.audit_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return self.audit_hash
