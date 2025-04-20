import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from datetime import datetime
import time
import requests

# === Fonction pour envoyer l'alerte sur Discord ===
def send_discord_alert(message):
    webhook_url = "https://discord.com/api/webhooks/1363203250316120124/FqC2sAT6rR3u7_tlyTrraVBuc_iBFkAfgudIWbSN1kKFWYMlVmEE23AyY-v4FmCYarsM"
    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("✅ Alerte envoyée sur Discord !")
        else:
            print("⚠️ Erreur Discord :", response.text)
    except Exception as e:
        print("❌ Erreur Discord :", e)

print("✅ Bot lancé avec Yahoo Finance !")

# === Paramètres des actifs à surveiller ===
assets = {
    "NASDAQ": {
        "ticker": "NDX",
        "rsi_seuils": (30, 69),
        "prix_alertes": []
    },
    "VIX": {
        "ticker": "^VIX",
        "rsi_seuils": (40, 70),
        "prix_alertes": [60, 33, 25, 15, 12, 9]
    },
    "US10Y": {
        "ticker": "^TNX",
        "rsi_seuils": (30, 70),
        "prix_alertes": [4.200, 4.400, 3.360, 4.000, 4.700, 2.000]
    }
}

# === Boucle de surveillance continue ===
while True:
    print(f"\n🔄 Vérification à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for name, data in assets.items():
        try:
            ticker = data["ticker"]
            df = yf.download(ticker, period="2mo", interval="1d", progress=False)

            # Récupération du dernier prix
            close = df["Close"].squeeze().iloc[-1]

            # Calcul RSI
            rsi = RSIIndicator(close=df["Close"].squeeze()).rsi().iloc[-1]

            print(f"\n📈 {name}")
            print(f"RSI: {rsi:.2f}")
            print(f"Prix actuel: {close:.3f}")

            # Vérification RSI
            bas, haut = data["rsi_seuils"]
            if rsi < bas:
                send_discord_alert(f"🔻 {name} : RSI sous {bas} !")
            elif rsi > haut:
                send_discord_alert(f"🔺 {name} : RSI au-dessus de {haut} !")

            # Vérification des prix cibles
            for seuil in data["prix_alertes"]:
                if abs(close - seuil) < 0.01:
                    send_discord_alert(f"🚨 {name} : prix a touché {seuil} !")

        except Exception as e:
            print(f"❌ Erreur pour {name} :", e)

    print("⏳ Attente 10 minutes avant la prochaine vérif...")
    time.sleep(600)
