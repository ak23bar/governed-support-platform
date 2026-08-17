import pytest

from gps.domain.enums import (
    CanonicalBlockType,
    CorpusPublicationStatus,
    DispatchMode,
    EvidenceCoverage,
    ResolutionType,
    RunStatus,
    SourceDocumentStatus,
    StrictEnum,
)


@pytest.mark.parametrize(
    ("enum_type", "unknown"),
    [
        (ResolutionType, "GUESS"),
        (DispatchMode, "BEST_EFFORT"),
        (EvidenceCoverage, "MOSTLY"),
        (RunStatus, "RETRYING"),
        (SourceDocumentStatus, "PUBLISHED"),
        (CanonicalBlockType, "freeform"),
        (CorpusPublicationStatus, "ACTIVE"),
    ],
)
def test_unknown_domain_enum_values_fail_closed(
    enum_type: type[StrictEnum],
    unknown: str,
) -> None:
    with pytest.raises(ValueError):
        enum_type(unknown)
