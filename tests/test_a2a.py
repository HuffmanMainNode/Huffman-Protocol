import importlib.util
import json
import sys
from pathlib import Path

import pytest

from huffman_protocol.a2a import validate_a2a_card
from huffman_protocol.cli import main
from huffman_protocol.validation import DocumentValidationError

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("a2a") is None,
    reason="install the optional a2a extra to run A2A adapter tests",
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "a2a-v1.0" / "agent-card.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def write_card(tmp_path: Path, document: dict) -> Path:
    path = tmp_path / "agent-card.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_valid_a2a_v1_agent_card_passes_offline() -> None:
    validate_a2a_card(FIXTURE)


def test_missing_required_agent_name_is_rejected(tmp_path: Path) -> None:
    document = load_fixture()
    document.pop("name")
    with pytest.raises(DocumentValidationError, match="invalid A2A AgentCard"):
        validate_a2a_card(write_card(tmp_path, document))


def test_unknown_agent_card_field_is_rejected(tmp_path: Path) -> None:
    document = load_fixture()
    document["unrecognizedField"] = "not part of A2A 1.0"
    with pytest.raises(DocumentValidationError, match="invalid A2A AgentCard"):
        validate_a2a_card(write_card(tmp_path, document))


def test_card_without_a2a_1_0_interface_is_rejected(tmp_path: Path) -> None:
    document = load_fixture()
    document["supportedInterfaces"][0]["protocolVersion"] = "0.3"
    with pytest.raises(DocumentValidationError, match="protocolVersion '1.0'"):
        validate_a2a_card(write_card(tmp_path, document))


def test_invalid_interface_type_is_rejected(tmp_path: Path) -> None:
    document = load_fixture()
    document["supportedInterfaces"] = "not-an-array"
    with pytest.raises(DocumentValidationError, match="invalid A2A AgentCard"):
        validate_a2a_card(write_card(tmp_path, document))


def test_duplicate_json_keys_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "duplicate-card.json"
    path.write_text('{"name":"first","name":"second"}', encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="duplicate JSON object key"):
        validate_a2a_card(path)


def test_cli_validate_a2a_card_command(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["huffman-protocol", "validate-a2a-card", str(FIXTURE)],
    )
    assert main() == 0
    assert "VALID:" in capsys.readouterr().out
