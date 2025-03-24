import pandas as pd
import sys
from ContactScraper import ContactScraper

def process_urls(start_row: int, end_row: int):
    # Read the CSV file
    df = pd.read_csv('output.csv')

    # Initialize the ContactScraper
    scraper = ContactScraper()

    # Lists to store results
    contact_details = []
    failed_urls = []

    # Process each row in the specified range
    for index, row in df.iloc[start_row:end_row].iterrows():
        promoter_name = row['Promoter_Name']
        contact_website = row['Contact Website']
        
        # Ensure the URL starts with https
        if not contact_website.startswith('http'):
            contact_website = 'https://' + contact_website
        
        # Scrape the website
        try: 
            results = scraper.scrape_website_prioritized(contact_website)
        
            # Check if the phone numbers are Indian
            indian_phones = [phone for phone in results['phones'] if phone.startswith('91') or phone.startswith('+91')]
        
            if indian_phones:
                contact_details.append({
                    'Promoter_Name': promoter_name,
                    'Contact Website': contact_website,
                    'Phone': ', '.join(indian_phones),
                    'Address': results.get('address', ''),
                    'Email': ', '.join(results['emails']),
                    'Contact Page URL': results['source_url']
                })
            else:
                failed_urls.append({
                   'Promoter_Name': promoter_name,
                   'Contact Website': contact_website
                })

            # Write the contact details to contactdetails.csv
            contact_details_df = pd.DataFrame(contact_details)
            contact_details_df.to_csv('contactdetails.csv', index=False)

            # Write the failed URLs to failed_urls.csv
            failed_urls_df = pd.DataFrame(failed_urls)
            failed_urls_df.to_csv('failed_urls.csv', index=False)
        except: 
            print('failed to parse url', contact_website)
     

# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_and_scrape.py <start_row> <end_row>")
        print("Example: python extract_and_scrape.py 0 10")
    else:
        start_row = int(sys.argv[1])
        end_row = int(sys.argv[2])
        process_urls(start_row, end_row)
