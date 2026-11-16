"""Contract tests verifying OpenAPI specification conformance against profile-api.yaml."""

import os
import yaml
from src.main import app

CONTRACT_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../specs/001-user-profile/contracts/profile-api.yaml",
)


def _load_contract() -> dict:
    """Load and parse the OpenAPI YAML specification."""
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_contract_file_exists_and_is_valid():
    """Verify that the contract specification YAML exists and is well-formed."""
    contract = _load_contract()
    assert contract["openapi"].startswith("3.0")
    assert "paths" in contract
    assert "components" in contract


def test_app_implements_all_contract_paths():
    """Verify all paths in OpenAPI contract are implemented in the live FastAPI app."""
    contract = _load_contract()
    openapi_schema = app.openapi()
    live_paths = openapi_schema["paths"]

    for path, methods in contract["paths"].items():
        if path == "/media/avatars/{filename}":
            # Mounted via StaticFiles at /media/avatars
            continue

        assert path in live_paths, f"Contract path '{path}' is not registered in FastAPI app"

        for method in methods:
            if method.lower() in ("get", "put", "post", "delete"):
                assert (
                    method.lower() in live_paths[path]
                ), f"Method '{method.upper()}' for '{path}' is missing in live app"


def test_profile_response_schema_conformance():
    """Verify that ProfileResponse schema contains all required contract fields."""
    contract = _load_contract()
    contract_fields = set(
        contract["components"]["schemas"]["ProfileResponse"]["properties"].keys()
    )

    openapi_schema = app.openapi()
    live_schemas = openapi_schema["components"]["schemas"]
    assert "ProfileResponse" in live_schemas

    live_fields = set(live_schemas["ProfileResponse"]["properties"].keys())

    # Every contract property must exist in live schema (camelCase)
    for field in contract_fields:
        assert field in live_fields, f"Missing property '{field}' in ProfileResponse"


def test_public_profile_response_schema_conformance():
    """Verify that PublicProfileResponse schema matches contract."""
    contract = _load_contract()
    contract_fields = set(
        contract["components"]["schemas"]["PublicProfileResponse"]["properties"].keys()
    )

    openapi_schema = app.openapi()
    live_schemas = openapi_schema["components"]["schemas"]
    assert "PublicProfileResponse" in live_schemas

    live_fields = set(live_schemas["PublicProfileResponse"]["properties"].keys())
    for field in contract_fields:
        assert field in live_fields, f"Missing property '{field}' in PublicProfileResponse"


def test_avatar_upload_response_schema_conformance():
    """Verify that AvatarUploadResponse schema matches contract."""
    contract = _load_contract()
    contract_fields = set(
        contract["components"]["schemas"]["AvatarUploadResponse"]["properties"].keys()
    )

    openapi_schema = app.openapi()
    live_schemas = openapi_schema["components"]["schemas"]
    assert "AvatarUploadResponse" in live_schemas

    live_fields = set(live_schemas["AvatarUploadResponse"]["properties"].keys())
    for field in contract_fields:
        assert field in live_fields, f"Missing property '{field}' in AvatarUploadResponse"
