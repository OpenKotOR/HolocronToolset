"""Re-export reference field config from PyKotor for backward compatibility."""

from __future__ import annotations

from pykotor.tools.reference_config import (
    CONVERSATION_FIELDS,
    CONVERSATION_FIELD_TYPES,
    DLG_CONDITION_PATHS,
    DLG_SCRIPT_PATHS,
    ITEMLIST_FIELDS,
    ITEMLIST_FIELD_TYPES,
    SCRIPT_FIELDS,
    SCRIPT_FIELD_TYPES,
    TAG_FIELDS,
    TAG_FIELD_TYPES,
    TEMPLATE_RESREF_FIELDS,
    TEMPLATE_RESREF_FIELD_TYPES,
    get_all_searchable_file_types,
    get_conversation_fields_for_type,
    get_itemlist_fields_for_type,
    get_script_fields_for_type,
    get_tag_fields_for_type,
    get_template_resref_fields_for_type,
)

__all__ = [
    "CONVERSATION_FIELDS",
    "CONVERSATION_FIELD_TYPES",
    "DLG_CONDITION_PATHS",
    "DLG_SCRIPT_PATHS",
    "ITEMLIST_FIELDS",
    "ITEMLIST_FIELD_TYPES",
    "SCRIPT_FIELDS",
    "SCRIPT_FIELD_TYPES",
    "TAG_FIELDS",
    "TAG_FIELD_TYPES",
    "TEMPLATE_RESREF_FIELDS",
    "TEMPLATE_RESREF_FIELD_TYPES",
    "get_all_searchable_file_types",
    "get_conversation_fields_for_type",
    "get_itemlist_fields_for_type",
    "get_script_fields_for_type",
    "get_tag_fields_for_type",
    "get_template_resref_fields_for_type",
]
