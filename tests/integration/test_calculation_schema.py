# tests/integration/test_calculation_schema.py
"""
Integration Tests for Calculation Pydantic Schemas

These tests verify that Pydantic schemas correctly validate calculation data
before it reaches the application logic. This is an important security and
data integrity layer that prevents invalid data from entering the system.

Key Testing Concepts:
1. Valid Data: Ensure schemas accept correct data
2. Invalid Data: Ensure schemas reject incorrect data with clear messages
3. Edge Cases: Test boundary conditions
4. Business Rules: Verify domain-specific validation (e.g., no division by 0)
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError
from app.schemas.calculation import (
    CalculationType,
    CalculationBase,
    CalculationCreate,
    CalculationUpdate,
    CalculationResponse,
)


# ============================================================================
# Tests for CalculationType Enum
# ============================================================================

def test_calculation_type_enum_values():
    """Test that CalculationType enum has correct values."""
    assert CalculationType.ADDITION.value == "addition"
    assert CalculationType.SUBTRACTION.value == "subtraction"
    assert CalculationType.MULTIPLICATION.value == "multiplication"
    assert CalculationType.DIVISION.value == "division"


# ============================================================================
# Tests for CalculationBase Schema
# ============================================================================

def test_calculation_base_valid_addition():
    """Test CalculationBase with valid addition data."""
    data = {
        "type": "addition",
        "a": 10.5,
        "b": 3
    }
    calc = CalculationBase(**data)
    assert calc.type == CalculationType.ADDITION
    assert calc.a == 10.5
    assert calc.b == 3.0


def test_calculation_base_valid_subtraction():
    """Test CalculationBase with valid subtraction data."""
    data = {
        "type": "subtraction",
        "a": 20,
        "b": 5.5
    }
    calc = CalculationBase(**data)
    assert calc.type == CalculationType.SUBTRACTION
    assert calc.a == 20.0
    assert calc.b == 5.5


def test_calculation_base_valid_multiplication():
    """Test CalculationBase with valid multiplication data."""
    data = {
        "type": "multiplication",
        "a": 10,
        "b": 5
    }
    calc = CalculationBase(**data)

    assert calc.type == CalculationType.MULTIPLICATION
    assert calc.a == 10.0
    assert calc.b == 5.0


def test_calculation_base_valid_division():
    """Test CalculationBase with valid division data."""
    data = {
        "type": "division",
        "a": 100,
        "b": 5
    }
    calc = CalculationBase(**data)

    assert calc.type == CalculationType.DIVISION
    assert calc.a == 100.0
    assert calc.b == 5.0


def test_calculation_base_case_insensitive_type():
    """Test that calculation type is case-insensitive."""
    for type_variant in ["Addition", "ADDITION", "AdDiTiOn"]:
        data = {
            "type": type_variant,
            "a": 1,
            "b": 2
        }
        calc = CalculationBase(**data)
        assert calc.type == CalculationType.ADDITION


def test_calculation_base_invalid_type():
    """Test that invalid calculation type raises ValidationError."""
    data = {
        "type": "modulus",
        "a": 10,
        "b": 3
    }
    with pytest.raises(ValidationError):
        CalculationBase(**data)

def test_calculation_base_missing_operand_a():
    """Test that missing first operand raises ValidationError."""
    data = {
        "type": "addition",
        "b": 5
    }

    with pytest.raises(ValidationError):
        CalculationBase(**data)


def test_calculation_base_missing_operand_b():
    """Test that missing second operand raises ValidationError."""
    data = {
        "type": "addition",
        "a": 10
    }

    with pytest.raises(ValidationError):
        CalculationBase(**data)


def test_calculation_base_invalid_operand():
    """Test that non-numeric operands raise ValidationError."""
    data = {
        "type": "addition",
        "a": "not a number",
        "b": 5
    }

    with pytest.raises(ValidationError):
        CalculationBase(**data)


def test_calculation_base_division_by_zero():
    """
    Test that division by zero is caught by schema validation.

    This demonstrates LBYL (Look Before You Leap): We check for the error
    condition before attempting the operation. This is appropriate at the
    API boundary to provide immediate feedback to the client.
    """
    data = {
        "type": "division",
        "a": 100,
        "b": 0
    }

    with pytest.raises(ValidationError) as exc_info:
        CalculationBase(**data)

    assert any(
        "Cannot divide by zero" in str(error)
        for error in exc_info.value.errors()
    )


def test_calculation_base_division_zero_numerator_ok():
    """Test that zero as the numerator is allowed."""
    data = {
        "type": "division",
        "a": 0,
        "b": 5
    }

    calc = CalculationBase(**data)

    assert calc.a == 0
    assert calc.b == 5


def test_calculation_base_negative_numbers():
    """Test that schemas accept negative numbers."""
    data = {
        "type": "addition",
        "a": -5,
        "b": -10
    }

    calc = CalculationBase(**data)

    assert calc.a == -5.0
    assert calc.b == -10.0


def test_calculation_base_decimal_numbers():
    """Test that schemas accept decimal numbers."""
    data = {
        "type": "addition",
        "a": 10.5,
        "b": 3.25
    }

    calc = CalculationBase(**data)

    assert calc.a == 10.5
    assert calc.b == 3.25


def test_calculation_base_large_numbers():
    """Test that schemas handle large numbers correctly."""
    data = {
        "type": "multiplication",
        "a": 1e10,
        "b": 1e10
    }
    calc = CalculationBase(**data)

    assert calc.a == 1e10
    assert calc.b == 1e10


def test_calculation_base_rejects_infinity():
    """Test that schemas reject infinite operands."""
    data = {
        "type": "addition",
        "a": float("inf"),
        "b": 5
    }

    with pytest.raises(ValidationError):
        CalculationBase(**data)


# ============================================================================
# Tests for CalculationCreate Schema
# ============================================================================

def test_calculation_create_valid():
    """Test CalculationCreate with valid data."""
    user_id = uuid4()
    data = {
        "type": "multiplication",
        "a": 2,
        "b": 3,
        "user_id": str(user_id)
    }
    calc = CalculationCreate(**data)
    assert calc.type == CalculationType.MULTIPLICATION
    assert calc.a == 2.0
    assert calc.b == 3.0
    assert calc.user_id == user_id


def test_calculation_create_missing_user_id():
    """Test that CalculationCreate requires user_id."""
    data = {
        "type": "addition",
        "a": 1,
        "b": 2
    }

    with pytest.raises(ValidationError):
        CalculationCreate(**data)

def test_calculation_create_invalid_user_id():
    """Test that invalid UUID format raises ValidationError."""
    data = {
        "type": "subtraction",
        "a": 10,
        "b": 5,
        "user_id": "not-a-valid-uuid"
    }
    with pytest.raises(ValidationError):
        CalculationCreate(**data)


# ============================================================================
# Tests for CalculationUpdate Schema
# ============================================================================

def test_calculation_update_valid():
    """Test CalculationUpdate with valid data."""
    data = {
        "a": 42,
        "b": 7
    }
    calc = CalculationUpdate(**data)

    assert calc.a == 42.0
    assert calc.b == 7.0


def test_calculation_update_all_fields_optional():
    """Test that CalculationUpdate can be empty (all fields optional)."""
    data = {}
    calc = CalculationUpdate(**data)

    assert calc.a is None
    assert calc.b is None


def test_calculation_update_only_a():
    """Test that CalculationUpdate allows updating only operand a."""
    calc = CalculationUpdate(a=20)

    assert calc.a == 20.0
    assert calc.b is None


def test_calculation_update_only_b():
    """Test that CalculationUpdate allows updating only operand b."""
    calc = CalculationUpdate(b=10)

    assert calc.a is None
    assert calc.b == 10.0


def test_calculation_update_invalid_operand():
    """Test that invalid update operands raise ValidationError."""
    with pytest.raises(ValidationError):
        CalculationUpdate(a="not a number")


# ============================================================================
# Tests for CalculationResponse Schema
# ============================================================================

def test_calculation_response_valid():
    """Test CalculationResponse with all required fields."""
    data = {
        "id": uuid4(),
        "user_id": uuid4(),
        "type": "addition",
        "a": 10,
        "b": 5,
        "result": 15.0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    calc = CalculationResponse(**data)

    assert calc.a == 10.0
    assert calc.b == 5.0
    assert calc.result == 15.0
    assert calc.type == CalculationType.ADDITION


def test_calculation_response_missing_result():
    """Test that CalculationResponse requires result field."""
    data = {
        "id": uuid4(),
        "user_id": uuid4(),
        "type": "multiplication",
        "a": 2,
        "b": 3,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    with pytest.raises(ValidationError):
        CalculationResponse(**data)


def test_calculation_response_missing_timestamps():
    """Test that CalculationResponse requires timestamps."""
    data = {
        "id": uuid4(),
        "user_id": uuid4(),
        "type": "addition",
        "a": 10,
        "b": 5,
        "result": 15.0
    }

    with pytest.raises(ValidationError):
        CalculationResponse(**data)


# ============================================================================
# Tests for Complex Validation Scenarios
# ============================================================================

def test_multiple_calculations_with_different_types():
    """
    Test that schemas correctly validate multiple calculations of
    different types.
    """
    user_id = uuid4()

    calcs_data = [
        {"type": "addition", "a": 1, "b": 2, "user_id": str(user_id)},
        {"type": "subtraction", "a": 10, "b": 3, "user_id": str(user_id)},
        {"type": "multiplication", "a": 2, "b": 4, "user_id": str(user_id)},
        {"type": "division", "a": 100, "b": 5, "user_id": str(user_id)},
    ]

    calcs = [CalculationCreate(**data) for data in calcs_data]

    assert len(calcs) == 4
    assert calcs[0].type == CalculationType.ADDITION
    assert calcs[1].type == CalculationType.SUBTRACTION
    assert calcs[2].type == CalculationType.MULTIPLICATION
    assert calcs[3].type == CalculationType.DIVISION


def test_schema_with_zero_operands():
    """Test that zero is accepted for non-denominator operands."""
    calc = CalculationBase(
        type="addition",
        a=0,
        b=0
    )

    assert calc.a == 0
    assert calc.b == 0


def test_schema_with_mixed_int_and_float():
    """Test that schemas accept mixed integers and floats."""
    calc = CalculationBase(
        type="subtraction",
        a=100,
        b=23.5
    )

    assert calc.a == 100.0
    assert calc.b == 23.5

@pytest.mark.parametrize("raw,expected", [
    ("Add", CalculationType.ADDITION),
    ("Sub", CalculationType.SUBTRACTION),
    ("Multiply", CalculationType.MULTIPLICATION),
    ("Divide", CalculationType.DIVISION),
])
def test_short_type_names_accepted(raw, expected):
    assert CalculationBase(type=raw, a=1, b=1).type == expected