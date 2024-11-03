import pandas as pd
from paths import nov_data

# Data structure to extract to
to_extract = {
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





def main():
    # Load in Novemeber csv banking data
    data_frame = load_csv(nov_data)

    if data_frame is not None:
        print(data_frame.head())

if __name__ == "__main__":
    main()
