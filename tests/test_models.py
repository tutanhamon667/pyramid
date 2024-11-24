import pytest
from app.db.models import User, Wallet, Key, ReferralRelationship
from sqlalchemy.exc import IntegrityError

def test_create_user(db_session):
    user = User(telegram_id="test_user")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
    assert user.telegram_id == "test_user"

def test_user_unique_telegram_id(db_session):
    user1 = User(telegram_id="test_user")
    user2 = User(telegram_id="test_user")
    db_session.add(user1)
    db_session.commit()
    
    with pytest.raises(IntegrityError):
        db_session.add(user2)
        db_session.commit()

def test_create_wallet(db_session, sample_user):
    wallet = Wallet(
        user_id=sample_user.id,
        type="USDT_TRC20",
        address="TRC20123456789"
    )
    db_session.add(wallet)
    db_session.commit()
    assert wallet.id is not None
    assert wallet.user_id == sample_user.id
    assert wallet.type == "USDT_TRC20"

def test_create_key(db_session):
    key = Key(number=1, price=1.0, is_active=True)
    db_session.add(key)
    db_session.commit()
    assert key.number == 1
    assert key.price == 1.0
    assert key.is_active is True

def test_create_referral_relationship(db_session):
    referrer = User(telegram_id="referrer")
    referral = User(telegram_id="referral")
    db_session.add_all([referrer, referral])
    db_session.commit()
    
    relationship = ReferralRelationship(
        referrer_id=referrer.telegram_id,
        referral_id=referral.telegram_id
    )
    db_session.add(relationship)
    db_session.commit()
    assert relationship.id is not None

def test_user_wallet_relationship(db_session, sample_user):
    wallet1 = Wallet(user_id=sample_user.id, type="USDT_TRC20", address="addr1")
    wallet2 = Wallet(user_id=sample_user.id, type="BTC", address="addr2")
    db_session.add_all([wallet1, wallet2])
    db_session.commit()
    
    assert len(sample_user.wallets) == 2
    assert sample_user.wallets[0].type in ["USDT_TRC20", "BTC"]
    assert sample_user.wallets[1].type in ["USDT_TRC20", "BTC"]

def test_user_referrals(db_session):
    referrer = User(telegram_id="referrer")
    referral1 = User(telegram_id="referral1")
    referral2 = User(telegram_id="referral2")
    db_session.add_all([referrer, referral1, referral2])
    db_session.commit()
    
    rel1 = ReferralRelationship(referrer_id=referrer.telegram_id, referral_id=referral1.telegram_id)
    rel2 = ReferralRelationship(referrer_id=referrer.telegram_id, referral_id=referral2.telegram_id)
    db_session.add_all([rel1, rel2])
    db_session.commit()
    
    referrals = db_session.query(ReferralRelationship).filter_by(referrer_id=referrer.telegram_id).all()
    assert len(referrals) == 2
