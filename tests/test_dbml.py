from dataclasses import dataclass

import pytest

from eralchemy.dbml import (
    add_nullability,
    extract_cardinalities,
)


@pytest.fixture
def Column():
    @dataclass
    class _Column:
        name: str = 'col_a'
        not_null: bool = False
        pk: bool = False

    return _Column



@pytest.fixture
def Relation(Column):
    col_a = Column(name='col_a')
    col_b = Column(name='col_b')
    class _Relation:
       def __init__(self, col1=col_a, col2=col_b):
           self.col1 = [col_a]
           self.col2 = [col_b]

    return _Relation


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


@pytest.mark.parametrize(
    'pk, cardinality, expected_cardinality',
    [
        (True, '+', '+'),
        (True, '1', '1'),
        (False, '+', '*'),
        (False, '1', '?'),
    ]
)
def test_add_nullability_can_use_primary_key_as_nullable_check(
        Column, pk, cardinality, expected_cardinality):
    column = Column(pk=pk)

    cardinaliry_with_nulls = add_nullability(column, cardinality)

    assert cardinaliry_with_nulls == expected_cardinality


def test_extract_cardinalities(Relation):
    relation = Relation()

    cardinalities = extract_cardinalities(relation)
    expected_cardinalities = ('1', '+')

    assert cardinalities == expected_cardinalities
