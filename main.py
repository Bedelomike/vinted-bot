import asyncio
import os
import re
import aiohttp
from telegram import constants
from telegram.ext import ApplicationBuilder

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
SEARCH_KEYWORD = "Maybelline New York Lash Sensational Sky High"
MAX_UNIT_PRICE = 6.0
VINTED_SEARCH_URL = f"https://www.vinted.fr/vetements?search_text={SEARCH_KEYWORD.replace(' ', '+')}&status_ids[]=1"

async def send_alert(app, title, price, url):
    message = f"🛍️ *{title}*\n💶 {price:.2f} €\n🔗 [Voir sur Vinted]({url})"
    await app.bot.send_message(
        chat_id=TELEGRAM_USER_ID,
        text=message,
        parse_mode=constants.ParseMode.MARKDOWN
    )

async def search_vinted(app):
    async with aiohttp.ClientSession() as session:
        async with session.get(VINTED_SEARCH_URL) as resp:
            html = await resp.text()

            articles = re.findall(r'<a[^>]*href="(/items/\d+[^"]+)"[^>]*>(.*?)</a>', html)
            prices = re.findall(r'price__amount[^>]*">([\d,]+)', html)

            sent = 0
            for i in range(min(len(articles), len(prices))):
                url = "https://www.vinted.fr" + articles[i][0]
                title = re.sub('<[^<]+?>', '', articles[i][1])
                price_text = prices[i].replace(",", ".")
                try:
                    price = float(price_text)
                except:
                    continue

                if price <= MAX_UNIT_PRICE:
                    await send_alert(app, title, price, url)
                    sent += 1

            print(f"✅ {sent} alertes envoyées.")

async def main():
    print("🔁 Démarrage du bot Vinted...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    while True:
        try:
            await search_vinted(app)
        except Exception as e:
            print("❌ Erreur pendant la recherche :", e)
        await asyncio.sleep(600)  # 10 min

if __name__ == "__main__":
    asyncio.run(main())
