from aiohttp import ClientSession
import asyncio
import bs4
from datetime import datetime
import json
import logging
import motor.motor_asyncio as mtr
import random
import re

# https://www.olx.ua/uk/nedvizhimost/kvartiry/prodazha-kvartir/
URL = "https://www.olx.ua/uk/nedvizhimost/kvartiry/prodazha-kvartir/"
DBURL = "mongodb://localhost:27017/realty"
DBNAME = "realty"


def check_time(time: str):
    if re.search("(сьогодні|сегодня)", time.lower()):
        return True, datetime.now().strftime("%d.%m.%y")

    return False, time


def set_size(tags: list[str]):
    size = None
    for tag in tags:
        if re.search("(Загальна площа|Общая площадь)", tag):
            size = float(re.search("[\d\.]+", tag).group(0))
            break

    return size


def set_price(price: str, currency = 38.40):
    priced = float(re.search("[\d\s]+", price).group(0).replace(" ", ""))

    if re.search("грн", price):
        priced /= currency

    return priced


def set_rooms(tags: list[str]):
    rooms = None
    for tag in tags:
        if re.search("(Кількість кімнат|Количество комнат)", tag):
            rooms = int(re.search("\d+", tag).group(0))
            break

    return rooms


async def get_location(
    url: str, session: ClientSession, origin = "www.olx.ua"
) -> dict | None:
    values = url.split("/")[-1][1:].split("&")
    ad_id = ""

    for v in values:
        if v.find("ad-id") != -1:
            ad_id = v.split("=")[-1]
            break
    else:
        return None
    
    async with session.get(
        f"https://{origin}/api/v1/targeting/data/?page=ad&params[ad_id]={ad_id}"
    ) as response:
        try:
            data = await response.json()
            city_id = data["data"]["targeting"]["city_id"]
        except Exception as ex_:
            logging.error(f"Cannot parse city {url}: {ex_}")
            return None
        
    async with session.get(
        f"https://{origin}/api/v1/geo-encoder/cities/{city_id}/"
    ) as response:
        try:
            data = await response.json()
            location = {
                "city": data["data"].get("name"),
                "municipality": data["data"].get("municipality"),
                "latitude": data["data"].get("latitude"),
                "longitude": data["data"].get("longitude"),
                "olx_city_id": city_id
            }
        except Exception as ex_:
            logging.error(f"Cannot parse city {url}: {ex_}")
            return None
        
    return location


async def parse_category_page(
    url: str, page: int | str = 1, origin: str = "www.olx.ua"
) -> list[dict[str, str | bool]]:
    logging.info(f"Start parse page {url}")

    data = []

    async with ClientSession(
        headers={"Accept-Language":"uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3"}
    ) as session: 
        async with session.get(f"{url}/?page={page}") as response:
            text = await response.text()
            soup = bs4.BeautifulSoup(text, "lxml")
            ads = soup.select("div.css-qfzx1y")
        
            for ad in ads:
                link = ad.select_one("a.css-z3gu2d").get("href")
                boosted = bool(ad.select_one("div.css-1jh69qu"))
                metainfo = ad.select_one("p.css-1a4brun.er34gjf0").text
                metainfo = metainfo.split("-")
                location = metainfo[0]
                _, time = check_time(metainfo[-1])
                location = location.split(",") + [None]
                city = location[0]
                street = location[1]

                data.append({
                    "link": f"https://{origin}{link}", 
                    "boosted": boosted,
                    "location": {
                        "city": city.strip() if city else city,
                        "street": street.strip() if street else street
                    },
                    "published": time
                })
                
    logging.info(f"Finish parse page {url}")

    return data


async def parse_ad_page(url: str, origin: str = "www.olx.ua"):
    logging.info(f"Start parse page {url}")

    async with ClientSession(
        headers={"Accept-Language":"uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3"}
    ) as session:
        async with session.get(url) as response:
            text = await response.text()
            soup = bs4.BeautifulSoup(text, "lxml")

            navs = [nav.text for nav in soup.select("li.css-7dfllt")]
            name = soup.select_one("h4.css-1juynto").text
            imgs = [img.get("src") for img in soup.select("img.css-1bmvjcs")]
            price = soup.select_one("h3.css-12vqlj3").text
            price = set_price(price)
            salesman = soup.select_one("h4.css-1lcz6o7.er34gjf0").text
            salesman_page = soup.select_one("a.css-eaigk1").get("href")
            published = soup.select_one("span.css-19yf5ek").text
            tags = [tag.text for tag in soup.select("li.css-1r0si1e")]
            size = set_size(tags)
            rooms = set_rooms(tags)
            description = soup.select_one("div.css-1t507yq.er34gjf0").text

            if published.lower().find("сьогодні") != -1:
                published = datetime.now().strftime("%d.%m.%y")

            data = {
                "navs": navs,
                "name": name,
                "images": imgs,
                "price": price,
                "salesman": salesman,
                "salesman_page": f"https://{origin}{salesman_page}",
                "published": published,
                "tags": tags,
                "description": description,
                "size": size,
                "rooms": rooms
            }

    logging.info(f"Finish parse page {url}")

    return data


async def parse(
    url: str, 
    path: str, 
    collection = None, 
    deley: tuple[int] = (3, 5),
    insert_by_step = False
):
    logging.info("Start parser")

    dataset = await parse_category_page(url)

    for data in dataset:
        try:
            page_data = await parse_ad_page(data["link"])
            data |= page_data

            if insert_by_step and collection is not None:
                await collection.insert_one(data)
        except Exception as ex_:
            logging.error(f"Get error on {data['link']}: {ex_}")

        await asyncio.sleep(random.randint(*deley))

    logging.info("Save data")

    try:
        if not insert_by_step and collection is not None:
            await collection.insert_many(dataset)

        with open(path, "w") as fp:
            json.dump(dataset, fp, indent=4, ensure_ascii=False)
    except Exception as ex_:
        logging.error(f"Error on save data: {ex_}")

    logging.info("Finish parser")


async def main():
    logging.basicConfig(
        format='%(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    client = mtr.AsyncIOMotorClient(DBURL)
    db = client[DBNAME]

    for i in range(1, 26):
        await parse(
            f"{URL}/?page={i}", 
            f"parsed/data{i}.json", 
            db.apartments, 
            insert_by_step=True
        )


if __name__ == "__main__":
    asyncio.run(main())