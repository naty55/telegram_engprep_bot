from db_api import DataBase


if __name__ == '__main__':
    db = DataBase()
    db.push("Hello", "שלום")
    db.rate("Hello", 1)
    db.delete("Hello")