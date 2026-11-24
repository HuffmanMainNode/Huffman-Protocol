import copy

from huffman_protocol.hiaa_identity import AgentIdentity
from huffman_protocol.hiaa_message import (
    ReplayCache,
    authorize,
    create_envelope,
    verify_envelope,
)

NOW = 1_800_000_000


def test_independent_identities_sign_and_verify():
    sender, receiver = AgentIdentity.generate(), AgentIdentity.generate()
    message = create_envelope(
        sender,
        receiver.agent_id,
        "status.read",
        {"status": "ready"},
        issued_at=NOW,
        message_id="m-1",
    )
    assert verify_envelope(message, now=NOW + 1)
    assert message["payload"]["sender"] == sender.agent_id


def test_tampering_and_sender_relabeling_are_rejected():
    sender = AgentIdentity.generate()
    message = create_envelope(
        sender, "receiver", "status.read", {"ok": True}, issued_at=NOW
    )
    altered = copy.deepcopy(message)
    altered["payload"]["body"]["ok"] = False
    assert not verify_envelope(altered, now=NOW + 1)
    altered = copy.deepcopy(message)
    altered["payload"]["sender"] = "hiaa:ed25519:forged"
    assert not verify_envelope(altered, now=NOW + 1)


def test_expired_and_future_messages_are_rejected():
    sender = AgentIdentity.generate()
    message = create_envelope(sender, "receiver", "status.read", {}, issued_at=NOW)
    assert not verify_envelope(message, now=NOW + 400)
    assert not verify_envelope(message, now=NOW - 1000)


def test_replay_cache_rejects_duplicate_delivery():
    sender = AgentIdentity.generate()
    message = create_envelope(
        sender, "receiver", "status.read", {}, issued_at=NOW, message_id="replay"
    )
    cache = ReplayCache()
    assert cache.accept(message, now=NOW + 1)
    assert not cache.accept(message, now=NOW + 1)


def test_replay_ids_are_scoped_to_sender():
    first_sender = AgentIdentity.generate()
    second_sender = AgentIdentity.generate()
    first = create_envelope(
        first_sender, "receiver", "status.read", {}, issued_at=NOW, message_id="same-id"
    )
    second = create_envelope(
        second_sender, "receiver", "status.read", {}, issued_at=NOW, message_id="same-id"
    )
    cache = ReplayCache()
    assert cache.accept(first, now=NOW + 1)
    assert cache.accept(second, now=NOW + 1)


def test_capability_is_receiver_controlled():
    sender = AgentIdentity.generate()
    message = create_envelope(sender, "receiver", "status.read", {}, issued_at=NOW)
    assert authorize(message, {"status.read"}, now=NOW + 1)
    assert not authorize(message, {"admin.delete"}, now=NOW + 1)
