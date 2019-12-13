import json
import asyncio
import websockets
import concurrent.futures
import time
import zmq
import sys
import threading

states = {
    "INIT": 0,
    "READY": 1,
    "THINKING": 2,
    "AWAITING_MOVE_RESPONSE": 3,
    "IDLE": 4
}

#----------------------------------------------GLOBAL Varibles----------------------------------------------


name = "GoCHI"
url = "ws://localhost:8080"

websocket = None
my_color = None
ClientState = states["INIT"]
isActionNeeded = False
OpponentMove = None
RequestedMove = None

SendMssg = None
ClienPortNumber = "8500"
GoThinkToken = False

socket2 = None
ClientGameConfiguration = None

#----------------------------------------------GLOBAL Varibles----------------------------------------------

def mInitConnectionWithBot(clientno):
    global RequestedMove
    global GoThinkToken 
    global socket2
    global OpponentMove
    global ClientGameConfiguration

    print(f"initiaing the connection With Bot")

    # if (clientno == 1):
    #     ClienPortNumber = "8500"

    # else : ClienPortNumber = "9000"

    context = zmq.Context()
    socket2 = context.socket(zmq.REQ)
    socket2.connect("tcp://localhost:%s" % ClienPortNumber)


    while True:
        
        if (GoThinkToken):
            template = "sendyourmove"
            SendMssgToBot = {
                "type" : "moverequest",
                "value" : template
            }
            socket2.send_string(json.dumps(SendMssgToBot))
            finaaaaaaaaaaaalrslt = socket2.recv()

            RequestedMove = { "type": "MOVE", "move": json.loads(finaaaaaaaaaaaalrslt) }
            GoThinkToken = False

        # if ( ClientGameConfiguration != None):
        #     template = ClientGameConfiguration
        #     SendMssgToBot = {
        #         "type" : "config",
        #         "value" : template
        #     }
        #     socket2.send_string(json.dumps(SendMssgToBot))
        #     print (socket2.recv())
        #     ClientGameConfiguration = None

        # if ( OpponentMove != None):
        #     template = OpponentMove
        #     SendMssgToBot = {
        #         "type" : "opponentmove",
        #         "value" : template
        #     }
        #     socket2.send_string(json.dumps(SendMssgToBot))
        #     print (socket2.recv())
        #     OpponentMove = None

    
class myThread (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter

   def run(self):
        mInitConnectionWithBot(self.threadID)


async def blocking_to_async(func, *args):
    result = await asyncio.wait(fs={
        asyncio.get_event_loop().run_in_executor(
            concurrent.futures.ThreadPoolExecutor(1),
            func, *args
        )
    })
    return_val = tuple(element.result() for element in tuple(result[0]))
    return return_val[0] if len(return_val) == 1 else return_val


async def dummy():
    global GoThinkToken
    GoThinkToken = True


def send_valid(valid, remaning_time, message=""):
    pass


def send_opponent_move(type, X, Y, time):
    pass


def send_score(reason, winner, B_score, B_time, W_score, W_time):
    pass


async def handle_init():
    global websocket, ClientState
    # connect to server
    websocket = await websockets.connect(url, ping_interval=0.5)
    msg = await websocket.recv()
    msg = json.loads(msg)
    if msg["type"].lower() == "name":
        msg = json.dumps({"type": "NAME", "name": name})
        await websocket.send(msg)
        ClientState = states["READY"]
    elif msg["type"] == "END":
        handle_end(msg)


async def handle_ready():
    global ClientState, my_color, websocket,ClientGameConfiguration
    print("now handling ready")
    msg = await websocket.recv()
    print("received", msg)
    msg = json.loads(msg)
    if msg["type"] == "START":
        color = msg["configuration"]["initialState"]["turn"]
        for log_entry in msg["configuration"]["moveLog"]:
            msg["configuration"]["initialState"]["players"][color]["remainingTime"] -= log_entry["deltaTime"]
            color = "B" if color == "W" else "W"
        color = msg["configuration"]["initialState"]["turn"]
        log_entries = []
        for log_entry in msg["configuration"]["moveLog"]:
            entry = {"type": log_entry["move"]["type"], "color": color}
            if entry["type"] == "place":
                entry["point"] = log_entry["move"]["point"]
            log_entries.append(entry)
            color = "B" if color == "W" else "W"
        # log_entries = [x for x in log_entries if x["type"] != "pass"]
        #board - movelog - color - rt for both
        if (msg["color"] == msg["configuration"]["initialState"]["turn"] and len(msg["configuration"]["moveLog"]) % 2 == 0) or (msg["color"] != msg["configuration"]["initialState"]["turn"] and len(msg["configuration"]["moveLog"]) % 2 != 0):
            ClientState = states["THINKING"]
            my_color = msg["color"]
        else:
            ClientState = states["IDLE"]
            my_color = "B" if msg["color"] == "W" else "W"
        
        ClientGameConfiguration = msg["configuration"]
        


    elif msg["type"] == "END":
        handle_end(msg)


def handle_end(msg):
    global ClientState
    print("END GAME reason is " + msg['reason'])
    send_score(reason=msg['reason'], winner=msg['winner'], B_score=msg['players']["B"]["score"], B_time=msg['players']
               ["B"]["remainingTime"], W_score=msg['players']["W"]["score"], W_time=msg['players']["W"]["remainingTime"])
    ClientState = states["READY"]


async def handle_thinking():
    global ClientState, websocket

    msg = json.dumps(RequestedMove)
    await websocket.send(msg)
    ClientState = states["AWAITING_MOVE_RESPONSE"]

        



async def handle_await_response():
    global ClientState, websocket
    msg = await websocket.recv()
    msg = json.loads(msg)
    if msg["type"] == "VALID": #rt  for both
        # send_valid(valid=True, remaning_time=msg["remainingTime"])
        ClientState = states["IDLE"]

    elif msg["type"] == "INVALID":
        # send_valid(
        #     valid=False, remaning_time=msg["remainingTime"], message=msg["message"])
        ClientState = states["THINKING"]
    elif msg["type"] == "END":
        handle_end(msg)


async def handle_idle():
    global ClientState, websocket,OpponentMove
    msg = await websocket.recv()
    msg = json.loads(msg) #rt for both
    if msg["type"] == "MOVE":
        OpponentMove =  msg["move"]
      
        ClientState = states["THINKING"]
    elif msg["type"] == "END":
        handle_end(msg)


async def main():
    global ClientState,GoThinkToken,RequestedMove,websocket
    while True:
        try:
            if ClientState == states["INIT"]:
                await handle_init()
            elif ClientState == states["READY"]:
                await handle_ready()
            elif ClientState == states["THINKING"]:
                GoThinkToken = True
                await websocket.pong()
                if ( RequestedMove != None ):
                    await (handle_thinking())
                    RequestedMove = None
                    GoThinkToken = False
            elif ClientState == states["AWAITING_MOVE_RESPONSE"]:
                await handle_await_response()
            elif ClientState == states["IDLE"]:
                await handle_idle()
        except Exception as e:
            print("type error: " + str(e))
            ClientState = states["INIT"]


if __name__ == "__main__":
    thread1 = myThread(1, "Thread1", 1)
    thread1.setDaemon(True)
    thread1.start() 
    asyncio.run(main())
