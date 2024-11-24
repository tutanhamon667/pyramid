import pytest
from fastapi import status
from app.models import WalletType
from app.db.models import User, Wallet, Key, ReferralRelationship

def test_register_user(client):
    response = client.post(
        "/register",
        params={
            "telegram_id": "new_user"
        },
        json=[{
            "type": "USDT_TRC20",
            "address": "TRC20_ADDRESS"
        }]
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["telegram_id"] == "new_user"
    assert len(data["wallets"]) == 1
    assert data["wallets"][0]["type"] == "USDT_TRC20"
    assert data["wallets"][0]["address"] == "TRC20_ADDRESS"

def test_register_duplicate_user(client, sample_user):
    response = client.post(
        "/register",
        params={
            "telegram_id": sample_user.telegram_id
        },
        json=[{
            "type": "USDT_TRC20",
            "address": "TRC20_ADDRESS"
        }]
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_add_referral(client, sample_user):
    # Create a new user to be referred
    new_user = {
        "telegram_id": "referral_user",
        "wallet_type": WalletType.USDT_TRC20,
        "wallet_address": "TRC20_ADDRESS"
    }
    client.post(
        "/register",
        params={"telegram_id": new_user["telegram_id"]},
        json=[{
            "type": new_user["wallet_type"],
            "address": new_user["wallet_address"]
        }]
    )

    response = client.post(
        "/add-referral",
        params={
            "referrer_id": sample_user.telegram_id,
            "referral_id": "referral_user"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Referral added successfully"

def test_add_invalid_referral(client):
    response = client.post(
        "/add-referral",
        params={
            "referrer_id": "non_existent_user",
            "referral_id": "also_non_existent"
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_verify_payment(client, sample_user):
    # First assign a curator to the user
    sample_user.curator_id = "test_curator"
    client.post(
        "/register",
        params={"telegram_id": "test_curator"},
        json=[{
            "type": "USDT_TRC20",
            "address": "TRC20_ADDRESS"
        }]
    )

    response = client.post(
        "/verify-payment",
        json={
            "user_id": sample_user.telegram_id,
            "verification_code": "VALID_CODE"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert "remaining_codes" in data

def test_verify_payment_invalid_user(client):
    response = client.post(
        "/verify-payment",
        json={
            "user_id": "non_existent_user",
            "verification_code": "VALID_CODE"
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_request_curator_change(client, sample_user):
    # Create a new curator
    new_curator = {
        "telegram_id": "new_curator",
        "wallet_type": WalletType.USDT_TRC20,
        "wallet_address": "TRC20_ADDRESS"
    }
    client.post(
        "/register",
        params={"telegram_id": new_curator["telegram_id"]},
        json=[{
            "type": new_curator["wallet_type"],
            "address": new_curator["wallet_address"]
        }]
    )

    response = client.post(
        "/request-curator-change",
        params={
            "user_id": sample_user.telegram_id
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Curator change requested. Wait 48 hours."

def test_request_curator_change_invalid_curator(client, sample_user):
    response = client.post(
        "/request-curator-change",
        params={
            "user_id": "non_existent_user"
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_user_info(client, sample_user, sample_wallet):
    response = client.get(f"/user/{sample_user.telegram_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["telegram_id"] == sample_user.telegram_id
    assert len(data["wallets"]) == 1
    assert data["wallets"][0]["type"] == sample_wallet.type
    assert data["wallets"][0]["address"] == sample_wallet.address

def test_get_nonexistent_user_info(client):
    response = client.get("/user/non_existent_user")
    assert response.status_code == status.HTTP_404_NOT_FOUND
