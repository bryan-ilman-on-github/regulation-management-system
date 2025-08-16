from app.scraper import BPKRegulationScraper
from bs4 import BeautifulSoup
from unittest.mock import MagicMock, patch
import json
import pytest
import requests

# Sample HTML content for testing
SAMPLE_HTML = """
<html>
<head><title>Test Regulation</title></head>
<body>
    <h4 class="mb-8">Peraturan Pemerintah (PP) No. 12 Tahun 2020</h4>
    <h1 class="text-white">Tentang Testing dan Automation</h1>
    
    <div class="py-4">
        <div class="fw-bold">Judul</div>
        <div>Peraturan Pemerintah (PP) Nomor 12 Tahun 2020 tentang Testing dan Automation</div>
    </div>
    
    <div class="py-4 bg-light-primary">
        <div class="fw-bold">Nomor</div>
        <div>12</div>
    </div>
    
    <div class="py-4">
        <div class="fw-bold">Tahun</div>
        <div>2020</div>
    </div>
    
    <div class="py-4 bg-light-primary">
        <div class="fw-bold">Tanggal Penetapan</div>
        <div>15 Juni 2020</div>
    </div>
    
    <div class="py-4">
        <div class="fw-bold">Status</div>
        <div>Berlaku</div>
    </div>
    
    <div class="py-4 bg-light-primary">
        <div class="fw-bold">Subjek</div>
        <div>TESTING</div>
    </div>
    
    <a class="download-file" href="/fake/path1.pdf">Link 1</a>
    <a class="download-file" href="/fake/path2.pdf">Link 2</a>
    
    <div class="container fs-6">
        <div class="row">
            <div class="fw-semibold bg-light-primary">diubah dengan</div>
        </div>
        <div class="row">
            <ol>
                <li><a href="/Details/12345">PP No. 15 Tahun 2021 tentang Update Testing</a></li>
            </ol>
        </div>
        
        <div class="row">
            <div class="fw-semibold bg-light-primary">mengubah</div>
        </div>
        <div class="row">
            <ol>
                <li><a href="/Details/54321">PP No. 10 Tahun 2019 tentang Original Testing</a></li>
            </ol>
        </div>
    </div>
</body>
</html>
"""


@pytest.fixture
def mock_response():
    """Create a mock response with our sample HTML"""
    mock = MagicMock()
    mock.content = SAMPLE_HTML.encode("utf-8")
    return mock


@pytest.fixture
def scraper():
    """Create a scraper instance"""
    return BPKRegulationScraper()


def test_scraper_initialization(scraper):
    """Test that the scraper initializes correctly"""
    assert scraper.base_url == "https://peraturan.bpk.go.id"
    assert scraper.session is not None
    assert "User-Agent" in scraper.session.headers


@patch("requests.Session.get")
def test_scrape_regulation_detail(mock_get, mock_response, scraper):
    """Test the main scraping method"""
    # Configure the mock to return our sample response
    mock_get.return_value = mock_response

    # Call the method
    result = scraper.scrape_regulation_detail("https://test.url")

    # Check the basic fields
    assert result["nama_peraturan"] == "Peraturan Pemerintah (PP) No. 12 Tahun 2020"
    assert result["materi_pokok"] == "Tentang Testing dan Automation"
    assert (
        result["judul"]
        == "Peraturan Pemerintah (PP) Nomor 12 Tahun 2020 tentang Testing dan Automation"
    )
    assert result["nomor"] == "12"
    assert result["tahun"] == "2020"
    assert result["status"] == "Berlaku"
    assert result["tanggal_penetapan"] == "2020-06-15"
    assert result["subjek"] == "TESTING"

    # Check the extracted regulation type
    assert result["tipe_dokumen"] == "Peraturan Pemerintah (PP)"
    assert result["bentuk"] == "Peraturan Pemerintah (PP)"
    assert result["bentuk_singkat"] == "PP"

    # Check default values
    assert result["teu"] == "Indonesia, Pemerintah Pusat"
    assert result["lokasi"] == "Pemerintah Pusat"

    # Check PDF link
    assert result["file_pdf"] == "https://peraturan.bpk.go.id/fake/path2.pdf"

    # Check relationships
    assert len(result["diubah_dengan"]) == 1
    assert (
        result["diubah_dengan"][0]["text"]
        == "PP No. 15 Tahun 2021 tentang Update Testing"
    )
    assert (
        result["diubah_dengan"][0]["link"]
        == "https://peraturan.bpk.go.id/Details/12345"
    )

    assert len(result["mengubah"]) == 1
    assert (
        result["mengubah"][0]["text"] == "PP No. 10 Tahun 2019 tentang Original Testing"
    )
    assert result["mengubah"][0]["link"] == "https://peraturan.bpk.go.id/Details/54321"


def test_parse_date(scraper):
    """Test the date parsing method"""
    # Test Indonesian format
    assert scraper._parse_date("15 Juni 2020") == "2020-06-15"
    assert scraper._parse_date("1 Januari 2021") == "2021-01-01"
    assert scraper._parse_date("30 Desember 1999") == "1999-12-30"

    # Test ISO format
    assert scraper._parse_date("2020-06-15") == "2020-06-15"

    # Test empty/None cases
    assert scraper._parse_date("") is None
    assert scraper._parse_date(None) is None

    # Test invalid format
    assert scraper._parse_date("Invalid date") is None


def test_extract_relationships(scraper):
    """Test the relationship extraction method"""
    # Create a sample BeautifulSoup object
    soup = BeautifulSoup(SAMPLE_HTML, "html.parser")

    # Initialize result dictionary
    result = {"diubah_dengan": [], "mencabut": [], "mengubah": [], "dicabut_dengan": []}

    # Call the method
    scraper._extract_relationships(soup, result)

    # Check the results
    assert len(result["diubah_dengan"]) == 1
    assert (
        result["diubah_dengan"][0]["text"]
        == "PP No. 15 Tahun 2021 tentang Update Testing"
    )
    assert (
        result["diubah_dengan"][0]["link"]
        == "https://peraturan.bpk.go.id/Details/12345"
    )

    assert len(result["mengubah"]) == 1
    assert (
        result["mengubah"][0]["text"] == "PP No. 10 Tahun 2019 tentang Original Testing"
    )
    assert result["mengubah"][0]["link"] == "https://peraturan.bpk.go.id/Details/54321"

    # These should still be empty
    assert len(result["mencabut"]) == 0
    assert len(result["dicabut_dengan"]) == 0


@patch("requests.Session.get")
def test_scraper_handles_request_error(mock_get, scraper):
    """Test that the scraper properly handles request errors"""
    # Configure the mock to raise an exception
    mock_get.side_effect = requests.RequestException("Test error")

    # This should be caught and handled in the main script, not in the class methods
    # We just ensure the exception is properly raised from the method
    with pytest.raises(requests.RequestException):
        scraper.scrape_regulation_detail("https://test.url")
