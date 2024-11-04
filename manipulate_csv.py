import pandas as pd
from private import nov_data,landlord,employer, filter_credit_card, find_insurance

from pydantic import BaseModel
from openai import OpenAI
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-GUI rendering

from flask import Flask, render_template, Response
import matplotlib.pyplot as plt
import io
import base64

client = OpenAI()

# Data structure to extract to
money = {
    'income':{
        'total': 0,
        'payroll': 0,
        'transfers': 0,
    },

    'recurring':{
        'total': 0,
        'rent': 0,
        'insurance': 0,
        'gym': 0,
    },

    'spending':{
        'total': 0,
        'groceries': 0,
        'dining_out': 0,
        'entertainment': 0,
        'general': 0,
        'hobbies': 0,
        'transport': 0,
        'shopping': 0,
        'other': 0
    },

    'holiday':{
        'total': 0,
        'general': 0
    },

    'other': {
        'total': 0,
        'credit_card_payments': 0
    }
}

def load_csv(file_path):
    # Load the CSV file into a DataFrame
    try:
        data = pd.read_csv(file_path)
        print("CSV loaded successfully!")
        return data
    except FileNotFoundError:
        print("The file was not found. Please check the file path.")
    except pd.errors.EmptyDataError:
        print("The file is empty.")
    except pd.errors.ParserError:
        print("There was an error parsing the file.")


# Removes from statement
def remove_pot_transfers(data_frame):
    # Remove entries where 'Type' is 'Pot transfer'
    return data_frame[data_frame['Type'] != 'Pot transfer']

def find_rent(data_frame):
    """Return the amount of rent paid & the filtered db"""
    rent = data_frame[(data_frame['Type'] == 'Faster payment') & 
                      (data_frame['Name'] == f'{landlord}') & 
                      (data_frame['Description'].str.contains('Rent', na=False))]
    rent = rent['Amount'].sum()

    # Filters df to remove rent payment
    data_frame = data_frame[~((data_frame['Type'] == 'Faster payment') & 
                              (data_frame['Name'] == f'{landlord}') & 
                              (data_frame['Notes and #tags'].str.contains('M3 Rent', na=False)))]
    return data_frame, rent

def find_holiday(data_frame):
    """Return the amount spent abroad & the filtered db"""
    holiday_spend = 0

    # Filters for all payments made in GBP
    filtered_db = data_frame[((data_frame['Local currency'] == 'GBP'))]

    payments = data_frame[~((data_frame['Local currency'] == 'GBP'))]
    if not payments.empty:  # Check if the DataFrame is not empty
        for i, payment in enumerate(payments.itertuples()):  # Use itertuples for iteration
            holiday_spend += payment.Amount  # Access Amount directly from the tuple

    return filtered_db, holiday_spend

def find_payroll(data_frame):
    payroll = data_frame[(data_frame['Name'] == f'{employer}')]
    payroll = payroll['Amount'].sum()

    data_frame = data_frame[~(data_frame['Name'] == f'{employer}')]
    return data_frame, payroll

def find_transfers_in(data_frame):
    """Return the amount recieved in transfers & the filtered db"""
    transfers = 0

    # Filters for all payments made in GBP
    filtered_db = data_frame[~((data_frame['Category'] == 'Income'))]

    payments = data_frame[((data_frame['Category'] == 'Income'))]
    if not payments.empty:  # Check if the DataFrame is not empty
        for i, payment in enumerate(payments.itertuples()):  # Use itertuples for iteration
            transfers += payment.Amount  # Access Amount directly from the tuple

    return filtered_db, transfers

# rename to filtering
def filter_db():
    # Load in Novemeber csv banking data
    data_frame = load_csv(nov_data)

    data_frame = remove_pot_transfers(data_frame)

    # removes from db and extracts credit card payments
    data_frame, cc_payments = filter_credit_card(data_frame)
    money['other']['credit_card_payments'] = cc_payments

    # Removed from db and extracts rent payment
    data_frame, rent = find_rent(data_frame)
    money['recurring']['rent'] = rent

    # Removed from db and extracts insurance payment
    data_frame, insurance = find_insurance(data_frame)
    money['recurring']['insurance'] = insurance

    # Removed from db and extracts holiday payments
    data_frame, holiday = find_holiday(data_frame)
    money['holiday']['general'] = holiday

    # Identify income 
    # payroll 
    data_frame, payroll = find_payroll(data_frame)
    money['income']['payroll'] = payroll
    # transfers

    # split general spending into categories
    data_frame, transfers = find_transfers_in(data_frame)
    money['income']['transfers'] = transfers

    data_frame.rename(columns={'Notes and #tags': 'Notes'}, inplace=True)

    return data_frame

def sort_spending(data_frame):
    """goes through db payment by payment and allocates a category"""
    # iterate over payments in db
    for i, payment in enumerate(data_frame.itertuples()):
        # get info passing on
        _type = payment.Type
        name = payment.Name
        notes = payment.Notes

        category = category_sort(name, _type, notes)

        # print('////////////////')
        # print(f"type: {_type}, name: {name}, notes: {notes}")
        # print(f"category: {category}")

        money['spending'][category] += payment.Amount

        # print(payment.Amount)

        # print(data_frame.columns)

        # make the open AI request
        # store the info

    # feed openAI relevant info

    # get back a category (from predefined list)

    # Add that payment to category total

def main():
    data_frame = filter_db()
    sort_spending(data_frame)

    # Calculate the sum of all values except 'total'
    income_sum = sum(value for key, value in money['income'].items() if key != 'total')
    # store this sum in 'total' key
    money['income']['total'] = income_sum

    # Calculate the sum of all values except 'total'
    spending_sum = sum(value for key, value in money['spending'].items() if key != 'total')
    # store this sum in 'total' key
    money['spending']['total'] = spending_sum

    # Calculate the sum of all values except 'total'
    recurring_sum = sum(value for key, value in money['recurring'].items() if key != 'total')
    # store this sum in 'total' key
    money['recurring']['total'] = recurring_sum

    # Calculate the sum of all values except 'total'
    holiday_sum = sum(value for key, value in money['holiday'].items() if key != 'total')
    # store this sum in 'total' key
    money['holiday']['total'] = holiday_sum

    # Calculate the sum of all values except 'total'
    other_sum = sum(value for key, value in money['other'].items() if key != 'total')
    # store this sum in 'total' key
    money['other']['total'] = other_sum


    # print(money)


def category_sort(name, _type, notes): 

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content":  """You are a financial assistant. I have a list of predefined spending categories:
                    'groceries', 'dining_out', 'entertainment', 'general', 'hobbies', 'transport', 'shopping', and 'other'.
                        Given a product or spending description, please match it to the most appropriate category from this list and return only the single category name.
                    """},
            {
                "role": "user",
                "content": f"What category should be applied to a payment with Name: {name}, type: {_type}, and notes: {notes}"
            }
        ]
    )

    category = completion.choices[0].message.content.strip().split(',')

    return category[0]

### Plotting
# for chart one
# spending = -1*money['spending']['total'] 
# saved = money['income']['total'] - money['spending']['total'] - money['recurring']['total'] - money['holiday']['total'] - money['other']['total']

# spending_val = (spending / (spending + saved)) * 100
# saved_val = (saved / (spending + saved)) * 100


app = Flask(__name__)

def chart_one():
    # Calculate spending and saved values in one line each
    spending = -money['spending']['total']
    saved = sum(money[category]['total'] for category in ['income', 'spending', 'recurring', 'holiday', 'other'])

    # Calculate percentages
    total = spending + saved
    spending_val = (spending / total) * 100
    saved_val = (saved / total) * 100

    # data for pie chart
    labels = [f'Spending, £{spending}', f'Saved, £{saved}']
    sizes = [spending_val, saved_val]  # The percentages for each category
    colors = ['blue', 'orange']
    explode = (0.1, 0)  # 'explode' the 2nd slice

    # Generate the pie chart
    img = io.BytesIO()
    plt.figure(figsize=(6, 4))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title("Spending Chart")
    plt.savefig(img, format='png')
    img.seek(0)

    # Encode the plot as a base64 string
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()  # Close the plot to free memory

    return plot_url


@app.route('/')
def index():
    plot_url1 = chart_one()

    return f'<img src="data:image/png;base64,{plot_url1}">'


# Once all basic filtering complete
# 1 - use openAI or eqv to to match categories.
# 2 - push all into SQL- every time something is filtered out of db: push to SQL
# 3 - do some visulaisation of key stats vs goals - split by size of supermarket
# 4 - introduce recipt machine vision 
# 5 - run on a server so i can just email (or alternative) interactions.

if __name__ == "__main__":
    main()
    app.run(debug=True)


    # name = 'Transport for London'
    # _type = 'Card payment'
    # notes = 'Travel charge for Wednesday, 16 Oct'

    # bob = category_sort(name, _type, notes)

    # print(bob)

