import inspect
import re
from pathlib import Path

import gps.domain.contracts as domain_contracts
import gps.domain.enums as domain_enums
from gps.domain.base import ContextualContract, Contract, RunContextContract
from gps.domain.enums import StrictEnum


def test_typescript_declarations_cover_e01_python_contract_and_enum_names() -> None:
    declaration_path = Path(__file__).resolve().parents[2] / "schemas/typescript/gps-domain-v1.d.ts"
    declaration = declaration_path.read_text(encoding="utf-8")

    python_contracts = {
        name
        for name, value in vars(domain_contracts).items()
        if inspect.isclass(value) and issubclass(value, Contract) and value.__module__ == domain_contracts.__name__
    }
    python_enums = {
        name
        for name, value in vars(domain_enums).items()
        if inspect.isclass(value)
        and value is not StrictEnum
        and issubclass(value, StrictEnum)
        and value.__module__ == domain_enums.__name__
    }
    declared_interfaces = set(re.findall(r"^export interface (\w+)", declaration, flags=re.MULTILINE))
    declared_types = set(re.findall(r"^export type (\w+)", declaration, flags=re.MULTILINE))

    assert "DERIVED from the E01 Python/Pydantic domain contracts" in declaration
    assert python_contracts <= declared_interfaces
    assert python_enums <= declared_types

    base_interfaces = {
        "VersionedContract": (Contract, None),
        "ContextualDomainContract": (ContextualContract, Contract),
        "RunContextDomainContract": (RunContextContract, ContextualContract),
    }
    for interface_name, (model, parent) in base_interfaces.items():
        expected_fields = set(model.model_fields)
        if parent is not None:
            expected_fields -= set(parent.model_fields)
        assert _typescript_interface_fields(declaration, interface_name) == expected_fields

    for contract_name in python_contracts:
        model = getattr(domain_contracts, contract_name)
        parent = (
            RunContextContract
            if issubclass(model, RunContextContract)
            else ContextualContract
            if issubclass(model, ContextualContract)
            else Contract
        )
        expected_fields = set(model.model_fields) - set(parent.model_fields)
        assert _typescript_interface_fields(declaration, contract_name) == expected_fields

    for enum_name in python_enums:
        enum_type = getattr(domain_enums, enum_name)
        match = re.search(rf"^export type {enum_name} =(?P<body>.*?);", declaration, flags=re.MULTILINE | re.DOTALL)
        assert match is not None
        assert set(re.findall(r'"([^"]+)"', match.group("body"))) == {member.value for member in enum_type}


def _typescript_interface_fields(declaration: str, interface_name: str) -> set[str]:
    match = re.search(
        rf"^export interface {interface_name}(?: extends \w+)? \{{(?P<body>.*?)^\}}",
        declaration,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None
    return set(re.findall(r"^\s+readonly (\w+):", match.group("body"), flags=re.MULTILINE))
