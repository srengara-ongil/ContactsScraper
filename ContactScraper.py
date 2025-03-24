import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, List, Tuple, Optional, Any, Union

class ContactScraper:
    """
    A class for scraping contact information (emails and phone numbers) from websites.
    Prioritizes contact information from Contact Us pages over the main page.
    Filters phone numbers to only include those starting with 91 or +91 (Indian numbers).
    """

    def __init__(self, user_agent: Optional[str] = None, timeout: int = 10):
        """
        Initialize the ContactScraper with custom settings.

        Args:
            user_agent: Custom user agent string. If None, a default will be used.
            timeout: Request timeout in seconds.
        """
        self.timeout = timeout
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}

        # Default regex patterns
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Phone patterns specifically for Indian numbers (starting with 91 or +91)
        self.phone_patterns = [
            r'91[-.\s]?\d{10}',               # 91 followed by 10 digits
            r'\+91[-.\s]?\d{10}',             # +91 followed by 10 digits
            r'91[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # 91 123-456-7890 format
            r'\+91[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'  # +91 123-456-7890 format
        ]
        
        # Contact page identifying terms
        self.contact_terms = ['contact', 'contact us', 'get in touch', 'reach us']

    def set_email_pattern(self, pattern: str) -> None:
        """Set a custom email regex pattern."""
        self.email_pattern = pattern

    def set_phone_patterns(self, patterns: List[str]) -> None:
        """Set custom phone number regex patterns."""
        self.phone_patterns = patterns

    def add_phone_pattern(self, pattern: str) -> None:
        """Add a phone pattern to the existing list."""
        self.phone_patterns.append(pattern)

    def set_contact_terms(self, terms: List[str]) -> None:
        """Set custom terms for identifying contact pages."""
        self.contact_terms = terms

    def add_contact_term(self, term: str) -> None:
        """Add a term to the existing list of contact page identifiers."""
        self.contact_terms.append(term.lower())

    def extract_contact_info(self, html_content: str) -> Tuple[List[str], List[str]]:
        """
        Extract email addresses and Indian phone numbers from HTML content.
        Only extracts phones starting with 91 or +91.

        Args:
            html_content: HTML content as string

        Returns:
            Tuple containing lists of unique emails and phone numbers
        """
        # Extract emails
        emails = re.findall(self.email_pattern, html_content)
        
        # Extract phone numbers matching Indian patterns
        phone_numbers = []
        for pattern in self.phone_patterns:
            phone_numbers.extend(re.findall(pattern, html_content))
        
        # Additional filtering to ensure we only get Indian numbers
        filtered_phones = []
        for phone in phone_numbers:
            # Clean up the phone number
            cleaned = re.sub(r'[-.\s()]', '', phone)
            # Check if it starts with +91 or 91
            if cleaned.startswith('+91') or cleaned.startswith('91'):
                filtered_phones.append(phone)
        
        # Remove duplicates
        return list(set(emails)), list(set(filtered_phones))

    def find_contact_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Find contact page links in the website.

        Args:
            soup: BeautifulSoup object of the page
            base_url: Base URL for resolving relative links

        Returns:
            List of contact page URLs
        """
        contact_links = []
        
        # Look for links containing contact-related text
        for link in soup.find_all('a', href=True):
            link_text = link.text.strip().lower()
            link_href = link['href'].lower()
            
            if any(term in link_text or term in link_href for term in self.contact_terms):
                full_url = urljoin(base_url, link['href'])
                contact_links.append(full_url)
        
        return list(set(contact_links))

    def get_page_content(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get HTML content from a URL with error handling.

        Args:
            url: URL to fetch

        Returns:
            Tuple of (html_content, error_message)
            If successful, error_message is None
            If failed, html_content is None
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text, None
        except Exception as e:
            return None, str(e)

    def scrape_website_prioritized(self, url: str) -> Dict[str, Any]:
        """
        Scrape a website for contact information with priority logic:
        1. Check contact pages first
        2. Only use main page info if no contact pages exist or no phone numbers found on contact pages

        Args:
            url: Website URL to scrape

        Returns:
            Dictionary containing prioritized contact information
        """
        results = {
            'source': None,  # Will be 'contact_page' or 'main_page'
            'source_url': None,
            'emails': [],
            'phones': [],
            'errors': []
        }
        
        # Get the main page
        main_page_html, error = self.get_page_content(url)
        
        if error:
            results['errors'].append(f"Error fetching main page: {error}")
            return results
            
        # Extract contacts from main page (we'll decide whether to use them later)
        main_emails, main_phones = self.extract_contact_info(main_page_html)
        
        # Find contact page links
        main_page_soup = BeautifulSoup(main_page_html, 'html.parser')
        contact_links = self.find_contact_links(main_page_soup, url)
        
        # Check if contact pages exist
        if contact_links:
            # Visit each contact page and look for phone numbers
            for link in contact_links:
                contact_html, error = self.get_page_content(link)
                
                if error:
                    results['errors'].append(f"Error fetching contact page {link}: {error}")
                    continue
                    
                contact_emails, contact_phones = self.extract_contact_info(contact_html)
                
                # If we found phone numbers on this contact page, use them and stop looking
                if contact_phones:
                    results['source'] = 'contact_page'
                    results['source_url'] = link
                    results['emails'] = contact_emails
                    results['phones'] = contact_phones
                    return results
        
        # If we get here, either no contact pages exist or none had phone numbers
        # So we'll use the main page info
        results['source'] = 'main_page'
        results['source_url'] = url
        results['emails'] = main_emails
        results['phones'] = main_phones
        
        return results

    def scrape_website(self, url: str, follow_contact_pages: bool = True) -> Dict[str, Any]:
        """
        Legacy method: Scrape a website for contact information from all pages.
        Consider using scrape_website_prioritized() instead for the priority logic.

        Args:
            url: Website URL to scrape
            follow_contact_pages: Whether to also scrape contact pages

        Returns:
            Dictionary containing all found contact information
        """
        results = {
            'main_page': {
                'url': url,
                'emails': [],
                'phones': []
            },
            'contact_pages': [],
            'errors': []
        }
        
        # Get the main page
        main_page_html, error = self.get_page_content(url)
        
        if error:
            results['errors'].append(f"Error fetching main page: {error}")
            return results
            
        # Extract contacts from main page
        main_emails, main_phones = self.extract_contact_info(main_page_html)
        results['main_page']['emails'] = main_emails
        results['main_page']['phones'] = main_phones
        
        # Stop here if we're not following contact pages
        if not follow_contact_pages:
            return results
            
        # Find and follow contact page links
        main_page_soup = BeautifulSoup(main_page_html, 'html.parser')
        contact_links = self.find_contact_links(main_page_soup, url)
        
        # Visit each contact page and extract information
        for link in contact_links:
            contact_page_data = {'url': link, 'emails': [], 'phones': []}
            
            contact_html, error = self.get_page_content(link)
            
            if error:
                contact_page_data['error'] = error
            else:
                contact_emails, contact_phones = self.extract_contact_info(contact_html)
                contact_page_data['emails'] = contact_emails
                contact_page_data['phones'] = contact_phones
                
            results['contact_pages'].append(contact_page_data)
        
        return results


# Example usage
if __name__ == "__main__":
    scraper = ContactScraper()
    
    # Add custom patterns if needed for other Indian number formats
    scraper.add_phone_pattern(r'91[-.\s]?\d{5}[-.\s]?\d{5}')  # For 5-5 digit format
    
    # Scrape a website with the prioritized approach
    website_url = "http://www.ramireddyconstructions.com"  # Replace with the actual website URL
    results = scraper.scrape_website_prioritized(website_url)
    
    # Print results
    print(f"Contact information found on: {results['source']}")
    print(f"Source URL: {results['source_url']}")
    print(f"Emails: {results['emails']}")
    print(f"Phones: {results['phones']} (Only Indian numbers)")
    
    if results['errors']:
        print("\nErrors encountered:")
        for error in results['errors']:
            print(f"  - {error}")