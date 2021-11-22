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
    print('not_null:', column.not_null)
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
