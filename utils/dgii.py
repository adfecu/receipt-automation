import requests
from bs4 import BeautifulSoup
import warnings

# Suppress the InsecureRequestWarning from verify=False
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

URL = "https://dgii.gov.do/app/WebApps/ConsultasWeb2/ConsultasWeb/consultas/rnc.aspx"

def consulta_rnc(rnc: str):
    session = requests.Session()

    # Step 1: GET the page with browser-like headers to bypass bot detection
    # These headers are translated from your cURL command
    browser_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=0, i',
        'referer': 'https://www.google.com/',
        'sec-ch-ua': '"Opera";v="120", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36',
    }
    
    # The session object will automatically receive and store cookies
    resp = session.get(URL, headers=browser_headers, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract hidden form fields required for the POST request
    def get_val(name):
        tag = soup.find("input", {"name": name})
        return tag["value"] if tag else ""

    viewstate = get_val("__VIEWSTATE")
    viewstategen = get_val("__VIEWSTATEGENERATOR")
    eventval = get_val("__EVENTVALIDATION")

    if not viewstate:
        # If viewstate is still not found, the page structure might have changed
        # or the anti-bot measures have become more sophisticated.
        # print(resp.text) # Uncomment to debug the received HTML
        raise RuntimeError("Could not find __VIEWSTATE. The page might be blocking the request.")

    # Step 2: Build the payload for the POST request (AJAX call)
    payload = {
        "ctl00$smMain": "ctl00$cphMain$upBusqueda|ctl00$cphMain$btnBuscarPorRNC",
        "ctl00$cphMain$txtRNCCedula": rnc,
        "ctl00$cphMain$txtRazonSocial": "",
        "ctl00$cphMain$hidActiveTab": "",
        "__EVENTTARGET": "ctl00$cphMain$btnBuscarPorRNC",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategen,
        "__EVENTVALIDATION": eventval,
        "__ASYNCPOST": "true",
    }
    
    # These headers are specific for the AJAX POST request
    ajax_headers = {
        "X-MicrosoftAjax": "Delta=true",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": browser_headers['user-agent'], # Maintain the same user-agent
        "Referer": URL, # The referer is now the page itself
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # The session sends the cookies it received from the GET request automatically
    res = session.post(URL, data=payload, headers=ajax_headers, verify=False)
    return parse_dgii_response(res.text)


def parse_dgii_response(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "cphMain_dvDatosContribuyentes"})
    
    data = {}
    if table:
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 2:
                # Clean up keys and values
                key = " ".join(cells[0].get_text(strip=True).replace(':', '').split())
                val = " ".join(cells[1].get_text(strip=True).split())
                data[key] = val
    return data


# Example usage:
if __name__ == "__main__":
    rnc_to_check = "131563856" # Example RNC for "CERVECERIA NACIONAL DOMINICANA"
    try:
        import time
        start = time.time()
        data = consulta_rnc(rnc_to_check)
        elapsed = time.time() - start
        print(f"consulta_rnc took {elapsed:.2f} seconds.")
        if data:
            # for key, value in data.items():
            #     print(f"{key}: {value}")
            print(data)
        else:
            print(f"No data found for RNC: {rnc_to_check}")
    except RuntimeError as e:
        print(f"An error occurred: {e}")