#Kasa lightbulb and asyncio
import asyncio
from kasa import SmartBulb, SmartDeviceException
from dotenv import load_dotenv
import os

#Colors from colors python file
from colors import GREEN, WHITE, RED

#Time stuff
from time import sleep
import time

#coinmarketcap api stuff
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

#json stuff
import json

#FastAPI stuff
from typing import Coroutine, Optional
from fastapi import FastAPI, Form

#pydantic for request bodies
from pydantic import BaseModel

app = FastAPI()

class KasaBulb(object):
    async def create(ip: str):
        self = KasaBulb()
        self.ip = ip          
        self.bulb = SmartBulb(self.ip)
        self.start_state = {}
        try:
            await self.bulb.update()
            self.start_state['color_temp'] = self.bulb.color_temp
            self.start_state['hsv'] = self.bulb.hsv
            print(f"Smart bulb '{self.bulb.alias}' connected")  
            print(f"Temp: {self.bulb.color_temp} | HSV: {self.start_state['hsv']}")
        except SmartDeviceException:
            print(f"Failed to connect to bulb at {self.ip}")
        return self

    # https://www.rapidtables.com/convert/color/rgb-to-hsv.html
    @staticmethod
    def rgb_to_hsv(red: int, green: int, blue: int) -> tuple:
        r_ = red / 255
        g_ = green / 255
        b_ = blue / 255
        cmax = max(r_, g_, b_)
        cmin = min(r_, g_, b_)
        delta = cmax - cmin
        
        if delta == 0:
            hue = 0
        elif cmax == r_:
            hue = 60 * (( (g_ - b_) / delta) % 6)
        elif cmax == g_:
            hue = 60 * (( (b_ - r_) / delta) + 2)
        elif cmax == b_:
            hue = 60 * (( (r_ - g_) / delta) + 4)

        if cmax != 0:
            sat = delta / cmax
        else:
            sat = 0

        return (int(hue), int(sat * 100), int(cmax * 100))

    def is_powered(self) -> bool:
        try:
            self.loop.run_until_complete(self.bulb.update())
            return True
        except SmartDeviceException:
            return False

    async def is_on(self) -> bool:
        try:
            await self.bulb.update()
            status = self.bulb.is_on
            return status
        except SmartDeviceException:
            return False

    async def set_rgb(self, red: int, green: int, blue: int):
        hsv = KasaBulb.rgb_to_hsv(red, green, blue)
        try:
            await self.bulb.set_hsv(*hsv)
            print(f"Bulb color set to hsv value: {hsv}")
        except SmartDeviceException:
            print("Failed to set bulb color")

    async def set_scene(self, scene: dict):
        hsv = scene.get('hsv')
        color_temp = scene.get('color_temp')
        rgb = scene.get('rgb')
        try:
            if hsv:
                await self.bulb.set_hsv(*hsv)
            elif hsv is None and rgb is not None:
                await self.bulb.set_hsv(*KasaBulb.rgb_to_hsv(*rgb))
            if color_temp is not None and color_temp != 0:
                await self.bulb.set_color_temp(color_temp)

        except SmartDeviceException:
            print("Failed to set bulb color")

    async def reset_state(self):
        try:
            await self.set_scene(self.start_state)
        except SmartDeviceException:
            print("Failed to set bulb color")

    async def emit_scene(self, scene: dict, delay: int = 1):
        try:
            status = await self.is_on()
            if status:  # only change scene if bulb is on
                await self.set_scene(scene)
                sleep(delay)
                await self.reset_state()
        except SmartDeviceException:
            print("Failed to set bulb color")

def check_coin(coin_symbol): #As of 8/3/2021 6:46PM, there are the top 30 cryptocurrencies from https://coinmarketcap.com/all/views/all/. Perhaps we can add all of them by using the below api call, but maybe in a later implementation
    coinlist = ['BTC','ETH','USDT','BNB','ADA','XRP','USDC','DOGE','DOT','UNI','BUSD','LINK','BCH','LTC','SOL','WBTC','MATIC','XLM','ETC','LUNA','THETA','DAI','VET','ICP','FIL','TRX','XMR','AAVE','EOS','FTT']

    if(coin_symbol in coinlist):
        return True
    else:
        return False

class Crypto(BaseModel): #adding class for pydantic model. Need request body for sending data from web client to API
    symbol: str
    time_option: str 
    bulb_ip: str

@app.post("/test")
async def getinfo(symbol:str = Form(...), bulb_ip:str = Form(...), time_option:str = Form(...)): #default constructor as doge for currency, with a time val of 0.1?
    #TEST
    print("symbol = ", symbol)
    print("time_option = ", time_option)
    print("bulb_ip = ",bulb_ip)

    if time_option == '1':
        print("Refreshing every 1 hour!")
        wait_timer = 3600
    else:
        print("Refreshing every 24 hours!")
        wait_timer = 86400

    if(check_coin(symbol)) == True:
        print("Coin Found! Continuing to request API from coinmarket. This takes a while. Please check FastAPI server.")
        asyncio.create_task(lightloop(wait_timer, symbol, bulb_ip))
        return {"success":"true"}

    else:
        print("Coin not found... Please restart the html page and enter valid symbols.")
        return {"success":"false", "reason":"coin not found"}

def get_coininfo(req_symbol, req_time):

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol':req_symbol,
        'convert':'USD'
        
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'f24cf5df-7e81-4015-add7-773b8ddeaf33',
    }

    try:
        session = Session()  #creating http session
        session.headers.update(headers)
        response = session.get(url, params=parameters) #gets response from using url and its parameters, however we need to turn into json data
        data = json.loads(response.text) #turns response into its json data
        s_symbol = req_symbol

        if req_time == 3600: #req_time of 1 means 1 hour intervals
            print("in req_time == 1, 1 hr interval...")
            coin_data = data["data"][s_symbol]["quote"]["USD"]["percent_change_1h"]
            return coin_data
        elif req_time == 86400: #req_time of 2 means 2 hour intervals
            print("in req_time == 2, 24 hr interval...")
            coin_data = data["data"][s_symbol]["quote"]["USD"]["percent_change_24h"]
            return coin_data
        else:
            print("Error...")
            return(data)
    except:
        print('Error...')

async def lightloop(wait_timer, symbol, bulb_ip):
    try:
        bedroom = await KasaBulb.create(bulb_ip)
    except:
        return "Bulb not found..."

    while True:
        coin_value = get_coininfo(symbol, wait_timer) #Get new coindata. wait for it to prevent errors.
        if coin_value > 0:
            await bedroom.set_scene(GREEN)
            print("Showing Green,", symbol, "is up!")
            time.sleep(wait_timer)
        elif coin_value == 0: #edge case
            await bedroom.set_scene(WHITE)
            print("Showing White,", symbol, "is somehow at exactly 0!")
            time.sleep(wait_timer)
        else: #final case if coindata < 0
            await bedroom.set_scene(RED)
            print("Showing Red,", symbol, "is down!")
            time.sleep(wait_timer)
