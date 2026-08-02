import asyncio
from typing import Any

import pytest
from httpx import AsyncClient
from httpx_ws import WebSocketDisconnect
from starlette import status
from httpx_ws.transport import ASGIWebSocketTransport
from httpx_ws import aconnect_ws, AsyncWebSocketSession
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from user_activity.dependencies import get_mongo_db
from database import ActivationTokenModel
from main import app


WS_PATH = "/api/v1/activity/users/"

RECEIVE_TIMEOUT = 5.0


async def _receive_json(ws: AsyncWebSocketSession) -> dict:
    """
    Receive and parse a single JSON message from a WebSocket test session.

    Args:
        ws (Any): An open WebSocket test session (httpx_ws connection).

    Returns:
        dict: The parsed JSON message received from the WebSocket.
    """
    return await asyncio.wait_for(ws.receive_json(), timeout=RECEIVE_TIMEOUT)


async def _register_activate_and_login(
        e2e_client: AsyncClient,
        e2e_db_session: AsyncSession,
        email: str,
        password: str = "StrongPass!123"
) -> tuple[int, str]:
    """
    Registers a user through the real /accounts/register/ endpoint, pulls the
    activation token straight from psql (the email body only contains a static
    link, not the token itself), activates the account, then logs in and
    returns (user_id, access_token).
    """
    register_resp = await e2e_client.post(
        "/api/v1/accounts/register/",
        json={"email": email, "password": password},
    )
    assert register_resp.status_code == 201, register_resp.text
    user_id = register_resp.json()["id"]

    stmt = select(ActivationTokenModel).where(ActivationTokenModel.user_id == user_id)
    result = await e2e_db_session.execute(stmt)
    activation_token = result.scalars().first()
    assert activation_token is not None, "Activation token was not created for the new user"

    activate_resp = await e2e_client.post(
        "/api/v1/accounts/activate/",
        json={"email": email, "token": activation_token.token},
    )
    assert activate_resp.status_code == 200, activate_resp.text

    login_resp = await e2e_client.post(
        "/api/v1/accounts/login/",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 201, login_resp.text
    access_token = login_resp.json()["access_token"]

    return user_id, access_token


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_two_users_connect_and_receive_connect_and_disconnect_events(
        e2e_client: AsyncClient,
        e2e_db_session: AsyncSession,
        reset_db_once_for_e2e: Any,
        seed_user_groups: Any,
        cleanup_mongo_user_activity: Any,
) -> None:
    """
    Verify that when two users connect to the activity WebSocket, each user
    receives the correct online-users snapshot, connect notification, and
    disconnect notification for the other user.

    Args:
        e2e_client (AsyncClient): HTTP client used to register/activate/login users.
        e2e_db_session (AsyncSession): Async database session for direct DB access.
        reset_db_once_for_e2e (Any): Fixture that resets the test database state.
        seed_user_groups (Any): Fixture that seeds required user groups.
        cleanup_mongo_user_activity (Any): Fixture that clears Mongo activity data after the test.

    Returns:
        None
    """
    user1_id, token1 = await _register_activate_and_login(
        e2e_client, e2e_db_session, email="cast_one@example.com"
    )
    user2_id, token2 = await _register_activate_and_login(
        e2e_client, e2e_db_session, email="cast_two@example.com"
    )

    transport = ASGIWebSocketTransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with aconnect_ws(WS_PATH, client) as ws1:
            await ws1.send_json({"token": token1})

            snapshot1 = await _receive_json(ws1)
            assert snapshot1["event"] == "online_users", (
                f"Expected 'online_users' event, got {snapshot1['event']}"
            )
            assert user1_id in [user["user_id"] for user in snapshot1["users"]], (
                "User1 should be present in the initial online users snapshot"
            )

            async with aconnect_ws(WS_PATH, client) as ws2:
                await ws2.send_json({"token": token2})

                user1_connected_event = await _receive_json(ws1)
                assert user1_connected_event["event"] == "user_connected", (
                    f"Expected 'user_connected' event, got {user1_connected_event['event']}"
                )
                assert user1_connected_event["user"]["user_id"] == user2_id, (
                    "User1 should be notified that user2 connected"
                )

                snapshot2 = await _receive_json(ws2)
                assert snapshot2["event"] == "online_users", (
                    f"Expected 'online_users' event, got {snapshot2['event']}"
                )
                assert {user["user_id"] for user in snapshot2["users"]} == {user1_id, user2_id}, (
                    "User2's snapshot should contain both online users"
                )

            user1_disconnected_event = await _receive_json(ws1)
            assert user1_disconnected_event["event"] == "user_disconnected", (
                f"Expected 'user_disconnected' event, got {user1_disconnected_event['event']}"
            )
            assert user1_disconnected_event["user_id"] == user2_id, (
                "User1 should be notified that user2 disconnected"
            )


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_invalid_token_closes_connection_with_policy_violation(
        e2e_client: AsyncClient,
        e2e_db_session: AsyncSession,
        reset_db_once_for_e2e: Any,
        seed_user_groups: Any,
        cleanup_mongo_user_activity: Any,
) -> None:
    """
    If the client sends a malformed/invalid JWT as the auth message,
    the server must close the socket with WS_1008_POLICY_VIOLATION
    and never register the connection.
    """
    transport = ASGIWebSocketTransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with aconnect_ws(WS_PATH, client) as ws:
            await ws.send_json({"token": "invalid_token"})

            with pytest.raises(WebSocketDisconnect) as exc_info:
                await _receive_json(ws)

            assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_user_activity_persisted_in_mongo(
        e2e_client: AsyncClient,
        e2e_db_session: AsyncSession,
        reset_db_once_for_e2e: Any,
        seed_user_groups: Any,
        cleanup_mongo_user_activity: Any,
) -> None:
    """
    On connect the user's activity doc must flip to "online" with a
    connected_at timestamp; on disconnect it must flip to "offline"
    with a disconnected_at timestamp.
    """
    user_id, token = await _register_activate_and_login(
        e2e_client, e2e_db_session, email="mongo_check@example.com"
    )
    db = get_mongo_db()

    transport = ASGIWebSocketTransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with aconnect_ws(WS_PATH, client) as ws:
            await ws.send_json({"token": token})
            snapshot = await _receive_json(ws)
            assert snapshot["event"] == "online_users"

            record = await db["user_activity"].find_one({"user_id": user_id}, {"_id": 0})
            assert record is not None
            assert record["status"] == "online"
            assert record.get("connected_at") is not None

        await asyncio.sleep(0.2)

        record = await db["user_activity"].find_one({"user_id": user_id}, {"_id": 0})
        assert record["status"] == "offline"
        assert record.get("disconnected_at") is not None


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_second_connection_same_user_does_not_rebroadcast(
        e2e_client: AsyncClient,
        e2e_db_session: AsyncSession,
        reset_db_once_for_e2e: Any,
        seed_user_groups: Any,
        cleanup_mongo_user_activity: Any,
) -> None:
    """
    A single user opening a second tab (second websocket) must not
    trigger another "user_connected" broadcast to other users, and
    closing just one of the two tabs must not trigger "user_disconnected".
    """
    user1_id, token1 = await _register_activate_and_login(
        e2e_client, e2e_db_session, email="two_tabs@example.com"
    )
    user2_id, token2 = await _register_activate_and_login(
        e2e_client, e2e_db_session, email="observer@example.com"
    )

    transport = ASGIWebSocketTransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with aconnect_ws(WS_PATH, client) as observer_ws:
            await observer_ws.send_json({"token": token2})
            await _receive_json(observer_ws)

            async with aconnect_ws(WS_PATH, client) as tab1:
                await tab1.send_json({"token": token1})
                event = await _receive_json(observer_ws)
                assert event["event"] == "user_connected"
                assert event["user"]["user_id"] == user1_id

                async with aconnect_ws(WS_PATH, client) as tab2:
                    await tab2.send_json({"token": token1})
                    await _receive_json(tab2)

                    with pytest.raises(asyncio.TimeoutError):
                        await asyncio.wait_for(observer_ws.receive_json(), timeout=1.0)

                with pytest.raises(asyncio.TimeoutError):
                    await asyncio.wait_for(observer_ws.receive_json(), timeout=1.0)

            disconnect_event = await _receive_json(observer_ws)
            assert disconnect_event["event"] == "user_disconnected"
            assert disconnect_event["user_id"] == user1_id
