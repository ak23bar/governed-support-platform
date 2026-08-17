import pytest
from pydantic import ValidationError

from gps.providers.protocols import ProviderReceipt


def test_transport_specific_or_secret_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        ProviderReceipt(
            request_id="r",
            status="ACCEPTED",
            redacted_details={},
            google_response={},
        )  # type: ignore[call-arg]


def test_receipt_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        ProviderReceipt(request_id="r", status="maybe", redacted_details={})  # type: ignore[arg-type]
