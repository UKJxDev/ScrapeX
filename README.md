## WebLens – Web Scraper

### Overview

WebLens is a lightweight web scraping application that extracts structured and unstructured data from websites. It allows users to input a URL and retrieve key information such as page metadata, text content, links, images, and headers in a structured format. The application also provides options to export the scraped data in multiple formats.

---

### Features

* Extracts metadata (title, description, keywords, author, canonical URL)
* Retrieves all links and images from a webpage
* Captures header tags (H1–H4)
* Cleans and processes full page text
* Displays data in a structured dashboard
* Export options: JSON, CSV, TXT, ZIP

---

### Tech Stack

* Python for core logic
* Streamlit for frontend interface
* Selenium for browser automation
* BeautifulSoup for HTML parsing
* Pandas for data handling and export

---

### Architecture

The application follows a simple modular architecture:

* Frontend (Streamlit): Handles user input and displays results
* Scraper Module: Uses Selenium to load pages and BeautifulSoup to parse content
* Data Processing Layer: Cleans and structures extracted data
* Export Layer: Converts data into downloadable formats

---

### Data Handling

No database is used. Data is processed in memory and structured as Python dictionaries.
For export, data is converted into:

* JSON for full structured data
* CSV for tabular data (links, images, headers)
* TXT for text content

This keeps the system lightweight and fast.

---

### How to Run (macOS)

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Install Chrome (if not already installed)

3. Run the app:

```
streamlit run app.py
```

4. Open in browser:

```
http://localhost:8501
```

---