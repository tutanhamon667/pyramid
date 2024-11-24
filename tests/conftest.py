import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.db.database import Base, get_db
from app.main import app
from app.db.models import User, Wallet, Key, ReferralRelationship
from typing import Generator
import asyncio

SQLALCHEMY_DATABASE_URL = "postgresql://contract:uyfuy^6jji@localhost:5433/pyramid"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=StaticPool,
        echo=True
    )
    yield engine

@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user(db_session):
    user = User(
        telegram_id="test_user_1",
        key_number=1
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_wallet(db_session, sample_user):
    wallet = Wallet(
        user_id=sample_user.id,
        type="USDT_TRC20",
        address="TRC20123456789"
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    return wallet

@pytest.fixture
def sample_key(db_session):
    key = Key(
        number=1,
        price=1.0,
        is_active=True
    )
    db_session.add(key)
    db_session.commit()
    db_session.refresh(key)
    return key

@pytest.fixture
def sample_referral_relationship(db_session):
    referrer = User(telegram_id="referrer_1")
    referral = User(telegram_id="referral_1")
    db_session.add_all([referrer, referral])
    db_session.commit()
    
    relationship = ReferralRelationship(
        referrer_id=referrer.telegram_id,
        referral_id=referral.telegram_id
    )
    db_session.add(relationship)
    db_session.commit()
    db_session.refresh(relationship)
    return relationship
