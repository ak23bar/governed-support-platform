import shutil
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from gps.application import ApplicationPackageError, load_application_package
from gps.domain.contracts import EnvironmentConfig


def test_mohid_package_hydrates_immutable_compatibility(repository_root) -> None:
    package = load_application_package(repository_root / "applications" / "mohid-support")
    assert package.manifest.application_id == "mohid-support"
    assert package.compatibility.application_package_version == "mohid-support-0.1.0"
    with pytest.raises(ValidationError):
        package.compatibility.runtime_version = "changed"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        package.taxonomy.products += ("KIOSK",)  # type: ignore[misc]
    with pytest.raises(TypeError):
        package.routing.queues[0] = package.routing.queues[0]  # type: ignore[index]


def test_application_policy_floor_negative_fixture(repository_root, tmp_path) -> None:
    source = repository_root / "applications" / "mohid-support"
    candidate = tmp_path / "mohid-support"
    shutil.copytree(source, candidate)
    fixture = repository_root / "tests" / "fixtures" / "application" / "policy-floor-violation.yaml"
    shutil.copy(fixture, candidate / "autonomy.yaml")
    with pytest.raises(ApplicationPackageError, match="outside policy floor"):
        load_application_package(candidate)


@pytest.mark.parametrize(
    ("filename", "field", "value"),
    [
        ("knowledge.yaml", "unexpected", True),
        ("routing.yaml", "queues", [{"queue_id": "q"}]),
        ("providers.yaml", "profiles", {"model": "fake", "embedding": "fake"}),
    ],
)
def test_malformed_or_unknown_declaration_fails_closed(
    repository_root: Path, tmp_path: Path, filename: str, field: str, value: object
) -> None:
    candidate = tmp_path / "mohid-support"
    shutil.copytree(repository_root / "applications" / "mohid-support", candidate)
    target = candidate / filename
    data = yaml.safe_load(target.read_text())
    data[field] = value
    target.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ApplicationPackageError):
        load_application_package(candidate)


@pytest.mark.parametrize("forbidden", ["credentials", "api_key", "workflow_code", "executable"])
def test_forbidden_credential_or_executable_field_fails_closed(
    repository_root: Path, tmp_path: Path, forbidden: str
) -> None:
    candidate = tmp_path / "mohid-support"
    shutil.copytree(repository_root / "applications" / "mohid-support", candidate)
    target = candidate / "providers.yaml"
    data = yaml.safe_load(target.read_text())
    data[forbidden] = "forbidden"
    target.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ApplicationPackageError, match="forbidden"):
        load_application_package(candidate)


def test_local_environment_configuration_is_typed_and_fail_closed(repository_root: Path) -> None:
    raw = yaml.safe_load((repository_root / "infra" / "environments" / "local.yaml").read_text())
    environment = EnvironmentConfig.model_validate(raw)
    assert environment.environment.value == "local"
    with pytest.raises(ValidationError):
        EnvironmentConfig.model_validate({**raw, "external_side_effects_enabled": True})
    with pytest.raises(ValidationError):
        EnvironmentConfig.model_validate({**raw, "credentials": {"token": "x"}})
