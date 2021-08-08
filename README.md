# kasabulb-crypto-light
Allows you to input a kasa lightbulb ip and control it to turn green or red depending on the cryptocurrency's price

This allows you to continuously change the color of certain Kasa lights (see compatibility list below) depending on the price of a cryptocurrency with the use of FastAPI and python-kasa.

In order to use this, we first have to run the FastAPI server. 
This can be done using command prompt and navigating to the folder, running the command: uvicorn bulb:app --reload. 

Then, we open the webpage labeled as main.html. Here, we see a form where we can input some data such as our lights ip address, which crypto we want to check (currently have the top 30 listed), and how often we want it to update the light (1 or 24 hours). Once we hit submit, our light will change once API data is received!


https://github.com/python-kasa/python-kasa
Plugs
    HS100
    HS103
    HS105
    HS107
    HS110
    
Power Strips
    HS300
    KP303
    KP400

Wall switches
    HS200
    HS210
    HS220

Bulbs
    LB100
    LB110
    LB120
    LB130
    LB230
    KL60
    KL110
    KL120
    KL125
    KL130

Light strips
    KL430
