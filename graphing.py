# Takes sql data and graphs it

from statement_to_sql import DbConnection
import pandas as pd
from flask import Flask, render_template, Response
import matplotlib.pyplot as plt
import io
import base64
from private import spend_limit


# Next.
# / Write function to extract data from sql 
# plot monthly spend on a line graph. 
# create new sql table for daily spend 
# plot this data according to sketches


class PullFromSql(DbConnection):
    def __init__(self, host_name, user_name, db_name) -> None:
        super().__init__(host_name, user_name, db_name)

    def get_data(self):
        self.create_db_connection()
        cursor = self.connection.cursor()
        
        query = "SELECT * FROM Overview"

        cursor.execute(query)

        # Fetch all rows and column names
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        # Convert the data into a pandas DataFrame
        self.db = pd.DataFrame(rows, columns=columns)
        
        # Close the cursor and connection
        cursor.close()
        self.connection.close()

        return self.db

class Plotting():
    def __init__(self, data) -> None:
        self.db = data


    def plot_spend(self):
        """
        Plots a line graph of monthly spending.

        Parameters:
        - data (pd.DataFrame): DataFrame containing 'Month' and 'Amount (£)' columns.
        """
        try:
            # # Ensure the 'Month' column is in datetime format for proper sorting
            # data['Month'] = pd.to_datetime(data['Month'], format='%Y-%m')
            
            # # Sort the data by month (if not already sorted)
            # data = data.sort_values('Month')
            
            monthly_spend = []
            for _, value in enumerate(self.db['total_out']):
                monthly_spend.append(value*-1)

            # Plot the data
            plt.figure(figsize=(10, 6))
            plt.plot(self.db['month'], monthly_spend, marker='o', linestyle='-', linewidth=2)
            plt.axhline(y=spend_limit, color='red', linestyle='--', label=f"Spend limit: {spend_limit}")  # Add 'spend limit' line
            plt.title("Monthly Spending", fontsize=16)
            plt.xlabel("Month", fontsize=14)
            plt.ylabel("Amount Spent (£)", fontsize=14)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"An error occurred while plotting: {e}")




# class Plotting():
#     def __init__(self) -> None:
#         pass

#     app = Flask(__name__)

#     def chart_one():
#         # Calculate spending and saved values in one line each
#         spending = -money['spending']['total']
#         saved = sum(money[category]['total'] for category in ['income', 'spending', 'recurring', 'holiday', 'other'])

#         # Calculate percentages
#         total = spending + saved
#         spending_val = (spending / total) * 100
#         saved_val = (saved / total) * 100

#         # data for pie chart
#         labels = [f'Spending, £{spending}', f'Saved, £{saved}']
#         sizes = [spending_val, saved_val]  # The percentages for each category
#         colors = ['blue', 'orange']
#         explode = (0.1, 0)  # 'explode' the 2nd slice

#         # Generate the pie chart
#         img = io.BytesIO()
#         plt.figure(figsize=(6, 4))
#         plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
#         plt.title("Spending Chart")
#         plt.savefig(img, format='png')
#         img.seek(0)

#         # Encode the plot as a base64 string
#         plot_url = base64.b64encode(img.getvalue()).decode()
#         plt.close()  # Close the plot to free memory

#         return plot_url

#     @app.route('/')
#     def index():
#         plot_url1 = chart_one()
#         plot_url2 = chart_two()

#         # Render both charts on the same page
#         return f'''
#             <h1>Finance_tracker.py</h1>
#             <h2>Spend vs Save</h2>
#             <img src="data:image/png;base64,{plot_url1}">
#             <h2>Spending Breakdwon</h2>
#             <img src="data:image/png;base64,{plot_url2}">
#         '''

def main():
    instance = PullFromSql('localhost', 'root', 'finance_tracker')
    db = instance.get_data()
    # print(db.head())

    plots = Plotting(db)
    plots.plot_spend()


if __name__ == "__main__":
    main()
    # app.run(debug=True)