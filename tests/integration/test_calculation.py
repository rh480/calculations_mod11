# tests/integration/test_calculation.py
"""
Integration Tests for Polymorphic Calculation Models

These tests verify the polymorphic behavior of the Calculation model hierarchy.
Polymorphism in SQLAlchemy means that different calculation types (Addition,
Subtraction, etc.) can be treated uniformly while maintaining type-specific
behavior.

What Makes These Tests Polymorphic:
1. Factory Pattern: Calculation.create() returns different subclasses
2. Type Resolution: isinstance() checks verify correct subclass instantiation
3. Polymorphic Behavior: Each subclass implements get_result() differently
4. Common Interface: All calculations share the same methods/attributes

These tests demonstrate key OOP principles:
- Inheritance: Subclasses inherit from Calculation
- Polymorphism: Same interface, different implementations
- Encapsulation: Each class encapsulates its calculation logic
"""

import pytest
import uuid

from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)


# Helper function to create a dummy user_id for testing.
def dummy_user_id():
    """
    Generate a random UUID for testing purposes.

    In real tests with a database, you would create an actual user
    and use their ID. This helper is sufficient for unit-level testing
    of the calculation logic without database dependencies.
    """
    return uuid.uuid4()


# ============================================================================
# Tests for Individual Calculation Types
# ============================================================================

def test_addition_get_result():
    """
    Test that Addition.get_result returns the correct sum.

    This verifies that the Addition class correctly implements the
    polymorphic get_result() method for its specific operation.
    """
    addition = Addition(user_id=dummy_user_id(), a=10, b=5)
    result = addition.get_result()
    assert result == 15, f"Expected 15, got {result}"


def test_subtraction_get_result():
    """
    Test that Subtraction.get_result returns the correct difference.

    Subtraction subtracts the second operand from the first operand.
    """
    subtraction = Subtraction(user_id=dummy_user_id(), a=20, b=5)

    # Expected: 20 - 5 = 15
    result = subtraction.get_result()
    assert result == 15, f"Expected 15, got {result}"


def test_multiplication_get_result():
    """
    Test that Multiplication.get_result returns the correct product.

    Multiplication multiplies the first operand by the second operand.
    """
    multiplication = Multiplication(
        user_id=dummy_user_id(), a=2, b=4
    )
    result = multiplication.get_result()
    assert result == 8, f"Expected 8, got {result}"


def test_division_get_result():
    """
    Test that Division.get_result returns the correct quotient.

    Division divides the first operand by the second operand.
    """
    division = Division(user_id=dummy_user_id(), a=100, b=5)

    # Expected: 100 / 5 = 20
    result = division.get_result()
    assert result == 20, f"Expected 20, got {result}"


def test_division_by_zero():
    """
    Test that Division.get_result raises ValueError when dividing by zero.

    This demonstrates EAFP (Easier to Ask for Forgiveness than Permission):
    We attempt the operation and catch the exception rather than checking
    beforehand.
    """
    division = Division(user_id=dummy_user_id(), a=50, b=0)

    with pytest.raises(ValueError, match="Cannot divide by zero"):
        division.get_result()


# ============================================================================
# Tests for Polymorphic Factory Pattern
# ============================================================================

def test_calculation_factory_addition():
    """
    Test the Calculation.create factory method for addition.

    This demonstrates polymorphism: The factory method returns a specific
    subclass (Addition) that can be used through the common Calculation
    interface.

    Key Polymorphic Concepts:
    1. Factory returns the correct subclass type
    2. The returned object behaves as both Calculation and Addition
    3. Type-specific behavior (get_result) works correctly
    """
    calc = Calculation.create(
        calculation_type='Add',
        user_id=dummy_user_id(),
        a=1,
        b=2,
    )

    # Verify polymorphism: factory returned the correct subclass
    assert isinstance(calc, Addition), \
        "Factory did not return an Addition instance."
    assert isinstance(calc, Calculation), \
        "Addition should also be an instance of Calculation."

    # Verify behavior: subclass implements get_result() correctly
    assert calc.get_result() == 3, "Incorrect addition result."
    assert calc.result == 3


def test_calculation_factory_subtraction():
    """
    Test the Calculation.create factory method for subtraction.

    Demonstrates that the factory pattern works consistently across
    different calculation types.
    """
    calc = Calculation.create(
        calculation_type='Sub',
        user_id=dummy_user_id(),
        a=10,
        b=4,
    )

    # Expected: 10 - 4 = 6
    assert isinstance(calc, Subtraction), \
        "Factory did not return a Subtraction instance."
    assert calc.get_result() == 6, "Incorrect subtraction result."
    assert calc.result == 6


def test_calculation_factory_multiplication():
    """
    Test the Calculation.create factory method for multiplication.
    """
    calc = Calculation.create(
        calculation_type='Multiply',
        user_id=dummy_user_id(),
        a=3,
        b=4,
    )

    # Expected: 3 * 4 = 12
    assert isinstance(calc, Multiplication), \
        "Factory did not return a Multiplication instance."
    assert calc.get_result() == 12, "Incorrect multiplication result."
    assert calc.result == 12


def test_calculation_factory_division():
    """
    Test the Calculation.create factory method for division.
    """
    calc = Calculation.create(
        calculation_type='Divide',
        user_id=dummy_user_id(),
        a=100,
        b=5,
    )

    # Expected: 100 / 5 = 20
    assert isinstance(calc, Division), \
        "Factory did not return a Division instance."
    assert calc.get_result() == 20, "Incorrect division result."
    assert calc.result == 20


def test_calculation_factory_invalid_type():
    """
    Test that Calculation.create raises a ValueError for unsupported types.

    This verifies that the factory pattern properly handles invalid inputs
    and provides clear error messages.
    """
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        Calculation.create(
            calculation_type='modulus',  # unsupported type
            user_id=dummy_user_id(),
            a=10,
            b=3,
        )


def test_calculation_factory_division_by_zero():
    """
    Test that Calculation.create raises a ValueError when dividing by zero.

    This verifies that the factory prevents invalid calculations before
    returning a calculation object.
    """
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        Calculation.create(
            calculation_type='Divide',
            user_id=dummy_user_id(),
            a=10,
            b=0,
        )


def test_calculation_factory_case_insensitive():
    """
    Test that the factory is case-insensitive.

    The factory should accept 'Add', 'ADD', 'add', etc.
    """
    # Test various cases
    for calc_type in ['add', 'Add', 'ADD', 'AdD']:
        calc = Calculation.create(
            calculation_type=calc_type,
            user_id=dummy_user_id(),
            a=5,
            b=3,
        )

        assert isinstance(calc, Addition), \
            f"Factory failed for case: {calc_type}"
        assert calc.get_result() == 8


# ============================================================================
# Tests for Input Validation (Edge Cases)
# ============================================================================

def test_negative_numbers_for_addition():
    """
    Test that Addition correctly handles negative numbers.

    This verifies that calculations accept valid negative numeric operands.
    """
    addition = Addition(user_id=dummy_user_id(), a=-5, b=-10)
    assert addition.get_result() == -15


def test_zero_operands_for_multiplication():
    """
    Test that Multiplication correctly handles zero operands.

    Multiplication by zero should always return zero.
    """
    multiplication = Multiplication(user_id=dummy_user_id(), a=5, b=0)
    assert multiplication.get_result() == 0


def test_negative_numbers_for_subtraction():
    """
    Test that Subtraction correctly handles negative numbers.
    """
    subtraction = Subtraction(user_id=dummy_user_id(), a=-5, b=-10)
    assert subtraction.get_result() == 5


# ============================================================================
# Tests Demonstrating Polymorphic Behavior
# ============================================================================

def test_polymorphic_list_of_calculations():
    """
    Test that different calculation types can be stored in the same list.

    This demonstrates polymorphism: A list of Calculation objects can contain
    different subclasses, and each maintains its type-specific behavior.

    This is a key benefit of polymorphism: you can treat different types
    uniformly while they maintain their unique implementations.
    """
    user_id = dummy_user_id()

    # Create a list of different calculation types
    calculations = [
        Calculation.create('Add', user_id, 1, 2),
        Calculation.create('Sub', user_id, 10, 3),
        Calculation.create('Multiply', user_id, 2, 3),
        Calculation.create('Divide', user_id, 100, 5),
    ]

    # Each calculation maintains its specific type
    assert isinstance(calculations[0], Addition)
    assert isinstance(calculations[1], Subtraction)
    assert isinstance(calculations[2], Multiplication)
    assert isinstance(calculations[3], Division)

    # All calculations share the same interface
    results = [calc.get_result() for calc in calculations]

    # Each produces its type-specific result
    assert results == [3, 7, 6, 20]


def test_polymorphic_method_calling():
    """
    Test that polymorphic methods work correctly.

    This demonstrates that you can call get_result() on any Calculation
    subclass and get the correct type-specific behavior without knowing
    the exact subclass type at compile time.
    """
    user_id = dummy_user_id()

    # Create calculations dynamically based on type string
    calc_types = ['Add', 'Sub', 'Multiply', 'Divide']
    expected_results = [12, 8, 20, 5]

    for calc_type, expected in zip(calc_types, expected_results):
        calc = Calculation.create(
            calc_type,
            user_id,
            10,
            2
        )

        # Polymorphic method call: same method name, different behavior
        result = calc.get_result()
        assert result == expected, \
            f"{calc_type} failed: expected {expected}, got {result}"
