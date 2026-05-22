from flask import Flask, request, jsonify

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import json
import time
import urllib.parse
import re

app = Flask(__name__)

CHROME = "/data/data/com.termux/files/usr/bin/chromium-browser"
DRIVER = "/data/data/com.termux/files/usr/bin/chromedriver"


def resolve_stream(page_url):

    chrome_options = Options()

    chrome_options.binary_location = CHROME

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    chrome_options.add_argument("--window-size=1920,1080")

    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    chrome_options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    chrome_options.add_experimental_option(
        "useAutomationExtension",
        False
    )

    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    chrome_options.set_capability(
        "goog:loggingPrefs",
        {"performance": "ALL"}
    )

    service = Service(DRIVER)

    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                window.navigator.chrome = {
                    runtime: {},
                };

                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });

                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1,2,3,4,5]
                });
            """
        }
    )

    try:

        print("\nOPEN PAGE:")
        print(page_url)

        driver.get(page_url)

        time.sleep(10)

        # iframe handle
        iframes = driver.find_elements(By.TAG_NAME, "iframe")

        for iframe in iframes:

            try:

                driver.switch_to.frame(iframe)

                video = driver.find_element(By.TAG_NAME, "video")

                driver.execute_script(
                    "arguments[0].play();",
                    video
                )

                break

            except:
                driver.switch_to.default_content()

        driver.switch_to.default_content()

        # main page video play
        try:

            video = driver.find_element(By.TAG_NAME, "video")

            actions = ActionChains(driver)

            actions.move_to_element(video).click().perform()

        except:

            try:
                driver.execute_script(
                    "document.querySelector('video').play();"
                )
            except:
                pass

        time.sleep(8)

        # DIRECT DOM SRC
        try:

            video = driver.find_element(By.TAG_NAME, "video")

            src = video.get_attribute("src")

            if not src:

                source = video.find_element(By.TAG_NAME, "source")

                src = source.get_attribute("src")

            if src and src.startswith("http"):

                print("\nDIRECT VIDEO SRC FOUND:")
                print(src)

                return src

        except:
            pass

        # PERFORMANCE LOG CHECK
        logs = driver.get_log("performance")

        for entry in logs:

            try:

                log = json.loads(
                    entry["message"]
                )["message"]

                if log["method"] == "Network.requestWillBeSent":

                    req_url = log["params"]["request"]["url"]

                    decoded = urllib.parse.unquote(req_url)

                    matches = re.findall(
                        r'(https?://[^\s"\']+\.(?:mp4|m3u8)[^\s"\']*)',
                        decoded,
                        re.I
                    )

                    for match in matches:

                        if any(x in match.lower() for x in [
                            "poster",
                            "thumb",
                            "sprite",
                            "logo",
                            "favicon",
                            "analytics"
                        ]):
                            continue

                        print("\nSTREAM FOUND:")
                        print(match)

                        return match

            except:
                pass

        return None

    except Exception as e:

        print("\nERROR:")
        print(str(e))

        return None

    finally:

        driver.quit()


@app.route("/")
def home():

    return "Resolver Running"


@app.route("/resolve")
def resolve():

    url = request.args.get("url")

    if not url:

        return jsonify({
            "status": "error",
            "message": "No URL provided"
        })

    stream = resolve_stream(url)

    if stream:

        return jsonify({
            "status": "success",
            "stream_url": stream
        })

    return jsonify({
        "status": "error",
        "message": "Stream not found"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080
    )