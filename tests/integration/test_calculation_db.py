#tests/integration/test_calculation_db.py
import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.calculation import Calculation, Addition, Division
from app.schemas.calculation import CalculationRead

def test_insert_and_read_back(db_session, user):
    calc = Calculation.create("Divide", user.id, 10, 4)
    db_session.add(calc)
    db_session.flush()
    db_session.expire_all()                      # force a real SELECT

    saved = db_session.query(Calculation).filter_by(id=calc.id).one()
    assert isinstance(saved, Division)
    assert (saved.a, saved.b, saved.type, saved.result) == (10, 4, "division", 2.5)
    assert saved.user_id == user.id
    assert saved.created_at is not None

def test_polymorphic_query_returns_subclasses(db_session, user):
    for t in ("Add", "Sub", "Multiply", "Divide"):
        db_session.add(Calculation.create(t, user.id, 8, 2))
    db_session.flush()
    db_session.expire_all()
    rows = db_session.query(Calculation).filter_by(user_id=user.id).all()
    assert {type(r).__name__ for r in rows} == {
        "Addition", "Subtraction", "Multiplication", "Division"}

def test_invalid_foreign_key_rejected(db_session):
    db_session.add(Calculation.create("Add", uuid.uuid4(), 1, 2))
    with pytest.raises(IntegrityError):
        db_session.flush()

def test_missing_operand_rejected(db_session, user):
    db_session.add(Addition(user_id=user.id, a=1))   # b missing
    with pytest.raises(IntegrityError):
        db_session.flush()

def test_division_by_zero_is_never_stored(db_session, user):
    with pytest.raises(ValueError):
        Calculation.create("Divide", user.id, 1, 0)
    assert db_session.query(Calculation).filter_by(user_id=user.id).count() == 0

def test_read_schema_serializes_orm_row(db_session, user):
    calc = Calculation.create("Add", user.id, 1, 2)
    db_session.add(calc)
    db_session.flush()
    read = CalculationRead.model_validate(calc)
    assert read.result == 3
    assert set(read.model_dump()) == {
        "id", "a", "b", "type", "result", "user_id", "created_at", "updated_at"}