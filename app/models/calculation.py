# app/models/calculation.py
"""
Calculation Models with Polymorphic Inheritance

This module demonstrates SQLAlchemy's polymorphic inheritance pattern, where
multiple calculation types (Addition, Subtraction, Multiplication, Division)
inherit from a base Calculation model. This is a powerful ORM feature that
allows different types of calculations to be stored in the same table while
maintaining type-specific behavior.

Polymorphic Inheritance Explained:
- Single Table Inheritance: All calculation types share one table
- Discriminator Column: The 'type' column determines which class to use
- Polymorphic Identity: Each subclass has a unique identifier
- Factory Pattern: Calculation.create() returns the appropriate subclass

This design pattern allows for:
1. Querying all calculations together: session.query(Calculation).all()
2. Automatic type resolution: SQLAlchemy returns the correct subclass
3. Type-specific behavior: Each subclass implements get_result() differently
4. Easy extensibility: Add new calculation types by creating new subclasses
"""

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class AbstractCalculation:
    """
    Abstract base class defining common attributes for all calculations.

    This class defines the common structure shared across all calculation
    types. Each calculation uses two numeric operands, a and b, instead
    of a variable-length inputs list.

    Design Pattern: This follows the Template Method pattern, where the
    abstract class defines the structure and subclasses provide specific
    implementations.
    """

    @property
    def inputs(self) -> list[float]:
        """
        Return the two operands as a list for compatibility with code
        that expects an inputs property.
        """
        return [self.a, self.b]

    @classmethod
    def create(
        cls,
        calculation_type: str,
        user_id: uuid.UUID,
        a: float,
        b: float
    ) -> "Calculation":
        """
        Factory method to create the appropriate calculation subclass.

        This implements the Factory Pattern, which provides a centralized way
        to create objects without specifying their exact class.

        Benefits of Factory Pattern:
        1. Encapsulation: Object creation logic is in one place
        2. Flexibility: Easy to add new calculation types
        3. Type Safety: Returns strongly-typed subclass instances

        Args:
            calculation_type: Type of calculation (e.g., 'Add')
            user_id: UUID of the user creating the calculation
            a: First operand
            b: Second operand

        Returns:
            An instance of the appropriate Calculation subclass

        Raises:
            ValueError: If calculation_type is unsupported or division
                        by zero is attempted
        """
        calculation_classes = {
            "add": Addition,
            "addition": Addition,
            "sub": Subtraction,
            "subtract": Subtraction,
            "subtraction": Subtraction,
            "multiply": Multiplication,
            "multiplication": Multiplication,
            "divide": Division,
            "division": Division,
        }

        calculation_class = calculation_classes.get(
            calculation_type.lower()
        )

        if calculation_class is None:
            raise ValueError(
                f"Unsupported calculation type: {calculation_type}"
            )

        calculation = calculation_class(
            user_id=user_id,
            a=a,
            b=b
        )

        calculation.result = calculation.get_result()

        return calculation

    def get_result(self) -> float:
        """
        Abstract method to compute the calculation result.

        Each subclass must implement this method with its specific logic.
        This follows the Template Method pattern where the interface is
        defined here but implementation is deferred to subclasses.

        Raises:
            NotImplementedError: If called on base class
        """
        raise NotImplementedError(
            "Subclasses must implement get_result() method"
        )

    def __repr__(self) -> str:
        return (
            f"<Calculation(type={self.type}, "
            f"a={self.a}, b={self.b})>"
        )


class Calculation(Base, AbstractCalculation):
    """
    Base calculation model with polymorphic configuration.

    This class combines SQLAlchemy's Base with our AbstractCalculation mixin
    and configures polymorphic inheritance through __mapper_args__.

    Polymorphic Configuration:
    - polymorphic_on: Specifies the discriminator column (type)
    - polymorphic_identity: The value stored for this base class

    When querying Calculation, SQLAlchemy automatically:
    1. Reads the 'type' column value
    2. Determines the appropriate subclass
    3. Returns an instance of that subclass
    """

    __tablename__ = 'calculations'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    type = Column(
        String(50),
        nullable=False,
        index=True
    )

    a = Column(
        Float,
        nullable=False
    )

    b = Column(
        Float,
        nullable=False
    )

    result = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="calculations"
    )

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "calculation",
    }


class Addition(Calculation):
    """
    Addition calculation subclass.

    Polymorphic Identity: 'addition'
    Operation: Adds the first operand to the second operand

    Example:
        add = Addition(user_id=user_id, a=1, b=2)
        result = add.get_result()  # Returns 3
    """

    __mapper_args__ = {"polymorphic_identity": "addition"}

    def get_result(self) -> float:
        """
        Calculate the sum of the two operands.

        Returns:
            The sum of a and b
        """
        return self.a + self.b


class Subtraction(Calculation):
    """
    Subtraction calculation subclass.

    Polymorphic Identity: 'subtraction'
    Operation: Subtracts the second operand from the first operand

    Example:
        sub = Subtraction(user_id=user_id, a=10, b=3)
        result = sub.get_result()  # Returns 7
    """

    __mapper_args__ = {"polymorphic_identity": "subtraction"}

    def get_result(self) -> float:
        """
        Subtract the second operand from the first operand.

        Returns:
            The result of a minus b
        """
        return self.a - self.b


class Multiplication(Calculation):
    """
    Multiplication calculation subclass.

    Polymorphic Identity: 'multiplication'
    Operation: Multiplies the first operand by the second operand

    Example:
        mult = Multiplication(user_id=user_id, a=2, b=3)
        result = mult.get_result()  # Returns 6
    """

    __mapper_args__ = {"polymorphic_identity": "multiplication"}

    def get_result(self) -> float:
        """
        Calculate the product of the two operands.

        Returns:
            The product of a and b
        """
        return self.a * self.b


class Division(Calculation):
    """
    Division calculation subclass.

    Polymorphic Identity: 'division'
    Operation: Divides the first operand by the second operand

    Example:
        div = Division(user_id=user_id, a=100, b=5)
        result = div.get_result()  # Returns 20

    Note: This implementation uses EAFP (Easier to Ask for Forgiveness than
    Permission) by attempting division and catching the ZeroDivisionError.
    """

    __mapper_args__ = {"polymorphic_identity": "division"}

    def get_result(self) -> float:
        """
        Divide the first operand by the second operand.

        Returns:
            The result of a divided by b

        Raises:
            ValueError: If attempting to divide by zero
        """

        try:
            return self.a / self.b
        except ZeroDivisionError as exc:
            raise ValueError("Cannot divide by zero.") from exc
