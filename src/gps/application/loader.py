from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from gps.domain.contracts import CompatibilityTuple
from gps.domain.enums import RouteType


class ApplicationPackageError(ValueError):
    pass


class FrozenDeclaration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ApplicationManifest(FrozenDeclaration):
    schema_version: str = Field(min_length=1)
    application_id: str = Field(min_length=1)
    package_version: str = Field(min_length=1)
    name: str = Field(min_length=1)
    required_runtime: str = Field(min_length=1)
    workflow_version: str = Field(min_length=1)
    corpus_version: str = Field(min_length=1)
    policy_version: str = Field(min_length=1)
    model_profile_version: str = Field(min_length=1)
    adapter_versions: tuple[str, ...] = Field(min_length=1)


class AutonomyConfig(FrozenDeclaration):
    schema_version: str = Field(min_length=1)
    requested_capabilities: tuple[str, ...]
    automatic_dispatch_enabled: bool = False


class KnowledgeConfig(FrozenDeclaration):
    schema_version: str = Field(min_length=1)
    sources: tuple[str, ...]
    status: Literal["fixture_only", "unpublished", "approved"]


class TerminologyEntry(FrozenDeclaration):
    term: str = Field(min_length=1)
    aliases: tuple[str, ...] = ()


class TaxonomyConfig(FrozenDeclaration):
    schema_version: str = Field(min_length=1)
    products: tuple[str, ...] = Field(min_length=1)
    categories: tuple[str, ...]
    terminology: tuple[TerminologyEntry, ...] = ()


class QueueDeclaration(FrozenDeclaration):
    queue_id: str = Field(min_length=1)
    route_type: RouteType
    product: str | None = None
    function: str | None = None


class RoutingConfig(FrozenDeclaration):
    schema_version: str = Field(min_length=1)
    default_route: RouteType
    queues: tuple[QueueDeclaration, ...]


class TemplateConfig(FrozenDeclaration):
    schema_version: str = Field(min_length=1)
    template_refs: tuple[str, ...]
    branding_refs: tuple[str, ...]


class ProviderProfiles(FrozenDeclaration):
    model: str = Field(min_length=1)
    embedding: str = Field(min_length=1)
    knowledge_source: str = Field(min_length=1)


class ProviderConfig(FrozenDeclaration):
    schema_version: str = Field(min_length=1)
    profiles: ProviderProfiles


class EvaluationConfig(FrozenDeclaration):
    schema_version: str = Field(min_length=1)
    dataset_refs: tuple[str, ...]
    case_refs: tuple[str, ...]


class ApplicationPackage(FrozenDeclaration):
    manifest: ApplicationManifest
    autonomy: AutonomyConfig
    knowledge: KnowledgeConfig
    taxonomy: TaxonomyConfig
    routing: RoutingConfig
    templates: TemplateConfig
    providers: ProviderConfig
    evaluations: EvaluationConfig
    compatibility: CompatibilityTuple


_DECLARATION_MODELS = {
    "knowledge": KnowledgeConfig,
    "taxonomy": TaxonomyConfig,
    "routing": RoutingConfig,
    "templates": TemplateConfig,
    "providers": ProviderConfig,
    "evaluations": EvaluationConfig,
}
_FORBIDDEN_KEYS = {
    "credential",
    "credentials",
    "password",
    "secret",
    "api_key",
    "access_token",
    "private_key",
    "sdk",
    "executable",
    "workflow_code",
    "policy_bypass",
}
_POLICY_FLOOR_CAPABILITIES = frozenset({"knowledge.sync", "case.read", "case.route", "review.propose"})


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ApplicationPackageError(f"cannot load {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise ApplicationPackageError(f"{path.name} must contain a mapping")
    return cast(dict[str, Any], value)


def _reject_forbidden(value: Any, location: str = "package") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            if normalized in _FORBIDDEN_KEYS:
                raise ApplicationPackageError(f"forbidden application-package key at {location}.{key}")
            _reject_forbidden(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden(child, f"{location}[{index}]")


def load_application_package(path: Path) -> ApplicationPackage:
    raw_manifest = _load_yaml(path / "manifest.yaml")
    raw_autonomy = _load_yaml(path / "autonomy.yaml")
    declarations = {name: _load_yaml(path / f"{name}.yaml") for name in _DECLARATION_MODELS}
    _reject_forbidden({"manifest": raw_manifest, "autonomy": raw_autonomy, **declarations})
    try:
        manifest = ApplicationManifest.model_validate(raw_manifest)
        autonomy = AutonomyConfig.model_validate(raw_autonomy)
        knowledge = KnowledgeConfig.model_validate(declarations["knowledge"])
        taxonomy = TaxonomyConfig.model_validate(declarations["taxonomy"])
        routing = RoutingConfig.model_validate(declarations["routing"])
        templates = TemplateConfig.model_validate(declarations["templates"])
        providers = ProviderConfig.model_validate(declarations["providers"])
        evaluations = EvaluationConfig.model_validate(declarations["evaluations"])
    except ValidationError as exc:
        raise ApplicationPackageError(str(exc)) from exc
    denied = set(autonomy.requested_capabilities) - _POLICY_FLOOR_CAPABILITIES
    if denied:
        raise ApplicationPackageError(f"application requests capabilities outside policy floor: {sorted(denied)}")
    if autonomy.automatic_dispatch_enabled:
        raise ApplicationPackageError("E01 policy floor prohibits automatic dispatch")
    compatibility = CompatibilityTuple(
        runtime_version=manifest.required_runtime,
        application_package_version=manifest.package_version,
        workflow_version=manifest.workflow_version,
        corpus_version=manifest.corpus_version,
        policy_version=manifest.policy_version,
        model_profile_version=manifest.model_profile_version,
        adapter_versions=manifest.adapter_versions,
    )
    return ApplicationPackage(
        manifest=manifest,
        autonomy=autonomy,
        knowledge=knowledge,
        taxonomy=taxonomy,
        routing=routing,
        templates=templates,
        providers=providers,
        evaluations=evaluations,
        compatibility=compatibility,
    )
