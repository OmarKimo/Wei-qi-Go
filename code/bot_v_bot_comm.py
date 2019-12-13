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

ReceivedMssg = None
#---------------------------------------------------------------------------


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
    myPlayer = gotypes.Player.white
    otherPlayer = gotypes.Player.black

    while True:
       
        recvdmssg = socket1.recv()
        print(f"< BOT RECEIVED !!!! {recvdmssg}")

        if ( recvdmssg.__eq__("sendyourmove")):
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
        elif(recvdmssg["type"].__eq__("START")):
            gameConfg = recvdmssg["configuration"]
            color = recvdmssg["color"]
            if color == "B":
                myPlayer, otherPlayer = otherPlayer, myPlayer
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
        elif(recvdmssg["type"].__eq__("MOVE")):
            move = recvdmssg["move"]
            otherMove = goboard.Move()
            if move['type'] == "pass":
                otherMove.is_pass = True
            elif move['type'] == "resign":
                otherMove.is_resign = True
            elif move['type'] == "place":
                otherMove.is_play = True
                otherMove.point = gotypes.Point(row= move['point']['row'], col= move['point']['col'])
            game = game.apply_move(otherMove)
            
                

    

#------------------------------------------------------------------------------


def main():
  
    thread2 = myThread(1, "Thread2", 1)
    # thread2.setDaemon(True)
    thread2.start()



if __name__ == '__main__':
    main()
