# -*- coding: utf-8 -*-
"""School Dashboard - SQLite Database manipulation functions

Functions:

@Author: Krzysztof Kordal, Michał Święciło
@Date: 2023.06
"""

# Built-in
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn