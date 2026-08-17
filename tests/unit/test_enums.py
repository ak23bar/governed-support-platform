import pytest

from gps.domain.enums import DispatchMode, EvidenceCoverage, ResolutionType, RunStatus


@pytest.mark.parametrize(
    ("enum_type", "unknown"),
    [
        (ResolutionType, "GUESS"),
        (DispatchMode, "BEST_EFFORT"),
        (EvidenceCoverage, "MOSTLY"),
        (RunStatus, "RETRYING"),
    ],
)
def test_unknown_domain_enum_values_fail_closed(
    enum_type: type[ResolutionType] | type[DispatchMode] | type[EvidenceCoverage] | type[RunStatus],
    unknown: str,
) -> None:
    with pytest.raises(ValueError):
        enum_type(unknown)
