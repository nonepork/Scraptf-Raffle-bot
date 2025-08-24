# -*- coding: UTF-8 -*-
import json
import random
import sys
import time

from loguru import logger
from selenium.webdriver.common.by import By
from seleniumbase import SB

logger.remove()
logger.add(
    sys.stdout,
    format="[<light-green>{time:HH:mm:ss}</light-green>] <lvl>{message}</lvl>",
    level="INFO",
)


def verify_cloudflare(sb):  # not used yet
    sb.assert_element('img[alt="Logo"]', timeout=4)
    sb.sleep(3)


def scroll_to_bottom(sb):
    while True:
        sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        if sb.assert_text("That's all, no more!", "div.raffle-pagination-done"):
            break


def modify_cookie(sb, cookie, value):
    if cookie:
        cookie["value"] = value
        sb.driver.delete_cookie(cookie["name"])
        sb.add_cookie(cookie)


def run():
    with SB(uc=True) as sb:
        # Wait till page loads
        sb.uc_open_with_reconnect("https://scrap.tf/", 3)

        # Login to steam
        with open("config.json") as jsonFile:
            data = json.load(jsonFile)
            modified_stf = data["scraptf"]
        if modified_stf == "":
            logger.error("Config.json is empty!")
            sys.exit(1)
        original_stf = sb.get_cookie("scraptf")
        modify_cookie(sb, original_stf, modified_stf)
        sb.refresh()

        # Get all raffle links
        sb.uc_open_with_reconnect("https://scrap.tf/raffles", 3)
        scroll_to_bottom(sb)

        links = []
        all_raffle_hrefs = sb.find_elements(".raffle-name")
        for elem in all_raffle_hrefs:
            a = elem.find_element(By.TAG_NAME, "a")
            links.append(a.get_attribute("href"))
        logger.success("Total raffles: {amount}", amount=len(links))

        # Join all raffles

        for link in links:
            sb.uc_open_with_reconnect(link, 3)

            try:
                sb.wait_for_element(
                    'button[data-loading-text="Entering..."]:not([style*="display: none;"])'
                )
                sb.click(
                    'button[data-loading-text="Entering..."]:not([style*="display: none;"])'
                )
                logger.opt(colors=True).info(
                    "{raffle_title} <green>Joined</green>",
                    raffle_title=sb.get_title().replace(" - Scrap.TF Raffles", ""),
                )
                time.sleep(random.randint(1, 3))

            except Exception:
                try:
                    sb.wait_for_element(
                        'button[data-loading-text="Leaving..."]:not([style*="display: none;"])'
                    )
                    logger.opt(colors=True).info(
                        "{raffle_title} <yellow>Already joined</yellow>",
                        raffle_title=sb.get_title().replace(" - Scrap.TF Raffles", ""),
                    )
                except Exception as e:
                    logger.exception(f"Error: {e}")
                    continue

    logger.success("Joined all raffles. :)")


if __name__ == "__main__":
    run()
