from dataclasses import dataclass
import os
from pathlib import Path

from pydbml import PyDBML
import pytest

from eralchemy.dbml import (
    add_nullability,
    column_to_intermediary,
    extract_cardinalities,
    relation_to_intermediary,
)

from tests.common import (
    ERColumn,
    Relation as ERRelation,
    Table as ERTable,
)


current_folder, _ = os.path.split(__file__)


@pytest.fixture(scope='module')
def dbml():
    fixture_filename = os.path.join(current_folder, 'fixtures', 'example.dbml')
    return PyDBML(Path(fixture_filename))


@pytest.fixture
def Column():
    @dataclass
    class _Column:
        name: str = 'col_a'
        type: str = 'a_type'
        not_null: bool = False
        pk: bool = False

    return _Column


@pytest.fixture
def Relation(Column):
    col_1 = Column(name='col_a')
    col_2 = Column(name='col_c')

    class _Relation:
       def __init__(
                self, ref_type, col_1=col_1, col_2=col_2):
            """
            ref_type should be in values (<, >, -)
            """
            self.type = ref_type
            self.col1 = [col_1]
            self.col2 = [col_2]

    return _Relation


def test_column_to_intermediary(Column):
    column = Column()

    intermediary_col = column_to_intermediary(column)

    assert isinstance(intermediary_col, ERColumn)
    assert intermediary_col.name =='col_a'
    assert intermediary_col.type == 'a_type'
    assert not intermediary_col.is_key


@pytest.mark.parametrize(
    'ith_ref, l_col, r_col, l_card, r_card',
    [
        (0, 'dim_contract_details', 'fct_contract_signed', '1', '*'),  # <
        (1, 'fct_contract_signed', 'dim_foo', '*', '1'),  # >
        (2, 'dim_bar', 'fct_contract_signed', '1', '?'),  # -
    ]
)
def test_relation_to_intermediary(dbml, ith_ref, l_col, r_col, l_card, r_card):
    relation = dbml.refs[ith_ref]

    intermediary_relation = relation_to_intermediary(relation)

    assert isinstance(intermediary_relation, ERRelation)
    assert intermediary_relation.left_col == l_col
    assert intermediary_relation.right_col == r_col
    assert intermediary_relation.left_cardinality == l_card
    assert intermediary_relation.right_cardinality == r_card


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
