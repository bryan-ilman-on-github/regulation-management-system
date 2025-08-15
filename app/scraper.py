"""
BPK Regulation Scraping Prototype

This module scrapes regulation data from the BPK website and provides the data
as a dictionary.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Optional, Dict, Any

class BPKRegulationScraper:
    """A scraper for fetching regulation details from peraturan.bpk.go.id."""
    
    def __init__(self):
        """Initializes the scraper with a session and user agent."""
        self.base_url = "https://peraturan.bpk.go.id"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_regulation_detail(self, url: str) -> Dict[str, Any]:
        """
        Scrapes regulation details from a given BPK regulation URL.

        Args:
            url: The full URL of the regulation detail page.

        Returns:
            A dictionary containing the scraped regulation data.
        """
        print(f"Scraping URL: {url}")
        
        response = self.session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Initialize result dictionary
        result = {
            'nama_peraturan': None,
            'link_peraturan': url,
            'tipe_dokumen': None,
            'materi_pokok': None,
            'judul': None,
            'teu': None,
            'nomor': None,
            'bentuk': None,
            'bentuk_singkat': None,
            'tahun': None,
            'tempat_penetapan': None,
            'tanggal_penetapan': None,
            'tanggal_pengundangan': None,
            'tanggal_berlaku': None,
            'sumber': None,
            'status': None,
            'bahasa': None,
            'lokasi': None,
            'bidang': None,
            'subjek': None,
            'dicabut_dengan': [],
            'mencabut': [],
            'diubah_dengan': [],
            'mengubah': [],
            'ujimateri_mk': [],
            'file_peraturan': [],
            'file_pdf': None
        }
        
        # Extract title from page header
        title_element = soup.find('h4', class_='mb-8')
        if title_element:
            result['nama_peraturan'] = title_element.get_text(strip=True)
        
        # Extract full title/subject
        subject_element = soup.find('h1', class_='text-white')
        if subject_element:
            result['materi_pokok'] = subject_element.get_text(strip=True)
        
        # Extract detailed information from rows
        detail_rows = soup.find_all('div', class_=['py-4', 'bg-light-primary'])
        
        for row in detail_rows:
            label_element = row.find('div', class_='fw-bold')
            if not label_element:
                continue
                
            label = label_element.get_text(strip=True)
            value_element = label_element.find_next_sibling('div')
            
            if not value_element:
                continue
                
            value = value_element.get_text(strip=True)
            
            # Map labels to fields
            if 'Judul' in label:
                result['judul'] = value
            elif 'Nomor' in label:
                result['nomor'] = value
            elif 'Tahun' in label:
                result['tahun'] = value
            elif 'Tempat Penetapan' in label:
                result['tempat_penetapan'] = value
            elif 'Tanggal Penetapan' in label:
                result['tanggal_penetapan'] = self._parse_date(value)
            elif 'Tanggal Pengundangan' in label:
                result['tanggal_pengundangan'] = self._parse_date(value)
            elif 'Tanggal Berlaku' in label:
                result['tanggal_berlaku'] = self._parse_date(value)
            elif 'Sumber' in label:
                result['sumber'] = value
            elif 'Status' in label:
                result['status'] = value
            elif 'Bahasa' in label:
                result['bahasa'] = value
            elif 'Subjek' in label:
                result['subjek'] = value if value else None
            elif 'Bidang' in label:
                result['bidang'] = value if value else None
        
        # Extract regulation type from nama_peraturan
        if result['nama_peraturan']:
            # Extract type like "Peraturan Pemerintah (PP)"
            type_match = re.search(r'^([^N]+)(?=\s+Nomor|\s+No\.)', result['nama_peraturan'])
            if type_match:
                result['tipe_dokumen'] = type_match.group(1).strip()
                result['bentuk'] = result['tipe_dokumen']
                
                # Extract short form like "PP"
                short_match = re.search(r'\(([^)]+)\)', result['tipe_dokumen'])
                if short_match:
                    result['bentuk_singkat'] = short_match.group(1)
        
        # Set default values
        result['teu'] = 'Indonesia, Pemerintah Pusat'
        result['lokasi'] = 'Pemerintah Pusat'
        
        # Extract PDF download link
        pdf_links = soup.find_all('a', class_='download-file')
        if len(pdf_links) >= 2:
            pdf_link = pdf_links[1]  # Second occurrence
            if pdf_link and pdf_link.get('href'):
                result['file_pdf'] = self.base_url + pdf_link['href']
        
        # Extract relationships (mencabut, diubah_dengan, etc.)
        self._extract_relationships(soup, result)
        
        return result

    def _parse_date(self, date_text: str) -> Optional[str]:
        """Parses date from various Indonesian formats to YYYY-MM-DD."""
        if not date_text or date_text.strip() == '':
            return None
            
        date_text = date_text.strip()
        
        month_mapping = {
            'januari': '01', 'februari': '02', 'maret': '03', 'april': '04',
            'mei': '05', 'juni': '06', 'juli': '07', 'agustus': '08',
            'september': '09', 'oktober': '10', 'november': '11', 'desember': '12'
        }
        
        # Pattern 1: Indonesian date format (e.g., 30 Juni 1961)
        match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', date_text, re.IGNORECASE)
        if match:
            day, month_name, year = match.groups()
            month_num = month_mapping.get(month_name.lower())
            if month_num:
                return f"{year}-{month_num}-{day.zfill(2)}"
        
        # Pattern 2: ISO format (e.g., 1961-06-30)
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
        if match:
            return date_text
        
        return None

    def _extract_relationships(self, soup: BeautifulSoup, result: Dict[str, Any]):
        """Extracts regulation relationships (mencabut, diubah_dengan, etc.)"""
        # Mapping from header text to result dictionary keys
        relationship_map = {
            'diubah dengan': 'diubah_dengan',
            'mencabut': 'mencabut',
            'mengubah': 'mengubah',
            'dicabut dengan': 'dicabut_dengan'
        }

        # Find all relationship headers
        headers = soup.find_all('div', class_=['fw-semibold', 'bg-light-primary'])

        for header in headers:
            header_text = header.get_text(strip=True).lower()
            relationship_type = relationship_map.get(header_text)

            if not relationship_type:
                continue
            
            # The list of related items is usually in an <ol> in the next row
            list_container = header.find_parent('div', class_='row')
            if list_container:
                ol_element = list_container.find_next_sibling('div', class_='row').find('ol')
                if ol_element:
                    items = []
                    for li in ol_element.find_all('li'):
                        link = li.find('a')
                        if link:
                            full_text = re.sub(r'\s+', ' ', li.get_text(strip=True))
                            href = link.get('href', '')
                            if href.startswith('/'):
                                href = self.base_url + href
                            
                            items.append({
                                'text': full_text,
                                'link': href
                            })
                    
                    if items:
                        result[relationship_type] = items

# This block allows the script to be run directly for testing
if __name__ == "__main__":
    # Test the scraper with a sample URL
    test_url = "https://peraturan.bpk.go.id/Details/49482/pp-no-34-tahun-2005"
    
    scraper = BPKRegulationScraper()
    
    print("Starting scraping...")
    try:
        scraped_data = scraper.scrape_regulation_detail(test_url)
        
        # Display scraped data in a readable format
        print("\n=== SCRAPED DATA ===")
        for key, value in scraped_data.items():
            # Pretty print lists
            if isinstance(value, list) and len(value) > 0:
                print(f"{key}:")
                print(json.dumps(value, indent=2, ensure_ascii=False))
            # Print non-empty values
            elif value is not None and value != '':
                print(f"{key}: {value}")
            # Indicate empty values
            else:
                print(f"{key}: (empty)")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")