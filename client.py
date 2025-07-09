import asyncio
import json

from google.genai import types
from google.genai.types import Part, Content
from mcp import ClientSession
from mcp.client.sse import sse_client
from google import genai


client = genai.Client(api_key="")  # Replace with your actual API key


def extract_data(image_bytes) -> dict | None:
    """
    Process the image bytes of the shareholding certificate and extract relevant data.

    :param image_bytes:   The bytestream of the image to be processed.
    :return:  The dict {"field": ..., "value": ...} of the data extracted from the image.

    """
    prompt = """
    
        You are given an image or scanned document of an old materialized shareholding certificate. Your task is to extract the following specific fields from the document and return the output in strict JSON format:
    
        1. company_name: Full legal name of the company issuing the certificate.
        2. shareholder_name: Full legal name of the individual or entity to whom the shares are issued.
        3. issue_date: The date on which the shares were issued, in YYYY-MM-DD format. If the date is not present, return null.
        4. number_of_shares: Total number of shares issued, as an integer.
        
        Constraints:
        
        1. Return only the JSON output, with no additional commentary.
        2. If any of the fields are missing or illegible, use null.
        3. Ensure the extracted text is accurate and complete, especially proper nouns and numeric values.
        4. Do not infer or guess—only extract what is explicitly stated in the certificate.
        
        Output format:
        
        {
          "company_name": "Example Corporation Ltd.",
          "shareholder_name": "John A. Doe",
          "issue_date": "1987-04-15",
          "number_of_shares": 1000
        }
        
        Begin parsing the document now.
    
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            prompt,
            types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg',
            )
        ]
    )

    print(response.text)

    try:
        result = json.loads(response.text)
        if isinstance(result, dict) and 'field' in result and 'value' in result:
            return result
        else:
            print("Invalid response format.")
            return None
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
        return None


async def main(extracted_json: json):
    """
    Main function that connects to the MCP server and processes the extracted data with the available tools.

    :param extracted_json: The JSON object containing extracted data from the shareholding certificate.
    :return: None | The result will be printed to the console.
    """
    async with sse_client("http://127.0.0.1:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools_result = await session.list_tools()

            print(type(tools_result))

            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            prompt = f"""
            
            You are an autonomous financial assistant tasked with analyzing a company name from an old shareholding certificate and finding relevant latest details fo the company.
            ---
            
            You have access to the following tool:
            
            1. `check_company_status(company_name: str, issue_date: str) -> dict`:  
               - Takes a company name and issue date as input
               - Uses Google Search to determine if the company is still active, has been acquired, merged, or dissolved  
               - Returns structured JSON with status, ticker, and source link
               
            2. `get_value(symbol: str, quantity: int) -> dict`:
                - Takes a stock ticker symbol and quantity of shares
                - Fetches the latest share price from NSE
                - Returns a dictionary with the total value of the shares   
            
            ### Objective:
            Do the following:
            
            - Use `check_company_status` to determine if the company still exists and, if so, whether the shares might be redeemable
            - If a valid ticker is returned, optionally call `get_value` to estimate the total value
            - Summarize the outcome clearly:  
              - Is the company still active?  
              - How many shares are held?  
              - Any action items for the user
            
            Return a structured final report that is human-readable but derived from all tool outputs.
            
            ### Input:
            - `company_name`: {extracted_json['company_name']}
            - `issue_date`: {extracted_json['issue_date']}
            - `number_of_shares`: {extracted_json['number_of_shares']}

            You may begin processing.
            """

            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=genai.types.GenerateContentConfig(
                    temperature=0.125,
                    tools=[session],
                    automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(
                        disable=False
                    ),
                ),
            )
            print(response.text)


if __name__ == "__main__":

    # Load the image bytes from a file (for testing purposes)

    #TODO (later): Automate the image loading part from the command line arguments
    #TODO (later): Can possibly add a gradio interface to upload the image and process it

    # Replace with the path to your image file
    with open("test_image.jpg", "rb") as f:
        image_bytes = f.read()

    data = extract_data(image_bytes=image_bytes)

    print("Extracted Data" + str(data))

    # Dummy data for testing

    # data = {
    #     "company_name": "India Tobacco Company Limited",
    #     "shareholder_name": "John A. Doe",
    #     "issue_date": "28-4-1973",
    #     "number_of_shares": 50
    # }

    asyncio.run(main(extracted_json=data))
