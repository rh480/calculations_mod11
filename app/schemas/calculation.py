# app/schemas/calculation.py
"""
Calculation Pydantic Schemas

This module defines Pydantic schemas for validating calculation data at the
API boundary. Pydantic provides automatic validation, serialization, and
documentation generation for FastAPI.

Key Concepts:
- Schemas define the shape of data coming in/out of the API
- Validation happens automatically before data reaches your code
- Field validators provide custom validation logic
- Model validators can validate across multiple fields
- ConfigDict controls schema behavior and documentation

Design Pattern: Data Transfer Objects (DTOs)
These schemas act as DTOs, defining contracts between schemas and clients.
"""

from enum import Enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
    field_validator,
)

_TYPE_ALIASES = {
    "add": "addition",
    "sub": "subtraction",
    "subtract": "subtraction",
    "multiply": "multiplication",
    "divide": "division",
}

class CalculationType(str, Enum):
    """
    Enumeration of valid calculation types.

    Using an Enum provides:
    1. Type safety: Only valid values can be used
    2. Auto-completion: IDEs can suggest valid values
    3. Documentation: Automatically appears in OpenAPI spec
    4. Validation: Pydantic automatically rejects invalid values

    Inheriting from str makes this a string enum, so values serialize
    naturally as strings in JSON.
    """

    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"


class CalculationBase(BaseModel):
    """
    Base schema for calculation data.

    This schema defines the common fields that all calculation requests share.
    It's used as a base for more specific schemas (Create, Update, Response).

    Design Pattern: This follows the DRY (Don't Repeat Yourself) principle by
    defining common fields once and reusing them in other schemas.
    """
    type: CalculationType = Field(
        ...,
        description="Type of calculation to perform",
        examples=["addition"],
    )

    a: float = Field(
        ...,
        allow_inf_nan=False,
        description="First operand",
        examples=[10.5],
    )

    b: float = Field(
        ...,
        allow_inf_nan=False,
        description="Second operand",
        examples=[3.0],
    )

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value):
        """
        Normalize calculation types to lowercase.

        This allows values such as Addition, ADDITION, and addition.
        """
        if isinstance(value, str):
            value = value.strip().lower()
            return _TYPE_ALIASES.get(value, value)
        return value

    @model_validator(mode="after")
    def validate_division(self) -> "CalculationBase":
        """
        Prevent division by zero.

        The second operand is the denominator.
        """
        if (
            self.type == CalculationType.DIVISION
            and self.b == 0
        ):
            raise ValueError("Cannot divide by zero")

        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"type": "addition", "a": 10.5, "b": 3},
                {"type": "division", "a": 100, "b": 2},
            ]
        },
    )


class CalculationCreate(CalculationBase):
    """
    Schema for creating a new Calculation.

    This schema is used when a client wants to create a calculation.
    It includes the user_id to associate the calculation with a user.

    In a real application, the user_id would typically come from the
    authenticated user's session rather than the request body.
    """

    user_id: UUID = Field(
        ...,
        description="UUID of the user who owns this calculation",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "type": "addition",
                "a": 10.5,
                "b": 3,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        },
    )


class CalculationUpdate(BaseModel):
    """
    Schema for updating an existing Calculation.

    This schema allows clients to update the operands of an existing
    calculation. All fields are optional since partial updates are allowed.

    Note: The calculation type cannot be changed after creation. If you need
    a different type, create a new calculation.
    """

    a: Optional[float] = Field(
        None,
        allow_inf_nan=False,
        description="Updated first operand",
    )

    b: Optional[float] = Field(
        None,
        allow_inf_nan=False,
        description="Updated second operand",
    )

    model_config = ConfigDict(from_attributes=True)


class CalculationResponse(CalculationBase):
    """
    Schema for reading a Calculation from the database.

    This schema includes all the fields that are returned when reading
    a calculation, including database-generated fields like id, created_at,
    and the computed result.

    The from_attributes=True config allows this schema to be populated from
    SQLAlchemy model instances using model_validate().
    """

    id: UUID = Field(
        ...,
        description="Unique UUID of the calculation",
        examples=["123e4567-e89b-12d3-a456-426614174999"],
    )

    user_id: UUID = Field(
        ...,
        description="UUID of the user who owns this calculation",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )

    created_at: datetime = Field(
        ...,
        description="Time when the calculation was created",
    )

    updated_at: datetime = Field(
        ...,
        description="Time when the calculation was last updated",
    )

    result: float = Field(
        ...,
        description="Result of the calculation",
        examples=[15.5],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174999",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "addition",
                "a": 10.5,
                "b": 3,
                "result": 13.5,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
            }
        },
    )


class CalculationRead(BaseModel):
    """
    Schema for reading a calculation from the database.

    Uses SQLAlchemy model attributes for serialization.
    """

    id: UUID
    a: float
    b: float
    type: CalculationType
    result: Optional[float] = None
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
