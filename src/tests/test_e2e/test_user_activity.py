import asyncio
from typing import Any

import pytest
from httpx import AsyncClient
from httpx_ws.transport import ASGIWebSocketTransport
from httpx_ws import aconnect_ws, AsyncWebSocketSession
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
