import pandas as pd
from paths import nov_data,landlord, filter_credit_card

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
    rent = rent['Amount'].sum()  # Assuming 'Money Out' contains the amounts

    # Filters df to remove rent payment
    data_frame = data_frame[~((data_frame['Type'] == 'Faster payment') & 
                              (data_frame['Name'] == f'{landlord}') & 
                              (data_frame['Notes and #tags'].str.contains('M3 Rent', na=False)))]
    return data_frame, rent



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


    print(data_frame['Type'])


if __name__ == "__main__":
    main()
