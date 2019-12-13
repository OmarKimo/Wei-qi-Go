from __future__ import print_function
# tag::bot_vs_bot[]
from dlgo import agent
from dlgo import goboard_fast as goboard
from dlgo import gotypes
from dlgo.utils import print_board, print_move
from dlgo.agent import load_prediction_agent, load_policy_agent, AlphaGoMCTS
from dlgo.rl import load_value_agent
from dlgo.encoders.alphago import AlphaGoEncoder
from dlgo.networks.alphago import alphago_model
from dlgo.agent.predict import DeepLearningAgent
import time
import h5py
import numpy as np
# from clientcommunication import * 
import websockets
import json
import asyncio
import zmq
import sys
import threading

#----------------------REMOVE------------------------------------
import random
import time

move = []
point = None
move1 = {"type": "pass"}
move2 = {"type": "resign"}
move3 = {
    "type": "place",
    "point" : point
}
move.append(move1)
move.append(move2)
move.append(move3)
#---------------------------------------------------------------------------
ReceivedMssg = None
#---------------------------------------------------------------------------

# <1> We set a sleep timer to 0.3 seconds so that bot moves aren't printed too fast to observe
# <2> Before each move we clear the screen. This way the board is always printed to the same position on the command line.
# end::bot_vs_bot[]

class myThread (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter

   def run(self):
        print(f"intering the Thread")
        mInitConnectionWithClient()


def mInitConnectionWithClient():
    ClienPortNumber = "8500"
    context = zmq.Context()
    socket1 = context.socket(zmq.REP)
    socket1.bind("tcp://*:%s" % ClienPortNumber)

    print("BOT IS OPEN FOR BUSINESS------------")

    fast_policy = load_prediction_agent(h5py.File('test_alphago_sl_policy.h5', 'r'))
    strong_policy = load_policy_agent(h5py.File('test_alphago_rl_policy.h5', 'r'))
    value = load_value_agent(h5py.File('test_alphago_value.h5', 'r'))
    alphago = AlphaGoMCTS(strong_policy, fast_policy, value)
    # board_size as input
    board_size = 19
    game = goboard.GameState.new_game(board_size)
    bots = alphago
    gameConfg = {}
	
    while True:
       
        recvdmssg = socket1.recv()
        print(f"< BOT RECEIVED ----------------------------------- {recvdmssg}")
        recvdmssg = json.loads(recvdmssg)
       

        if ( recvdmssg["type"] == "moverequest"):
            print(f"< BOT RECEIVED !!!! {recvdmssg}")
            # sentmssg= createmove()
            bot_move = bots.select_move(game)
            sentmssg={}
            if(bot_move.is_pass):
                sentmssg["type"]="pass"
            elif(bot_move.is_resign):
                sentmssg["type"]="resign"
            else :
                sentmssg["type"]="place"
                sentmssg["point"]={"row": bot_move.point.row,"column": bot_move.point.col}

            print(f"sening: {sentmssg['point']}")
            print(f"BOT IS SENDING -----------: {sentmssg}")
            socket1.send_string(json.dumps(sentmssg))
            game = game.apply_move(bot_move)

        elif ( recvdmssg["type"] == "config" ) :  # messge is a configuration;
            gameConfg = recvdmssg["value"]
            print(f"BOT RECEIVED YOUT CONFIGURATION -----")

            gameState = gameConfg["initialState"]
            board = gameState['board']
            # statePlayerW = gameState['players']['W']
            # statePlayerB = gameState['players']['B']
            turn = gameState['turn']
            moveLog = gameConfg["moveLog"]
            komi = gameConfg['komi']
            ko = gameConfg['ko']
            # prisonerScore = gameConfg["prisonerScore"]
            game.ko = ko
            game.komi = komi
            for i in range(19):
                for j in range(19):
                    color = None
                    if board[i][j] == "B":
                        color = gotypes.Player.black
                    elif board[i][j] == "W":
                        color = gotypes.Player.black
                    game.board._grid[gotypes.Point(row=i+1, col=j+1)] = color
            nextPlayer = gotypes.Player.white
            if turn == "B":
                nextPlayer = gotypes.Player.black
            game.next_player = nextPlayer
            for move in moveLog:
                botMove = goboard.Move()
                if move['type'] == "pass":
                    botMove.is_pass = True
                elif move['type'] == "resign":
                    botMove.is_resign = True
                elif move['type'] == "place":
                    botMove.is_play = True
                    botMove.point = gotypes.Point(row= move['point']['row'], col= move['point']['col'])
                game = game.apply_move(botMove)
            socket1.send_string("BOT RECEIVED YOUT CONFIGURATION")

        elif ( recvdmssg["type"] == "opponentmove" ) :  # messge is a Opponentmove;
            OpponentMove = recvdmssg["value"]
            print(f"BOT RECEIVED Opponent Move ----- {OpponentMove}")
            otherMove = goboard.Move()
            if OpponentMove['type'] == "pass":
                otherMove.is_pass = True
            elif OpponentMove['type'] == "resign":
                otherMove.is_resign = True
            elif OpponentMove['type'] == "place":
                otherMove.is_play = True
                otherMove.point = gotypes.Point(row= OpponentMove['point']['row'], col= OpponentMove['point']['col'])
            game = game.apply_move(otherMove)
            socket1.send_string("BOT RECEIVED opponent Move")

        
        else :
            print(f'Unknown Mssg Received --- {recvdmssg}')

#---------------------------------TO BE REMOVED-=------------------------------


def createmove():
    global move
    
    # recvdmssg = json.loads(recvdmssg)
    # if ( recvdmssg.__eq__("sendyourmove")):
        
    y = round(random.uniform(1,3))

    # if ( y.__eq__(1)):
    #     finalmove = move[0]
    #     return finalmove

    # elif ( y.__eq__(2)):
    #     finalmove = move[1]
    #     return finalmove

    finalmove = move[2]
    finalmove = populatePoint(finalmove)
    return finalmove

    # else: ( print ( "ERROR IN MOVE SELECTION"))


def populatePoint(finalmove):
    r = round(random.uniform(0,18))
    c = round(random.uniform(0,18))
    finalmove["point"] = {"row": r , "column": c }
    print (f'sening {finalmove["point"]}')
    time.sleep(1)
    return finalmove

#------------------------------------------------------------------------------


def main():
    # fast_policy = load_prediction_agent(h5py.File('test_alphago_sl_policy.h5', 'r'))
    # strong_policy = load_policy_agent(h5py.File('test_alphago_rl_policy.h5', 'r'))
    # value = load_value_agent(h5py.File('test_alphago_value.h5', 'r'))
    # alphago = AlphaGoMCTS(strong_policy, fast_policy, value)

    # board_size = 19
    # game = goboard.GameState.new_game(board_size)
    # bots = {
    #     gotypes.Player.black: alphago,
    #     gotypes.Player.white: alphago,
    # }
    # while not game.is_over():
        # time.sleep(0.3)  # <1>

        # print(chr(27) + "[2J")  # <2>
        # print_board(game.board)
    thread2 = myThread(1, "Thread2", 1)
    # thread2.setDaemon(True)
    thread2.start()

    # bot_move = bots[game.next_player].select_move(game)
        # print_move(game.next_player, bot_move)
        # game = game.apply_move(bot_move)


if __name__ == '__main__':
    main()
