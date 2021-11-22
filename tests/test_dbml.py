from dataclasses import dataclass

import pytest

from eralchemy.dbml import add_nullability


@pytest.fixture
def Column():
    @dataclass
    class _Column:
        not_null: bool = False
        pk: bool = False

    return _Column


@pytest.mark.parametrize(
    'not_null, cardinality, expected_cardinality',
    [
        (True, '+', '+'),
        (True, '1', '1'),
        (False, '+', '*'),
        (False, '1', '?'),
    ]
)
def test_add_nullability(Column, not_null, cardinality, expected_cardinality):
    column = Column(not_null=not_null)

    cardinaliry_with_nulls = add_nullability(column, cardinality)

    assert cardinaliry_with_nulls == expected_cardinality
