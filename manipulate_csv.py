import pandas as pd
from private import nov_data,landlord,employer, filter_credit_card, find_insurance

# Data structure to extract to
money = {
    'income':{
        'total': None,
        'payroll': None,
        'transfers': None,
    },

    'recurring':{
        'rent': None,
        'insurance': None,
        'gym': None,
    },

    'spending':{
        'groceries': None,
        'dining_out': None,
        'entertainment': None,
        'general': None,
        'hobbies': None,
        'transport': None,
        'shopping': None,
        'other': None
    },

    'holiday':{
        'general': None
    },

    'other': {
        'credit_card_payments': None
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
def main():
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


    print(data_frame['Name'])
    # print(money)


# Once all basic filtering complete
# 1 - use openAI or eqv to to match categories.
# 2 - push all into SQL
# 3 - do some visulaisation of key stats vs goals
# 4 - introduce recipt machine vision 
# 5 - run on a server so i can just email (or alternative) interactions.

if __name__ == "__main__":
    main()
