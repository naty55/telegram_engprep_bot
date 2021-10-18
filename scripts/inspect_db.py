import pandas as pd
import sqlite3

conn = sqlite3.connect("../test.db")
while (table_name := input("Select table name to show\n>>>")) != 'q':
    df = pd.read_sql(f'select * from {table_name}', conn)
    print(df)
