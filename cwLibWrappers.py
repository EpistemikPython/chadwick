##############################################################################################################################
# coding=utf-8
#
# cwLibWrappers.py -- Chadwick baseball library wrappers for Python3
#
# based on source code by Ben Dilday for the pychadwick project
# https://github.com/bdilday/pychadwick
#
# Copyright (c) 2019-2021 Mark Sattolo <epistemik@gmail.com>

__author__       = "Mark Sattolo"
__author_email__ = "epistemik@gmail.com"
__created__ = "2019-11-07"
__updated__ = "2021-01-31"

from ctypes import c_void_p
from pychadwick.box import CWBoxPlayer, CWBoxPitcher, CWBoxscore
from pychadwick.chadwick import *
from pychadwick.roster import CWPlayer

chadwick = Chadwick()
cwlib = chadwick.libchadwick


class MyCwlib:
    # char * cw_game_info_lookup(CWGame * game, char * label)
    @staticmethod
    def game_info_lookup(game_ptr:POINTER(CWGame), label:bytes) -> str:
        logging.debug("\n MyCwlib.game_info_lookup():\n-------------------------")
        func = cwlib.cw_game_info_lookup
        func.restype = c_char_p
        func.argtypes = (POINTER(CWGame), c_char_p,)
        result = func(game_ptr, label)
        return result.decode(encoding='UTF-8')

    # void cw_game_write(CWGame *game, FILE *file)
    @staticmethod
    def game_write(game_ptr:POINTER(CWGame), file_ptr:c_void_p):
        logging.debug("\n MyCwlib.game_write():\n-------------------------")
        func = cwlib.cw_game_write
        func.restype = None
        func.argtypes = (POINTER(CWGame), c_void_p,)
        return func(game_ptr, file_ptr)

    # CWGameIterator *cw_gameiter_create(CWGame *game)
    @staticmethod
    def gameiter_create(game_ptr:POINTER(CWGame)) -> POINTER(CWGameIterator):
        logging.debug("\n MyCwlib.gameiter_create():\n-------------------------")
        func = cwlib.cw_gameiter_create
        func.restype = POINTER(CWGameIterator)
        func.argtypes = (POINTER(CWGame),)
        return func(game_ptr)

    # CWBoxscore *cw_box_create(CWGame *game)
    @staticmethod
    def box_create(game_ptr:POINTER(CWGame)) -> POINTER(CWBoxscore):
        logging.debug("\n MyCwlib.box_create():\n-------------------------")
        func = cwlib.cw_box_create
        func.restype = POINTER(CWBoxscore)
        func.argtypes = (POINTER(CWGame),)
        return func(game_ptr)

    # CWRoster *cw_roster_create(char *team_id, int year, char *league, char *city, char *nickname)
    @staticmethod
    def roster_create(team:str, year:int, league:str, city:str, nickname:str) -> POINTER(CWRoster):
        logging.debug("\n MyCwlib.roster_create():\n-------------------------")
        bteam = bytes(team, "utf8")
        bleague = bytes(league, "utf8")
        bcity = bytes(city, "utf8")
        bnickname = bytes(nickname, "utf8")

        func = cwlib.cw_roster_create
        func.restype = POINTER(CWRoster)
        func.argtypes = (c_char_p, c_int, c_char_p, c_char_p, c_char_p,)
        return func(bteam, year, bleague, bcity, bnickname)

    # int cw_roster_read(CWRoster *roster, FILE *file)
    @staticmethod
    def roster_read(roster_ptr:POINTER(CWRoster), file_handle:c_void_p) -> int:
        logging.debug("\n MyCwlib.roster_read():\n-------------------------")
        func = cwlib.cw_roster_read
        func.restype = c_int
        func.argtypes = (POINTER(CWRoster), c_void_p,)
        return func(roster_ptr, file_handle)

    # CWPlayer *cw_roster_player_find(CWRoster *roster, char *player_id)
    @staticmethod
    def roster_player_find(roster_ptr:POINTER(CWRoster), player_id:bytes) -> POINTER(CWPlayer):
        logging.debug("\n MyCwlib.roster_player_find():\n-------------------------")
        func = cwlib.cw_roster_player_find
        func.restype = POINTER(CWPlayer)
        func.argtypes = (POINTER(CWRoster), c_char_p,)
        return func(roster_ptr, player_id)

    # CWBoxPlayer *cw_box_get_starter(CWBoxscore *boxscore, int team, int slot)
    @staticmethod
    def box_get_starter(box_ptr:POINTER(CWBoxscore), team:int, slot:int) -> POINTER(CWBoxPlayer):
        logging.debug(" MyCwlib.box_get_starter():\n-------------------------")
        func = cwlib.cw_box_get_starter
        func.restype = POINTER(CWBoxPlayer)
        func.argtypes = (POINTER(CWBoxscore), c_int, c_int,)
        return func(box_ptr, team, slot)

    # CWBoxPitcher *cw_box_get_starting_pitcher(CWBoxscore *boxscore, int team)
    @staticmethod
    def box_get_starting_pitcher(box_ptr:POINTER(CWBoxscore), team:int) -> POINTER(CWBoxPitcher):
        logging.debug("\n MyCwlib.box_get_starting_pitcher():\n-------------------------")
        func = cwlib.cw_box_get_starting_pitcher
        func.restype = POINTER(CWBoxPitcher)
        func.argtypes = (POINTER(CWBoxscore), c_int,)
        return func(box_ptr, team)
# END class MyCwlib
