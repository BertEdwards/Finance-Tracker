# file to take monthly staments and writing to sql
import mysql.connector
from mysql.connector import Error
import os
from monzo_import import MonzoStatement
from private import nov_data

#for testing 
from sql_to_csv import do_export


# Define write to sql class
    # Function to take 'money' and write to sql

# Define fetching from sql class
    # function to fetch data so can be graphed.

class DbConnection():
    def __init__(self, host_name, user_name, db_name) -> None:
        self.host_name = host_name
        self.user_name = user_name
        self.user_password = os.getenv("MYSQL_PASSWORD")
        self.db_name = db_name

    # connecting to mysql server
    def _create_db_connection(self):
        """ Creates connection to mysql database"""
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=self.host_name,
                user=self.user_name,
                passwd=self.user_password,
                database=self.db_name
            )
        except Error as err:
            pass
            # logger.error(f"Error: '{err}'", exc_info=True)
        return self.connection
    
    def execute_query(self, query, params=None):
        """ Execute a query to the mysql database"""
        self._create_db_connection()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
        except Error as err:
            pass
            # logger.error(f"Error: '{err}'", exc_info=True)


class WriteMonthlyData(DbConnection):
    def __init__(self, host_name, user_name, db_name, money) -> None:
        super().__init__(host_name, user_name, db_name)
        self.money = money

    def write_to_overview(self, month, year):

        month = month.strip()
        # Creates a unique value for the entry in the db to prevent duplication
        date_hash = f"{month.lower()}{year}"
        total_in = self.money['income']['total']
        total_out = self.money['recurring']['total'] + self.money['spending']['total'] + self.money['holiday']['total'] + self.money['other']['total']

        params = {
            'year': year,
            'month': month,
            'date_hash': date_hash,
            'total_in': total_in,
            'total_out': total_out
        }

        query = """
        INSERT INTO Overview 
        (year, month, date_hash, total_in, total_out)
        VALUES ( %(year)s, %(month)s, %(date_hash)s, %(total_in)s, %(total_out)s)

        """

        self.execute_query(query, params)

def main():
    # november = MonzoStatement(nov_data)
    # november.money
    # nov_write = WriteMonthlyData("localhost", "root", "finance_tracker", november.money)
    # nov_write.write_to_overview("october", 2024)

    do_export("Overview", "finance_tracker")



if __name__ == "__main__":
    main()
    






