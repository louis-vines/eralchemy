from pathlib import Path

from pydbml import PyDBML

from eralchemy.models import  Column, Relation, Table
from eralchemy.sqla import format_name, format_type


def dbml_file_to_intermediary(filepath):
    """Parses a .dbml file and returns intermediary syntax"""
    parsed = PyDBML(Path(filepath))
    return pydbml_to_intermediary(parsed)


def pydbml_to_intermediary(pydbml_obj):
    """Converts parsed pydbml object to intermediary representation"""
    tables = [table_to_intermediary(table) for table in pydbml_obj.tables]
    relations = [
        relation_to_intermediary(relation)
        for relation in pydbml_obj.refs
    ]
    return tables, relations


def table_to_intermediary(table):
    """Convert pydbml table to intermediary representation"""
    columns = [column_to_intermediary(column) for column in table.columns]
    return Table(
        name=table.name,
        columns=columns,
    )


def column_to_intermediary(column, type_formatter=format_type):
    return Column(
        name=column.name,
        type=type_formatter(column.type),
        is_key=column.pk,
    )


def relation_to_intermediary(relation):
    left_cardinality, right_cardinality = extract_cardinalities(relation)

    return  Relation(
        left_col=format_name(relation.table1.name),
        right_col=format_name(relation.table2.name),
        left_cardinality=left_cardinality,
        right_cardinality=right_cardinality,
    )

def extract_cardinalities(relation):
    """Get intermediary cardinality represenation from pydbml relation"""
    columns = (relation.col1[0], relation.col2[0])
    cardinalities = _CARDINALITY_LOOKUP[relation.type]

    return tuple(
        add_nullability(column, cardinality)
        for column, cardinality in zip(columns, cardinalities)
    )


def add_nullability(column, cardinality):
    """Incorporate nullability into intermediary cardinality represenation"""
    if column.not_null or column.pk:
        return cardinality

    return _NULLABLE_CARDINALITY_LOOKUP[cardinality]


_CARDINALITY_LOOKUP = {
    '<': ('1', '+'),
    '>': ('+', '1'),
    '-': ('1', '1'),
    '': (None, None)
}

_NULLABLE_CARDINALITY_LOOKUP = {
    '+': '*',
    '1': '?',
    None: None,
}
