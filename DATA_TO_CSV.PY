import requests  # This is used to send requests to get data from a website (API).
import pandas as pd  # This helps us work with data easily, like making tables.
import os  # This helps us work with the computer's file system.
from API_KEYS import api_keys  # This imports a list of API keys from a separate file.
from API_ENDPOINTS import endpoints  # This imports a list of API endpoints from a separate file.

# This class handles everything related to getting data from the API and saving it to a CSV file.
class ApiDataExporter:
    
    # This is what happens when we create an instance of the class. We set up some starting information.
    def __init__(self, base_url, endpoint, per_page=100):
        self.base_url = base_url  # The website's address where we want to get data.
        self.endpoint = endpoint  # The specific section of the website we're asking for data.
        self.url = base_url + endpoint  # The full address we'll be using to get data.
        self.per_page = per_page  # How many data items we want to get each time we ask.
        self.api_keys = api_keys  # Our list of keys to access the API.
        self.current_api_key_index = 0  # Start by using the first API key.

    # This function asks for one page of data from the API.
    def fetch_page(self, page):
        params = {'per_page': self.per_page, 'page': page, 'api_key': self.api_keys[self.current_api_key_index]}
        try:
            # Send the request to the API with the given parameters (like page number and API key).
            response = requests.get(self.url, params=params)
            # If the request fails, this will raise an error.
            response.raise_for_status()
            # Convert the response (usually in JSON) to a Python dictionary.
            return response.json()
        except requests.RequestException as e:
            # If there's an error, we print it and return nothing (None).
            print(f"Request error: {e}")
            return None

    # This function gets all the pages of data by looping through each one.
    def fetch_all_pages(self):
        all_data = []  # This will hold all the data we get.
        page = 1  # Start with page 1.
        
        # We keep asking for more pages of data until there are no more pages.
        while True:
            data = self.fetch_page(page)  # Get data from the current page.
            if data and 'results' in data:
                # If there are results, we get the data.
                fetched_data = data['results']
                if not fetched_data:
                    # If the results are empty, that means we're done.
                    break
                all_data.extend(fetched_data)  # Add this page's data to our list of all data.
                print(f"Fetched {len(fetched_data)} records from page {page}. Total records: {len(all_data)}")
                page += 1  # Move to the next page.
                
                # If we've collected 3000 or more items, stop collecting more.
                if len(all_data) >= 150:
                    break
            else:
                # If there's no data or an error, stop the process.
                print("No data or error in response.")
                break

        return all_data  # Return all the data we've collected.

    # This function saves the collected data into a CSV file.
    def save_to_csv(self, all_data):
        # Create a DataFrame, which is like a table, from the data we got.
        df = pd.DataFrame(all_data)
        # Create the file name based on the API endpoint we're using.
        file_name = self.format_filename(self.endpoint) + '.csv'
        # This is the folder where we'll save the CSV file.
        directory = 'C:/Users/nassa/OneDrive/Desktop/FECDATAPULLTOEXCEL/CSV_FILES_OF_FEC/'
        # Create the full path (folder + file name) for saving the file.
        file_path = os.path.join(directory, file_name)

        # If the folder doesn't exist yet, create it.
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory '{directory}' created.")

        # Save the data as a CSV file.
        df.to_csv(file_path, index=False)
        print(f"Data saved to file '{file_path}'.")

    # This function creates a nice file name by replacing special characters in the endpoint name.
    @staticmethod
    def format_filename(endpoint):
        return endpoint.replace('/', '_').replace('?', '_').replace('&', '_')

    # This is the main function that runs the whole process: fetch data and save it.
    def run(self):
        all_data = self.fetch_all_pages()  # Get all the data from the API.
        if all_data:
            # If we got data, save it to a CSV file.
            self.save_to_csv(all_data)
        else:
            # If no data was fetched, print an error message.
            print(f"No data fetched for endpoint '{self.endpoint}'.")

# This is the main part of the program that runs everything.
def main():
    base_url = "https://api.open.fec.gov/v1/"  # The base URL for the API.
    
    # Loop through all the endpoints we want to get data from.
    for endpoint in endpoints:
        exporter = ApiDataExporter(base_url, endpoint)  # Create an instance of the exporter class for this endpoint.
        exporter.run()  # Run the exporter to fetch data and save it.

# If this file is run directly (not imported as a module), run the main function.
if __name__ == "__main__":
    main()
