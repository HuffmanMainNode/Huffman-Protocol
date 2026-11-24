import threading

import pytest

from huffman_protocol.hiaa_identity import AgentIdentity
from huffman_protocol.hiaa_message import create_envelope
from huffman_protocol.hiaa_transport import HIAARequestServer, send_envelope


def test_two_independent_identities_sign_and_verify():
    receiver = AgentIdentity.generate()
    sender = AgentIdentity.generate()
    with HIAARequestServer(
        ("127.0.0.1", 0),
        receiver,
        {"status.read"},
        lambda body: {"echo": body},
        trusted_senders={sender.agent_id},
    ) as server:
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            message = create_envelope(
                sender,
                receiver.agent_id,
                "status.read",
                {"question": "status"},
            )
            acknowledgement = send_envelope(
                server.server_address,
                message,
                expected_peer=receiver.agent_id,
            )
            assert acknowledgement["payload"]["sender"] == receiver.agent_id
            assert acknowledgement["payload"]["recipient"] == sender.agent_id
            assert acknowledgement["payload"]["body"]["result"] == {"echo": {"question": "status"}}
        finally:
            server.shutdown()
            worker.join(timeout=2)


def test_tcp_receiver_denies_unapproved_capability():
    receiver = AgentIdentity.generate()
    sender = AgentIdentity.generate()
    with HIAARequestServer(
        ("127.0.0.1", 0),
        receiver,
        {"status.read"},
        lambda body: {"unexpected": True},
        trusted_senders={sender.agent_id},
    ) as server:
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            message = create_envelope(
                sender,
                receiver.agent_id,
                "admin.delete",
                {"target": "all"},
            )
            with pytest.raises(PermissionError):
                send_envelope(
                    server.server_address,
                    message,
                    expected_peer=receiver.agent_id,
                )
        finally:
            server.shutdown()
            worker.join(timeout=2)


def test_tcp_receiver_rejects_message_addressed_to_another_agent():
    receiver = AgentIdentity.generate()
    sender = AgentIdentity.generate()
    other = AgentIdentity.generate()
    with HIAARequestServer(
        ("127.0.0.1", 0),
        receiver,
        {"status.read"},
        lambda body: {"unexpected": True},
        trusted_senders={sender.agent_id},
    ) as server:
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            message = create_envelope(
                sender,
                other.agent_id,
                "status.read",
                {"question": "status"},
            )
            with pytest.raises(PermissionError):
                send_envelope(
                    server.server_address,
                    message,
                    expected_peer=receiver.agent_id,
                )
        finally:
            server.shutdown()
            worker.join(timeout=2)
