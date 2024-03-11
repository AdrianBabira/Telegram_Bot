from typing import Dict, List, TypeVar, Any
from database.common.models import db_sqlite

T = TypeVar("T")


def _store_data(sdb: db_sqlite, model: T, *data: List[Dict]) -> None:
    with sdb.atomic():
        model.insert_many(*data).execute()


def _retrieve_all_data(sdb: db_sqlite, model: T, *columns: Any) -> Any:
    with sdb.atomic():
        response = model.select(*columns)

    return response


def _check_if_data_exists(sdb: db_sqlite, model: T, *query: Any, **filters: Any) -> bool:
    exists = True
    try:
        with sdb.atomic():
            instance = model.get_or_none(*query, **filters)
            if instance is None:
                exists = False
    except model.DoesNotExist:
        exists = False
    return exists


class CRUDInterface:
    @staticmethod
    def store():
        return _store_data

    @staticmethod
    def retrieve():
        return _retrieve_all_data

    @staticmethod
    def check_if_data_exists():
        return _check_if_data_exists


if __name__ == "__main__":
    CRUDInterface()
