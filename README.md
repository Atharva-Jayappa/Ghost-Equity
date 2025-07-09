# 🕵️‍♂️ GhostEquity  : Legacy Stock Discovery & Valuation Agent  

GhostEquity is a Python-based Agent for analyzing old shareholding certificates and investigating the current status and value of historical company shares. It leverages Google Gemini, yfinance, and FastMCP to automate extraction, validation, and valuation of legacy financial documents.

---

## 📝 What does it do?

1. **Extracts Data from Share Certificates:**  
   Uses Google Gemini to process scanned images of old share certificates and extract key fields (company name, shareholder, issue date, number of shares).

2. **Checks Company Status:**  
   Uses a custom tool (with Google's Search grounding via Gemini) to determine if the company is still active, has merged, been acquired, or dissolved, and fetches the latest ticker and relevant info.

3. **Estimates Share Value:**  
   If the company is still listed, fetches the latest share price from NSE (via yfinance) and estimates the total value of the shares.

4. **Returns a Human-Readable Report:**  
   Summarizes findings and action items for the user.

---

## 🛠️ Features

- **Automated OCR & Data Extraction** from share certificate images.
- **Real-Time Company Status Lookup** using Google Search (via Gemini).
- **Live Share Price Fetching** from NSE using yfinance.
- **Modular Tooling** via FastMCP for easy extension.
- **JSON-based APIs** for integration and automation.

---

## 📦 Requirements

- Python 3.9+
- [google-generativeai](https://pypi.org/project/google-generativeai/)
- [yfinance](https://pypi.org/project/yfinance/)
- [regex](https://pypi.org/project/regex/)
- [MCP](https://pypi.org/project/mcp/) 

Install dependencies:
```bash
pip install google-generativeai yfinance regex mcp
```

---

## 🚀 Usage

### 1. Set up your Google GenAI API Key

Edit both `server.py` and `client.py` and replace the empty string in `genai.Client(api_key="")` with your actual API key.

### 2. Start the Server

```bash
python server.py
```
- The server runs on `http://127.0.0.1:8050` and exposes tools for company status checking and share value estimation.

### 3. Run the Client

- Place a scanned share certificate image as `test_image.jpg` in the project directory (or modify the path in `client.py`).
- Run:

```bash
python client.py
```
- The client will:
  - Extract data from the image using Gemini.
  - Connect to the server and use the available tools.
  - Print a structured report with findings.

---

## 📁 Project Structure

```
client.py   # Extracts data from images and coordinates analysis
server.py   # Hosts tools for company status and share value lookup
README.md   # Project documentation
LICENSE     # License information
```

---

## ⚡ Example Workflow

1. Scan or photograph an old share certificate.
2. Run the client to extract and analyze the data.
3. Receive a report on whether the company still exists and the potential value of the shares.

---

## 🤝 Contributing

Contributions are welcome! 

---

## 📄 License

See the LICENSE file for details.

---

