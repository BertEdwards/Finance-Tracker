import mysql.connector
import csv
import os





def do_export(table_name, db):
    user_password = os.getenv("MYSQL_PASSWORD")

    # MySQL connection configuration
    config = {
        'user': 'root',  # Replace with your MySQL username
        'password': user_password,  # Replace with your MySQL password
        'host': 'localhost',
        'database': db,  # Replace with your database name
    }

    # Connect to MySQL database
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    # SQL query to fetch data from the table
    query = f"SELECT * FROM {table_name};"

    # Execute the query
    cursor.execute(query)

    # Fetch all rows from the query result
    rows = cursor.fetchall()

    # Get the column headers
    column_headers = [i[0] for i in cursor.description]

    # Specify the CSV file path
    csv_file_path = f"{table_name}.csv"

    # Write data to CSV file
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write the column headers
        writer.writerow(column_headers)
        
        # Write the rows
        writer.writerows(rows)

    # Close the cursor and connection
    cursor.close()
    connection.close()

    print(f"Data from table '{table_name}' has been exported to '{csv_file_path}'")

# The specific table you want to export
# table_name = 'variants'  # Replace with the name of the table you want to export
# do_export('products')

if __name__ == "__main__": 
    pass
