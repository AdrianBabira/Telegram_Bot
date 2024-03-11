from database.utils.CRUD import CRUDInterface


crud = CRUDInterface()

if __name__ == "__main__":
    check_func = crud.check_if_data_exists()
