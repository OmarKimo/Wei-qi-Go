import websockets
import json
import asyncio
import enum
import zmq
import sys
import threading
import time
import concurrent.futures

# This enum represents the client states
class eClientStates(enum.Enum):
    # The client is initializing the connection with the server
    INIT = 0 
    # The client is ready to start a game
    READY = 1 
    # The client is waiting for the opponent's move
    IDLE = 2 
    # The client is thinking of a move
    THINKING = 3 
    # The client is awaiting the server's response
    # about the move (VALID or INVALID)
    AWAITING_MOVE_RESPONSE = 4 

#----------------------------------------------Varibles----------------------------------------------

# To Be Assigned from the Gui
CLIENT_NAME = "AwesomeClient"
# To Be Assigned from the Gui

PortNumber = 8080
URI = f"ws://localhost:{PortNumber}"     # Default , RUnning on the same Machine

ClienPortNumber = "8500"


#This will store the initial client state
ClientState = eClientStates.INIT

#This will store the initial client state
ClientColor = None

# This will store the requested move, and if the server responds with VALID, it will be verified

ServerTerminationResaon = None
Winner = None
ClientScoreAndTime = None
ClientRemainingTime = 900000
isActionNeeded = False
OpponentMove = None
RequestedMove = None

SendMssg = None

GoThinkToken = False

socket2 = None

#----------------------------------------------Varibles----------------------------------------------



def mInitConnectionWithBot():
    global RequestedMove
    global GoThinkToken 
    global socket2
 
    print(f"initiaing the connection With Bot")

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
            # time.sleep(10)
            finaaaaaaaaaaaalrslt = socket2.recv()

            RequestedMove = json.loads(finaaaaaaaaaaaalrslt)
            GoThinkToken = False
        
    

class myThread (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter

   def run(self):
        mInitConnectionWithBot()


def mClientSendMssg():
    mssg = { "type": "NAME", "name": CLIENT_NAME }
    return mssg


def mClientHandleMssg(ReceivedMssg):
 
    global ClientState
    global isActionNeeded
    global ClientColor
    global ClientScoreAndTime
    global ClientRemainingTime

    ReceivedJsonMssg = json.loads(ReceivedMssg)
    if ( ReceivedJsonMssg["type"].__eq__("NAME") ) :  
        isActionNeeded = True
        

    elif ( ReceivedJsonMssg["type"].__eq__("START") ) :
        ClientColor = ReceivedJsonMssg["color"]
        ClientGameConfiguration = ReceivedJsonMssg["configuration"]

        # socket2.connect("tcp://localhost:%s" % ClienPortNumber)
        template = ClientGameConfiguration
        SendMssgToBot = {
            "type" : "config",
            "value" : template
        }
        socket2.send_string(json.dumps(SendMssgToBot))
        print (socket2.recv())

        if (
            ClientGameConfiguration["initialState"]["turn"] == (ClientColor) and len(ClientGameConfiguration["moveLog"]) % 2 ==0
            or ClientGameConfiguration["initialState"]["turn"] != (ClientColor) and len(ClientGameConfiguration["moveLog"]) % 2 !=0
            ):

            ClientState = eClientStates.THINKING
            isActionNeeded = True

        
        else : 
            ClientState = eClientStates.IDLE
        

    elif ( ReceivedJsonMssg["type"].__eq__("MOVE") ) :# ANother Client Has Made a MOVE
        OpponentMove = ReceivedJsonMssg["move"]
        ClientRemainingTime = ReceivedJsonMssg["remainingTime"]

        # socket2.connect("tcp://localhost:%s" % ClienPortNumber)
        template = OpponentMove
        SendMssgToBot = {
            "type" : "opponentmove",
            "value" : template
        }
        socket2.send_string(json.dumps(SendMssgToBot))
        print (socket2.recv())

        ClientState = eClientStates.THINKING
        isActionNeeded = True


    elif (ReceivedJsonMssg["type"].__eq__("END")) :
        print(f'Handling {ReceivedJsonMssg["type"]} Request...')
        ServerTerminationResaon = ReceivedJsonMssg["reason"]
        if (ServerTerminationResaon.__eq__("error")):
            print("Game Terminated due to Opponent Disconnection.")
        WinnerColor = ReceivedJsonMssg["winner"]
        print(f"Game Winner is {WinnerColor}")
        ClientState = eClientStates.READY

    elif (ReceivedJsonMssg["type"].__eq__("VALID")) :
        ClientRemainingTime = ReceivedJsonMssg["remainingTime"]
        ClientState = eClientStates.IDLE

    elif (ReceivedJsonMssg["type"].__eq__("INVALID")) :
        print(ReceivedJsonMssg["message"])
        ClientRemainingTime = ReceivedJsonMssg["remainingTime"]
        ClientState = eClientStates.THINKING

        isActionNeeded = True


async def mClientServerCommunication():
    global isActionNeeded
    global ClientState
    global RequestedMove
    global GoThinkToken

    ConnectionObject = await websockets.connect(URI,ping_interval=1)

    while True:

        if (isActionNeeded == False):

            SendMssg = None
            # time.sleep(10)
            ReceivedMssg = await ConnectionObject.recv()
            mClientHandleMssg(ReceivedMssg)


        if (isActionNeeded):

            if (ClientState == eClientStates.THINKING):
            
                GoThinkToken = True
                if ( RequestedMove != None ):
                    SendMssg = { "type": "MOVE", "move": RequestedMove }

                    print(f'Sending Message : --------------------------- {SendMssg}..')
                    await ConnectionObject.send(json.dumps(SendMssg))
                    
                    ClientState = eClientStates.AWAITING_MOVE_RESPONSE

                    RequestedMove = None 
                    GoThinkToken = False
                    isActionNeeded = False
                

            elif (ClientState == (eClientStates.INIT))   :
                SendMssg = mClientSendMssg()
               
                print(f'Sending Message : -----------------------------{SendMssg}..')
                await ConnectionObject.send(json.dumps(SendMssg))
                ClientState = eClientStates.READY
                isActionNeeded = False
        
    

def mInitClientServerCommunication():
    asyncio.get_event_loop().run_until_complete(mClientServerCommunication())
    asyncio.get_event_loop().run_forever()


async def mCommunicationHelper(func,*args):
    rslt = await asyncio.wait(fs={
        asyncio.get_event_loop.
        run_in_executor(
            concurrent.futures.ThreadPoolExecutor(1),
            func,*args
        )
    })

    funcRet = tuple(elem.result() for elem in tuple(rslt[0]))
    return funcRet[0] if len(funcRet) == 1 else funcRet


def main():
    # Print some info to the user
    print(f'Name: {CLIENT_NAME}')
    print(f'Connecting to Uri :  {URI}')
    print(f'Starting Main Funcion...')
    
    thread1 = myThread(1, "Thread1", 1)
    thread1.setDaemon(True)
    thread1.start() 
    # mCommunicationHelper()
    mInitClientServerCommunication()


if __name__ == "__main__":
    main()