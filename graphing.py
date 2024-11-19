# Takes sql data and graphs it

# Next.
# Write function to extract data from sql
# plot monthly spend on a line graph. 
# create new sql table for daily spend 
# plot this data according to sketches

class DbConnection():
    def __init__(self, db_config) -> None:
        self.db_config = db_config

        self._create_db_connection()


    # connecting to mysql server
    def _create_db_connection(self):
        """ Creates connection to mysql database"""
        self.db_connection = None
        self.db_cursor = None
        try:
            self.db_connection = mysql.connector.connect(**self.db_config)
            self.db_cursor = self.db_connection.cursor()
        except Error as err:
            # logger.error(f"Error: '{err}'", exc_info=True)
            print(f'Failed, {err}')
        return self.db_connection, self.db_cursor

# from flask import Flask, render_template, Response
# import matplotlib.pyplot as plt
# import io
# import base64

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




# if __name__ == "__main__":
#     main()
#     app.run(debug=True)