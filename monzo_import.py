import pandas as pd
from private import landlord,employer, filter_credit_card, find_insurance

from pydantic import BaseModel
from openai import OpenAI

class MonzoStatement:
    def __init__(self, path) -> None:
        self.path = path
    # Data structure to extract to
        self.money = {
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
        self.extract_from_statement()


    def extract_from_statement(self):
        self.load_csv(self.path)
        # removes pot transfers from df
        self.data = self.data[self.data['Type'] != 'Pot transfer']

        # removes from db and extracts credit card payments
        self.data, cc_payments = filter_credit_card(self.data)
        self.money['other']['credit_card_payments'] = cc_payments

        self.find_rent()
        # Removed from db and extracts rent payment
        self.money['recurring']['rent'] = self.rent

        # Removed from db and extracts insurance payment
        self.data, insurance = find_insurance(self.data)
        self.money['recurring']['insurance'] = insurance

        self.find_holiday()
        self.money['holiday']['general'] = self.holiday_spend

        self.find_payroll()
        self.money['income']['payroll'] = self.payroll

        self.find_transfers_in()
        self.money['income']['transfers'] = self.transfers

        # Run AI category allocation on remaining payments
        self.sort_spending()

        # populates the 'total' fields in money
        self.sum_totals()



    def load_csv(self, file_path) -> pd.DataFrame:
        # Load the CSV file into a DataFrame
        try:
            self.data = pd.read_csv(file_path)
            self.orignial_data = pd.read_csv(file_path)
            self.data.rename(columns={'Notes and #tags': 'Notes'}, inplace=True)
            print("CSV loaded successfully!")
            return self.data
        except FileNotFoundError:
            print("The file was not found. Please check the file path.")
        except pd.errors.EmptyDataError:
            print("The file is empty.")
        except pd.errors.ParserError:
            print("There was an error parsing the file.")

    def find_rent(self):
        """Filters db to remove rent and returns the rent payment"""
        rent = self.data[(self.data['Type'] == 'Faster payment') & 
                        (self.data['Name'] == f'{landlord}') & 
                        (self.data['Description'].str.contains('Rent', na=False))]
        self.rent = rent['Amount'].sum()

        # Filters df to remove rent payment
        self.data = self.data[~((self.data['Type'] == 'Faster payment') & 
                                (self.data['Name'] == f'{landlord}') & 
                                (self.data['Notes'].str.contains('M3 Rent', na=False)))]
        return self.rent

    def find_holiday(self):
        """Filters db to remove holiday spending and returns the total spent"""
        self.holiday_spend = 0

        payments = self.data[~((self.data['Local currency'] == 'GBP'))]
        if not payments.empty:  # Check if the DataFrame is not empty
            for i, payment in enumerate(payments.itertuples()):  # Use itertuples for iteration
                self.holiday_spend += payment.Amount  # Access Amount directly from the tuple

        # Filters for all payments made in GBP
        self.data = self.data[((self.data['Local currency'] == 'GBP'))]

        return self.holiday_spend

    def find_payroll(self):
        payroll = self.data[(self.data['Name'] == f'{employer}')]
        self.payroll = payroll['Amount'].sum()

        self.data = self.data[~(self.data['Name'] == f'{employer}')]
        return self.payroll

    def find_transfers_in(self):
        """Return the amount recieved in transfers & the filtered db"""
        self.transfers = 0

        payments = self.data[((self.data['Category'] == 'Income'))]
        if not payments.empty:  # Check if the DataFrame is not empty
            for i, payment in enumerate(payments.itertuples()):  # Use itertuples for iteration
                self.transfers += payment.Amount  # Access Amount directly from the tuple

        self.data = self.data[~((self.data['Category'] == 'Income'))]

        return self.transfers

    def sort_spending(self):
        """goes through db payment by payment and allocates a category"""
        # iterate over payments in db
        for i, payment in enumerate(self.data.itertuples()):
            # get info passing on
            _type = payment.Type
            name = payment.Name
            notes = payment.Notes

            category = self.category_sort(name, _type, notes)

            self.money['spending'][category] += payment.Amount

    def category_sort(self, name, _type, notes): 
        client = OpenAI()

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
    
    def sum_totals(self):
        # Calculate the sum of all values except 'total'
        self.money['income']['total'] = sum(value for key, value in self.money['income'].items() if key != 'total')


        # Calculate the sum of all values except 'total'
        self.money['spending']['total'] = sum(value for key, value in self.money['spending'].items() if key != 'total')


        # Calculate the sum of all values except 'total'
        self.money['recurring']['total'] = sum(value for key, value in self.money['recurring'].items() if key != 'total')


        # Calculate the sum of all values except 'total'
        self.money['holiday']['total'] = sum(value for key, value in self.money['holiday'].items() if key != 'total')


        # Calculate the sum of all values except 'total'
        self.money['other']['total'] = sum(value for key, value in self.money['other'].items() if key != 'total')





def main():
    # november = MonzoStatement(nov_data)
    # print(november.money)
    pass


if __name__ == "__main__":
    main()