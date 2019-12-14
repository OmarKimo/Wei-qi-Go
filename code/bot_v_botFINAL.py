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
    # global game
    ClienPortNumber = "8500"
    context = zmq.Context()
    socket1 = context.socket(zmq.REP)
    socket1.bind("tcp://*:%s" % ClienPortNumber)

    fast_policy = load_prediction_agent(h5py.File('test_alphago_sl_policy.h5', 'r'))
    strong_policy = load_policy_agent(h5py.File('test_alphago_rl_policy.h5', 'r'))
    value = load_value_agent(h5py.File('test_alphago_value.h5', 'r'))
    alphago = AlphaGoMCTS(strong_policy, fast_policy, value)
    # board_size as input
    board_size = 19
    game = goboard.GameState.new_game(board_size)

    print("BOT IS OPEN FOR BUSINESS------------")

    bots = alphago

    while True:
       
        recvdmssg = socket1.recv()
        print(f"< BOT RECEIVED ----------------------------------- {recvdmssg}")
        recvdmssg = json.loads(recvdmssg)
       
        if (recvdmssg["type"] == "moverequest"):
            # global game
            print(f"< BOT RECEIVED !!!! {recvdmssg}")
            bot_move = bots.select_move(game)
            sentmssg={}
            if(bot_move.is_pass):
                sentmssg["type"]="pass"
            elif(bot_move.is_resign):
                sentmssg["type"]="resign"
            else :
                sentmssg["type"]="place"
                sentmssg["point"]={"row": bot_move.point.row-1,"column": bot_move.point.col-1}

            print(f"sening: {sentmssg['point']}")
            print(f"BOT IS SENDING -----------: {sentmssg}")
            socket1.send_string(json.dumps(sentmssg))
            # if(game.is_valid_move(bot_move)):
            game = game.apply_move(bot_move)
                

       
        elif ( recvdmssg["type"] == "opponentmove" ) :  # messge is a Opponentmove;
            OpponentMove = recvdmssg["value"]
            print(f"BOT RECEIVED Opponent Move ----- {OpponentMove}")
            socket1.send_string(f"BOT RECEIVED opponent Move {OpponentMove}")
            opmove = goboard.Move()
            if OpponentMove['type'] == "pass":
                opmove = opmove.pass_turn()
            elif OpponentMove['type'] == "resign":
                opmove = opmove.resign()
            elif OpponentMove['type'] == "place":
                opmove = opmove.play(gotypes.Point(row= OpponentMove['point']['row'] + 1, col= OpponentMove['point']['column'] + 1))
            if(game.is_valid_move(opmove)):
                game = game.apply_move(opmove)

        elif ( recvdmssg["type"] == "config" ) :  # messge is a configuration;
            # game = goboard.GameState.new_game(board_size)
            configuration = recvdmssg["value"]
            print(f"BOT RECEIVED YOUT CONFIGURATION -----")
            socket1.send_string("BOT RECEIVED YOUT CONFIGURATION")
            
            gameState = configuration["initialState"]
            board = gameState['board']
            # statePlayerW = gameState['players']['W']
            # statePlayerB = gameState['players']['B']
            turn = gameState['turn']
            moveLog = configuration["moveLog"]
            komi = configuration['komi']
            ko = configuration['ko']
            # prisonerScore = gameConfg["prisonerScore"]
            game.ko = ko
            game.komi = komi
            nextPlayer = gotypes.Player.white
            if turn == "B":
                nextPlayer = gotypes.Player.black
            game.next_player = nextPlayer
            game = getGameState(moveLog,game) #return gamestate
            # for i in range(19):
            #     for j in range(19):
            #         color = None
            #         if board[i][j] == "B":
            #             color = gotypes.Player.black
            #         elif board[i][j] == "W":
            #             color = gotypes.Player.black
            #         game.board._grid[gotypes.Point(row=i+1, col=j+1)] = color
            
            # for move in moveLog:
            #     botMove = goboard.Move()
            #     if move['type'] == "pass":
            #         botMove.pass_turn()
            #     elif move['type'] == "resign":
            #         botMove.resign()
            #     elif move['type'] == "place":
            #         botMove.play(gotypes.Point(row= move['point']['row'] + 1, col= move['point']['col'] + 1))
            #     game = game.apply_move(botMove)
            print(f"Game= {game}")
        else :
            print(f'Unknown Mssg Received --- {recvdmssg}')




def getGameState(movelog,game):
    # global G
    # G=game
    for moveL in movelog:
        M = goboard.Move() #init move
        move = moveL["move"]
        print(f"moveL: {move}")
        if(move["type"] == "pass"):
            M= M.pass_turn()
            # G = G.apply_move(M) 
        elif(move["type"] == "resign"):
            M= M.resign()
            # G = G.apply_move(M) 
        elif(move["type"] == "place"):
            #init point
            P = goboard.Point(move["point"]["row"]+1,move["point"]["column"]+1)
            M= M.play(P)
            print(f"move chooses: {M}")
        if(game.is_valid_move(M)):
            game = game.apply_move(M) 

    return game

#------------------------------------------------------------------------------

def main():
  
    thread2 = myThread(1, "Thread2", 1)
    # thread2.setDaemon(True)
    thread2.start()



if __name__ == '__main__':
    main()
