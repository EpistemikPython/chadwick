##############################################################################################################################
# coding=utf-8
#
# cwLibWrappers.py -- Chadwick baseball library wrappers for Python3
#
# The data processed by this software was obtained free of charge from and is copyrighted by Retrosheet.
# Interested parties may contact Retrosheet at 20 Sunset Rd., Newark, DE 19711.
#
# Original C code Copyright (c) 2002-2021
# Dr T L Turocy, Chadwick Baseball Bureau (ted.turocy@gmail.com)
#
# based on source code by Ben Dilday for the pychadwick project
# https://github.com/bdilday/pychadwick
#
# Copyright (c) 2019-2021 Mark Sattolo <epistemik@gmail.com>

__author__       = "Mark Sattolo"
__author_email__ = "epistemik@gmail.com"
__created__ = "2019-11-07"
__updated__ = "2021-06-11"

from ctypes import c_void_p
from pychadwick.box import CWBoxPlayer, CWBoxPitcher, CWBoxscore
from pychadwick.chadwick import Chadwick, POINTER, CWRoster, CWGame, c_int, c_char_p
from pychadwick.roster import CWPlayer

chadwick = Chadwick()
cwlib = chadwick.libchadwick


class MyCwlib:
    # char *cw_game_info_lookup(CWGame *game, char *label)
    @staticmethod
    def game_info_lookup(game_ptr:POINTER(CWGame), label:bytes) -> str:
        """
        Scans the info records for 'label' and returns the associated data.
        The pointer returned is internal to the CWGame structure, so it should not be deleted, nor its contents changed.
        The list is scanned from the tail first, to return the last seen record in the case of multiple records.
        """
        func = cwlib.cw_game_info_lookup
        func.restype = c_char_p
        func.argtypes = (POINTER(CWGame), c_char_p,)
        result = func(game_ptr, label)
        return result.decode(encoding='UTF-8')

    # CWRoster *cw_roster_create(char *team_id, int year, char *league, char *city, char *nickname)
    @staticmethod
    def roster_create(team:str, year:int, league:str, city:str, nickname:str) -> POINTER(CWRoster):
        """
        Allocates and initializes a new CWRoster. Roster initially has no players.
        Caller is responsible for memory management of returned pointer.
        """
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
        """
        Read in a roster (in Retrosheet format) from file 'file'.
        Returns nonzero on success, zero on failure.
        """
        func = cwlib.cw_roster_read
        func.restype = c_int
        func.argtypes = (POINTER(CWRoster), c_void_p,)
        return func(roster_ptr, file_handle)

    # CWPlayer *cw_roster_player_find(CWRoster *roster, char *player_id)
    @staticmethod
    def roster_player_find(roster_ptr:POINTER(CWRoster), player_id:bytes) -> POINTER(CWPlayer):
        """
        Finds the record for the player with the given player_id.
        Returns null if the player_id is not on the roster.
        """
        func = cwlib.cw_roster_player_find
        func.restype = POINTER(CWPlayer)
        func.argtypes = (POINTER(CWRoster), c_char_p,)
        return func(roster_ptr, player_id)

    # CWBoxscore *cw_box_create(CWGame *game)
    @staticmethod
    def box_create(game_ptr:POINTER(CWGame)) -> POINTER(CWBoxscore):
        """Create a boxscore from the game 'game'."""
        func = cwlib.cw_box_create
        func.restype = POINTER(CWBoxscore)
        func.argtypes = (POINTER(CWGame),)
        return func(game_ptr)

    # CWBoxPlayer *cw_box_get_starter(CWBoxscore *boxscore, int team, int slot)
    @staticmethod
    def box_get_starter(box_ptr:POINTER(CWBoxscore), team:int, slot:int) -> POINTER(CWBoxPlayer):
        """Find the starter for 'team' in batting order position 'slot'."""
        func = cwlib.cw_box_get_starter
        func.restype = POINTER(CWBoxPlayer)
        func.argtypes = (POINTER(CWBoxscore), c_int, c_int,)
        return func(box_ptr, team, slot)

    # CWBoxPitcher *cw_box_get_starting_pitcher(CWBoxscore *boxscore, int team)
    @staticmethod
    def box_get_starting_pitcher(box_ptr:POINTER(CWBoxscore), team:int) -> POINTER(CWBoxPitcher):
        """Find the starting pitcher for 'team'."""
        func = cwlib.cw_box_get_starting_pitcher
        func.restype = POINTER(CWBoxPitcher)
        func.argtypes = (POINTER(CWBoxscore), c_int,)
        return func(box_ptr, team)

# END class MyCwlib
