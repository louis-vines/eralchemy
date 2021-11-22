from dataclasses import dataclass

import pytest

from eralchemy.dbml import (
    add_nullability,
    extract_cardinalities,
    relation_to_intermediary,
)

from tests.common import (
    ERColumn,
    Relation as ERRelation,
    Table as ERTable,
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
    col_1 = Column(name='col_a')
    col_2 = Column(name='col_b')

    class _Relation:
       def __init__(self, ref_type, col_1=col_1, col_2=col_2):
           """
           ref_type should be in values (<, >, -)
           """
           self.type = ref_type
           self.col1 = [col_1]
           self.col2 = [col_2]

    return _Relation


def test_relation_to_intermediary(Relation):
    relation = Relation('<')

    intermediary_repr = relation_to_intermediary(relation)

    assert isinstance(intermediary_repr, ERRelation)


@pytest.mark.parametrize(
    'ref_type, expected_cardinalities',
    [
        ('<', ('1', '+')),
        ('>', ('+', '1')),
        ('-', ('1', '1')),
        ('', (None, None)),
    ]
)
def test_extract_cardinalities(Relation, Column, ref_type, expected_cardinalities):
    relation = Relation(
        ref_type,
        col_1=Column('col_a', not_null=True),
        col_2=Column('col_b', not_null=True),
    )

    cardinalities = extract_cardinalities(relation)

    assert cardinalities == expected_cardinalities


@pytest.mark.parametrize(
    'ref_type, expected_cardinalities',
    [
        ('<', ('?', '*')),
        ('>', ('*', '?')),
        ('-', ('?', '?')),
        ('', (None, None)),
    ]
)
def test_extract_cardinalities_with_nullable(
        Relation, Column, ref_type, expected_cardinalities):
    relation = Relation(
        ref_type,
        col_1=Column('col_a', not_null=False),
        col_2=Column('col_b', not_null=False),
    )

    cardinalities = extract_cardinalities(relation)

    assert cardinalities == expected_cardinalities


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
