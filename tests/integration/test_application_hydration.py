from gps.application import load_application_package


def test_application_package_hydrates_without_credentials(repository_root) -> None:
    package = load_application_package(repository_root / "applications" / "mohid-support")
    serialized = package.model_dump_json().lower()
    assert "password" not in serialized
    assert "api_key" not in serialized
    assert package.autonomy.automatic_dispatch_enabled is False
