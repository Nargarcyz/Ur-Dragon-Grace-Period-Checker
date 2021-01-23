from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image, ImageDraw
from requests import get
import PySimpleGUI as sg
from datetime import datetime
from threading import Timer

autoQuery = True
customQueryInterval = 5
queryThread = None


def toggleAutoQuery(icon, item):
    global autoQuery
    autoQuery = not item.checked


# Setups the API check to be at the same time as the API updates
def querySetup(icon):
    global queryThread
    icon.visible = True
    response = get("https://ddda.lennardf1989.com/api/v2/grace/Steam")
    if response.status_code == 200:
        lastTime = str(response.json()["timestamp"].split("T")[1][0:-5]).split(":")[1]
        currentTime = str(str(datetime.now().time()).split(".")[0]).split(":", 1)[1]
        nextTime = (
            5 * 60
            - (int(currentTime.split(":")[0]) - int(lastTime)) * 60
            - int(currentTime.split(":")[1])
        )
        print(lastTime)
        print(currentTime)
        print(nextTime)
        queryThread = Timer(nextTime, queryCheck, [icon])
        queryThread.start()

    else:
        queryThread = Timer(customQueryInterval * 60, queryCheck, [icon])
        queryThread.start()


# API check on an interval, threaded
def queryCheck(icon):
    global queryThread
    print("Querying API")
    response = get("https://ddda.lennardf1989.com/api/v2/grace/Steam")
    if response.status_code == 200:
        responseData = response.json()
        print(responseData)
        if responseData["grace"] == "yes":
            time = responseData["timestamp"]
            icon.notify(
                "The Ur-Dragon is in grace period, go kill him Arisen!\nLast update: "
                + str(time.split("T")[1][0:-4])
                + ", "
                + str(time.split("T")[0]),
                "Ur-Dragon in grace period! ("
                + str(responseData["platform"])
                + ", Generation "
                + str(responseData["generation"])
                + ")",
            )
    queryThread = Timer(customQueryInterval * 60, queryCheck, [icon])
    queryThread.start()


# Manual API check
def checkGrace(icon, item):
    response = get("https://ddda.lennardf1989.com/api/v2/grace/Steam")
    print(response)
    if response.status_code == 200:
        responseData = response.json()
        print(responseData)
        if responseData["grace"] == "yes":
            time = responseData["timestamp"]
            icon.notify(
                "The Ur-Dragon is in grace period, go kill him Arisen!\nLast update: "
                + str(time.split("T")[1][0:-4])
                + ", "
                + str(time.split("T")[0]),
                "Ur-Dragon in grace period! ("
                + str(responseData["platform"])
                + ", Generation "
                + str(responseData["generation"])
                + ")",
            )
        else:
            icon.notify(
                "The Ur-Dragon is not in grace period, keep hacking away!",
                "Nothing yet...",
            )
    else:
        icon.notify(
            "Failed to request the Ur-Dragon's grace state",
            "Request failed.",
        )


# Exits the program
def exitProgram(icon, item):
    global queryThread
    queryThread.cancel()
    icon.stop()


# Creates an image for the tray icon
def create_image():
    width = height = 100

    color1 = (255, 100, 0)
    color2 = (255, 255, 0)
    # Generate an image and draw a pattern
    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)

    return image


# Creates a window for the user to input the new interval for checking the API
def updateQueryInterval(icon, item):
    global queryThread, customQueryInterval
    queryLayout = [
        [sg.Text("Input query interval in minutes")],
        [sg.Input()],
        [sg.Button("Ok")],
    ]
    queryWindow = sg.Window("Set Query Interval", queryLayout)
    while True:
        event, values = queryWindow.read()
        if event == sg.WINDOW_CLOSED:
            queryWindow.close()
            return
        elif event == "Ok":
            print(values[0])
            customQueryInterval = float(values[0])
            queryThread.cancel()
            queryThread = Timer(customQueryInterval * 60, queryCheck, [icon])
            queryThread.start()
            queryWindow.close()
            return


# Creates the tray icon and its menu
icon(
    "test",
    create_image(),
    menu=menu(
        item("Check Grace", checkGrace, checked=None),
        item("Toggle Auto-Query", toggleAutoQuery, checked=lambda item: autoQuery),
        item("Edit Auto-Query", updateQueryInterval, checked=None),
        item("Quit", exitProgram, checked=None),
    ),
).run(setup=lambda icon: querySetup(icon))
