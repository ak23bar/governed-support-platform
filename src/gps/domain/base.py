from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class Contract(BaseModel):
    """Strict, immutable and versioned boundary object."""

    model_config = ConfigDict(extra="forbid", frozen=True, use_enum_values=False)
    schema_version: str = Field(default="1.0", min_length=1)
    contract_name: ClassVar[str]


class ContextualContract(Contract):
    tenant_id: str = Field(min_length=1)
    application_id: str = Field(min_length=1)


class RunContextContract(ContextualContract):
    case_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)


class JsonPayload(Contract):
    values: dict[str, Any] = Field(default_factory=dict)

    @field_validator("values")
    @classmethod
    def prohibit_obvious_secret_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        forbidden = {"password", "secret", "api_key", "access_token", "private_key"}
        found = forbidden.intersection(key.lower() for key in value)
        if found:
            raise ValueError(f"secret-bearing keys are prohibited: {sorted(found)}")
        return value
