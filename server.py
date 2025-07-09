from google.genai.types import Tool, GoogleSearch
from mcp.server.fastmcp import FastMCP
import json
from google import genai
from google.genai import types
import regex as re
import yfinance as yf

# Set up the FastMCP server
server = FastMCP(
    name="Financial FOrensics Tools",
    host="0.0.0.0",
    port=8050
)

client = genai.Client(api_key="")  # Replace with your actual API key


@server.tool(name="check_company_status")
async def check_company_status(
        company_name: str,
        issue_date: str,
) -> dict:
    """
    Check the status of a company and its shareholder.

    :param company_name: Full legal name of the company.
    :param issue_date: Date of share issuance in YYYY-MM-DD format.
    :return: A dictionary containing the status of the company and shareholder.
    """

    prompt = f"""

        You are an AI assistant helping to verify the current status of companies based on historical stock share records. 

        You have access to the Google Search tool — **always use it** to check the **real-time status** of each company, since the data must be up-to-date and cannot be guessed or inferred.

        For each company name provided, search and return the following as JSON:

        - `original_name`: The original company name as given in the input.
        - `current_name`: The most recent name of the company, if it has changed. If no change, use the original name.
        - `status`: One of `"active"`, `"acquired"`, `"merged"`, `"dissolved"`, `"unknown"` — based on the most recent and reliable information
        - `ticker`: The most recent **active ticker** if the company is still traded or has a clear successor. `"NA"` otherwise.
        - `source`: The URL of the page used to determine the above information
        - `additional-notes`: Any additional relevant information about the company, such as recent news or changes in ownership.

        Respond only with a JSON array. Do not include explanations or extra commentary.

        Example output:
        {{
                "original_name": "Example Corporation Ltd.",
                "current_name": "Example Corp.",
                "status": "active",
                "ticker": "EXC",
                "source": "https://example.com/company-status",
                "additional-notes": "The company recently expanded its operations to Europe."
        }}

        Input:

        original_name: {company_name}
        issue_date: {issue_date}

        Begin searching for the current status of the company now.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt],
        config=types.GenerateContentConfig(tools=[Tool(google_search=GoogleSearch())])
    )

    print("Response from model:", response.text)

    if not response or not response.candidates:
        return {"error": "No response from model"}
    try:
        # Obtain the raw text from the candidate response
        json_text = response.candidates[0].content.parts[0].text
        # Remove markdown code fences if present
        json_text = re.sub(r"^```(?:json)?\s*", "", json_text, flags=re.MULTILINE)
        json_text = re.sub(r"\s*```$", "", json_text, flags=re.MULTILINE)
        # Parse the cleaned JSON text
        data = json.loads(json_text)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from model"}

    return data


@server.tool()
async def get_value(symbol: str, quantity) -> dict:
    """
    Fetch the current share price from NSE for the given ticker/symbol.

    :param symbol: Stock ticker symbol (e.g., "RELIANCE").
    :param quantity: Number of shares.
    :return: A dictionary containing the success status, unit price, total price, and timestamp.
    """
    try:
        ticker = yf.Ticker(symbol.upper() + ".NS")
        return {"success": True, "total_price": ticker.info["currentPrice"] * quantity, "symbol": symbol.upper(), "individual_price": ticker.info["currentPrice"], "timestamp": ticker.info["regularMarketTime"]}
    except Exception as e:
        return {"success": False, "message": str(e)}


# Run the server
if __name__ == "__main__":
    try:
        server.run(transport="sse")
    except KeyboardInterrupt:
        print("Server stopped by user.")
