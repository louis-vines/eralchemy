def add_nullability(column, cardinality):
    """Incorporate nullability into intermediary cardinality represenation"""
    if column.not_null or column.pk:
        return cardinality

    return _NULLABLE_CARDINALITY_LOOKUP[cardinality]


_NULLABLE_CARDINALITY_LOOKUP = {
    '+': '*',
    '1': '?',
    None: None,
}
