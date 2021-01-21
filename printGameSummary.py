##############################################################################################################################
# coding=utf-8
#
# myChadwick.py -- Chadwick baseball tools coded in Python3
#
# Original C code Copyright (c) 2002-2020
# Dr T L Turocy, Chadwick Baseball Bureau (ted.turocy@gmail.com)
#
# Port to Python3 and modifications Copyright (c) 2019-2021 Mark Sattolo <epistemik@gmail.com>

__author__       = "Mark Sattolo"
__author_email__ = "epistemik@gmail.com"
__created__ = "2019-11-07"
__updated__ = "2021-01-19"

import csv
import sys
from argparse import ArgumentParser
from ctypes import c_void_p
from datetime import datetime as dt
from pychadwick.box import CWBoxPlayer, CWBoxPitcher
from pychadwick.chadwick import *
from pychadwick.roster import CWPlayer

chadwick = Chadwick()
cwlib = chadwick.libchadwick

POSITIONS = ["", "p", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf", "dh", "ph", "pr"]
MARKERS = ['*', '+', '#']

RETROSHEET_FOLDER = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/"
ROSTERS_FOLDER = RETROSHEET_FOLDER + "rosters/"
REGULAR_SEASON_FOLDER = RETROSHEET_FOLDER + "event/regular/"
POST_SEASON_FOLDER = RETROSHEET_FOLDER + "event/post/"


def c_char_p_to_str(lpcc:c_char_p, maxlen:int=20) -> str:
    """Convert a C-type char array to a python string:
       convert and concatenate the values until hit the null terminator or the char limit"""
    limit = 1 if maxlen <= 1 else min(maxlen, 256)
    bytez = lpcc[:limit]
    result = ""
    if len(bytez) == 0:
        return result
    if len(bytez) == 1:
        return chr(bytez[0])
    ct = 0
    for b in bytez:
        if b == 0:
            return result.strip()
        result += chr(b)
        ct += 1
        if ct == limit:
            return result.strip()


class MyCwlib:
    # char * cw_game_info_lookup(CWGame * game, char * label)
    @staticmethod
    def cwlib_game_info_lookup(game_ptr:POINTER(CWGame), label:bytes) -> str:
        logging.debug("\n cwlib_game_info_lookup():\n-------------------------")
        func = cwlib.cw_game_info_lookup
        func.restype = c_char_p
        func.argtypes = (POINTER(CWGame), c_char_p,)
        result = func(game_ptr, label)
        return result.decode(encoding='UTF-8')

    # void cw_game_write(CWGame *game, FILE *file)
    @staticmethod
    def cwlib_game_write(game_ptr:POINTER(CWGame), file_ptr:c_void_p):
        logging.debug("\n cwlib_game_write():\n-------------------------")
        func = cwlib.cw_game_write
        func.restype = None
        func.argtypes = (POINTER(CWGame), c_void_p,)
        return func(game_ptr, file_ptr)

    # CWGameIterator *cw_gameiter_create(CWGame *game)
    @staticmethod
    def cwlib_gameiter_create(game_ptr:POINTER(CWGame)) -> POINTER(CWGameIterator):
        logging.debug("\n cwlib_gameiter_create():\n-------------------------")
        func = cwlib.cw_gameiter_create
        func.restype = POINTER(CWGameIterator)
        func.argtypes = (POINTER(CWGame),)
        return func(game_ptr)

    # CWBoxscore *cw_box_create(CWGame *game)
    @staticmethod
    def cwlib_box_create(game_ptr:POINTER(CWGame)) -> POINTER(CWBoxscore):
        logging.debug("\n cwlib_box_create():\n-------------------------")
        func = cwlib.cw_box_create
        func.restype = POINTER(CWBoxscore)
        func.argtypes = (POINTER(CWGame),)
        return func(game_ptr)

    # CWRoster *cw_roster_create(char *team_id, int year, char *league, char *city, char *nickname)
    @staticmethod
    def cwlib_roster_create(team:str, year:int, league:str, city:str, nickname:str) -> POINTER(CWRoster):
        logging.debug("\n cwlib_roster_create():\n-------------------------")
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
    def cwlib_roster_read(roster_ptr:POINTER(CWRoster), file_handle:c_void_p) -> int:
        logging.debug("\n cwlib_roster_read():\n-------------------------")
        func = cwlib.cw_roster_read
        func.restype = c_int
        func.argtypes = (POINTER(CWRoster), c_void_p,)
        return func(roster_ptr, file_handle)

    # CWPlayer *cw_roster_player_find(CWRoster *roster, char *player_id)
    @staticmethod
    def cwlib_roster_player_find(roster_ptr:POINTER(CWRoster), player_id:bytes) -> POINTER(CWPlayer):
        logging.debug("\n cwlib_roster_player_find():\n-------------------------")
        func = cwlib.cw_roster_player_find
        func.restype = POINTER(CWPlayer)
        func.argtypes = (POINTER(CWRoster), c_char_p,)
        return func(roster_ptr, player_id)

    # CWBoxPlayer *cw_box_get_starter(CWBoxscore *boxscore, int team, int slot)
    @staticmethod
    def cwlib_box_get_starter(box_ptr:POINTER(CWBoxscore), team:int, slot:int) -> POINTER(CWBoxPlayer):
        logging.debug(" cwlib_box_get_starter():\n-------------------------")
        func = cwlib.cw_box_get_starter
        func.restype = POINTER(CWBoxPlayer)
        func.argtypes = (POINTER(CWBoxscore), c_int, c_int,)
        return func(box_ptr, team, slot)

    # CWBoxPitcher *cw_box_get_starting_pitcher(CWBoxscore *boxscore, int team)
    @staticmethod
    def cwlib_box_get_starting_pitcher(box_ptr:POINTER(CWBoxscore), team:int) -> POINTER(CWBoxPitcher):
        logging.debug("\n cwlib_box_get_starting_pitcher():\n-------------------------")
        func = cwlib.cw_box_get_starting_pitcher
        func.restype = POINTER(CWBoxPitcher)
        func.argtypes = (POINTER(CWBoxscore), c_int,)
        return func(box_ptr, team)
# END class MyCwlib


class MyChadwickTools:
    def __init__(self, logger:logging.Logger):
        self.lgr = logger
        self.lgr.warning(F" Start {self.__class__.__name__}")
        self.rosters = {}
        self.event_files = {}
        self.games = {}
        self.note_count = 0

    # void cwbox_print_timeofgame(CWGame * game)
    def print_time_of_game(self, p_game:pointer):
        self.lgr.info("print_time_of_game():\n----------------------------------")
        tog = int(MyCwlib.cwlib_game_info_lookup(p_game, b'timeofgame'))
        if tog and tog > 0:
            minutes = str(tog % 60)
            if len(minutes) == 1: minutes = "0" + minutes
            print(F"T -- {tog // 60}:{minutes}")

    # void cwbox_print_attendance(CWGame * game)
    def print_attendance(self, p_game:pointer):
        self.lgr.info("print_attendance():\n----------------------------------")
        print(F"A -- {MyCwlib.cwlib_game_info_lookup(p_game, b'attendance')}")

    # void cwbox_print_header(CWGame *game, CWRoster *visitors, CWRoster *home)
    def print_header( self, p_game:pointer, p_vis:pointer, p_home:pointer ):
        self.lgr.info("print_header():\n----------------------------------")

        dn_code = "?"
        day_night = MyCwlib.cwlib_game_info_lookup(p_game, b"daynight")
        if day_night:
            dn_code = "D" if day_night == "day" else "N" if day_night == "night" else day_night

        game_date = MyCwlib.cwlib_game_info_lookup(p_game, b"date")
        self.lgr.info(F"game date = {game_date}")
        year, month, day = game_date.split('/')
        game_number = MyCwlib.cwlib_game_info_lookup(p_game, b"number")
        self.lgr.info(F"game_number = {game_number}")
        game_number_str = "" if game_number == "0" else F", game #{game_number}"

        vis_city = p_vis.contents.city
        vis_city_text = c_char_p_to_str(vis_city)
        self.lgr.info(F"visitor = {vis_city_text}")

        home_city = p_home.contents.city
        home_city_text = c_char_p_to_str(home_city)
        self.lgr.info(F"home = {home_city_text}")

        print(F"\n\t\tGame of {month}/{day}/{year}{game_number_str} -- {vis_city_text} @ {home_city_text} ({dn_code})\n")

    # void cwbox_print_linescore(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_linescore( self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer ):
        self.lgr.info("print_linescore():\n----------------------------------")

        linescore = p_box.contents.linescore
        for t in range(0,2):
            runs = 0
            if t == 0:
                print(F"{c_char_p_to_str(p_vis.contents.city, 16):16}" if p_vis
                      else MyCwlib.cwlib_game_info_lookup(p_game, b"visteam"), end = '')
            else:
                print(F"{c_char_p_to_str(p_home.contents.city, 16):16}" if p_home
                      else MyCwlib.cwlib_game_info_lookup(p_game, b"hometeam"), end = '')

            for ix in range(1,32):
                if linescore[ix][t] >= 10:
                    print(F"({linescore[ix][t]})", end = '')
                    runs += linescore[ix][t]
                elif linescore[ix][t] >= 0:
                    print(F"{linescore[ix][t]}", end = '')
                    runs += linescore[ix][t]
                elif t == 0:
                    break
                elif linescore[ix][0] < 0:
                    break
                else:
                    print("x ", end = '')
                    break

                if ix % 3 == 0:
                    print(" ", end = '')

            print(F" -- {runs:2}")

        outs_at_end = p_box.contents.outs_at_end
        if outs_at_end != 3:
            if p_box.contents.walk_off:
                print(F"  {outs_at_end} out{'' if outs_at_end == 1 else 's'} when winning run scored.")
            else:
                print(F"  {outs_at_end} out{'' if outs_at_end == 1 else 's'} when game ended.")

    # void cwbox_print_text(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_text( self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer ):
        self.lgr.info("print_text():\n----------------------------------")

        self.note_count = 0
        slots = [1,1]
        players = list()
        ab = [0,0]
        r  = [0,0]
        h  = [0,0]
        bi = [0,0]
        pa = [0,0]
        bb = [0,0]
        so = [0,0]

        player0 = MyCwlib.cwlib_box_get_starter(p_box, 0, 1)
        self.lgr.debug(F"type(player0) = {type(player0)}")
        players.insert(0, player0)
        player1 = MyCwlib.cwlib_box_get_starter(p_box, 1, 1)
        self.lgr.debug(F"type(player1) = {type(player1)}")
        players.insert(1, player1)

        self.print_header(p_game, p_vis, p_home)

        vis_city = c_char_p_to_str(p_vis.contents.city) if p_vis else MyCwlib.cwlib_game_info_lookup(p_game, b"visteam")
        home_city = c_char_p_to_str(p_home.contents.city) if p_home else MyCwlib.cwlib_game_info_lookup(p_game, b"hometeam")

        print(F"  {vis_city:18} PA  AB   H  BB  SO  R RBI      {home_city:18} PA  AB   H  BB  SO  R RBI    ")

        while slots[0] <= 9 or slots[1] <= 9 :
            for t in range(0,2):
                if slots[t] <= 9:
                    self.print_player(players[t], p_vis if (t == 0) else p_home)
                    # NOTE: misspelling 'battiing' in the python wrapper file
                    batting = players[t].contents.battiing.contents
                    ab[t] += batting.ab
                    r[t]  += batting.r
                    h[t]  += batting.h
                    bb[t] += batting.bb
                    pa[t] += batting.pa
                    so[t] += batting.so
                    if batting.bi != -1:
                        bi[t] += batting.bi
                    else:
                        bi[t] = -1
                    players[t] = players[t].contents.next
                    if not players[t]:
                        # In some National Association games, teams played with 8 players.
                        # This generalization allows for printing boxscores when some batting slots are empty.
                        while slots[t] <= 9 and not players[t]:
                            slots[t] += 1
                            if slots[t] <= 9:
                                players[t] = cwlib.cw_box_get_starter(p_box, t, slots[t])
                else:
                    print(F"{''.ljust(45)}", end = '')
                print("     ", end = ''),
            print("")

        print(F"{''.ljust(20)} --  --  --  --  -- -- -- {''.ljust(24)} --  --  --  --  -- -- --")
        print(F"{''.ljust(20)}{pa[0]:3}{ab[0]:4}{h[0]:4}{bb[0]:4}{so[0]:4}{r[0]:3}", end = '')
        print(F"{bi[0]:3} " if bi[0] >= 0 else "    ", end = '')
        print(F"{''.ljust(24)}{pa[1]:3}{ab[1]:4}{h[1]:4}{bb[1]:4}{so[1]:4}{r[1]:3}", end = '')
        print(F"{bi[1]:3} " if bi[1] >= 0 else "    ")
        print("")

        self.print_linescore(p_game, p_box, p_vis, p_home)
        print("")

        for t in range(0, 2):
            pitcher = MyCwlib.cwlib_box_get_starting_pitcher(p_box, t)
            if t == 0:
                print(F"  {vis_city:18}   IP  H  R ER BB SO  TP TS GB FB")
            else:
                print(F"  {home_city:18}   IP  H  R ER BB SO  TP TS GB FB")
            while pitcher:
                self.print_pitcher( p_game, pitcher, (p_vis if (t == 0) else p_home) )
                pitcher = pitcher.contents.next
            if t == 0:
                print("")

        self.print_pitcher_apparatus(p_box)
        print("")

        self.print_apparatus(p_game, p_box, p_vis, p_home)
        print("")

    # void cwbox_print_player(CWBoxPlayer *player, CWRoster *roster)
    def print_player( self, p_player:POINTER(CWBoxPlayer), p_roster:POINTER(CWRoster) ):
        self.lgr.info("print_player():\n----------------------------------")

        bio = None
        posstr = ""

        player = p_player.contents
        if p_roster:
            bio = MyCwlib.cwlib_roster_player_find(p_roster, player.player_id)

        if bio:
            name = c_char_p_to_str(bio.contents.last_name) + " " + c_char_p_to_str(bio.contents.first_name, 1)
        else:
            name = player.name
        self.lgr.info(F"player name = {name}")

        if player.ph_inn > 0 and player.positions[0] != 11:
            posstr = "ph"
        elif player.pr_inn > 0 and player.positions[0] != 12:
            posstr = "pr"

        for pos in range(0, player.num_positions):
            if len(posstr) > 0:
                posstr += "-"
            posstr += POSITIONS[player.positions[pos]]

        if len(posstr) <= 10:
            if len(posstr) + len(name) > 18:
                outstr = F"{name[:(18 - len(posstr))]}, "
            else:
                outstr = F"{name}, "
            outstr += posstr
        else:
            # When there are a lot of positions, can't do much sensibly...
            outstr = F"{name}, {POSITIONS[player.positions[0]]}..."

        self.lgr.info(F"outstr = {outstr}")

        # NOTE: misspelling 'battiing' in the python wrapper file
        batting = player.battiing.contents

        print(F"{outstr:20}{batting.pa:3}{batting.ab:4}{batting.h:4}{batting.bb:4}{batting.so:4}{batting.r:3}", end = '')
        print(F"{batting.bi:3}" if batting.bi >= 0 else "", end = '')

    # void
    # cwbox_print_player_apparatus(CWGame *game, CWBoxEvent *list, int index, char *label, CWRoster *visitors, CWRoster *home)
    def print_player_apparatus(self, p_events:pointer, index:int, label:str, p_vis:pointer, p_home:pointer):
        # Generic output for list of events (2B, 3B, WP, etc)
        self.lgr.info("print_player_apparatus():\n----------------------------------")
        if not p_events:
            return
        event = p_events.contents
        comma = 0
        print(F"{label} -- ", end = '')
        while event:
            search_event = event
            bio = None
            name = ""
            count = 0
            if event.mark > 0:
                event = event.next.contents if event.next else None
                continue
            while search_event:
                if event.players[index] == search_event.players[index]:
                    count += 1
                    search_event.mark = 1
                search_event = search_event.next.contents if search_event.next else None

            if p_vis:
                bio = MyCwlib.cwlib_roster_player_find(p_vis, event.players[index])
            if not bio and p_home:
                bio = MyCwlib.cwlib_roster_player_find(p_home, event.players[index])
            if not bio:
                name = event.players[index].decode('UTF8')
                self.lgr.warning("bio NOT available!")
            if comma:
                print(", ", end = '')
            if count == 1:
                if bio:
                    print(F"{c_char_p_to_str(bio.contents.last_name)} "
                          F"{c_char_p_to_str(bio.contents.first_name[0],1)}", end = '')
                elif name:
                    print(F"{name}", end = '')
                else:
                    print(F"{event.players[index].decode('UTF8')}", end = '')
            else:
                if bio:
                    print(F"{c_char_p_to_str(bio.contents.last_name)} "
                          F"{c_char_p_to_str(bio.contents.first_name[0],1)} {count}", end = '')
                elif name:
                    print(F"{name} {count}", end = '')
                else:
                    print(F"{event.players[index].decode('UTF8')} {count}", end = '')
            comma = 1
        print("")
        # NOTE: reset events.mark >> NEEDED in Python?
        event = p_events.contents
        while event:
            event.mark = 0
            event = event.next.contents if event.next else None

    # void cwbox_print_apparatus(CWGame * game, CWBoxscore * boxscore, CWRoster * visitors, CWRoster * home)
    def print_apparatus( self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer ):
        # Output the apparatus (list of events and other miscellaneous game information)
        self.lgr.info("print_apparatus():\n----------------------------------")

        boxscore = p_box.contents
        self.print_player_apparatus(boxscore.err_list, 0, "E", p_vis, p_home)
        self.print_double_plays(p_game, p_box, p_vis, p_home)
        self.print_triple_plays(p_game, p_box, p_vis, p_home)
        self.print_lob(p_game, p_box, p_vis, p_home)
        self.print_player_apparatus(boxscore.b2_list, 0, "2B", p_vis, p_home)
        self.print_player_apparatus(boxscore.b3_list, 0, "3B", p_vis, p_home)
        self.print_player_apparatus(boxscore.hr_list, 0, "HR", p_vis, p_home)
        self.print_player_apparatus(boxscore.sb_list, 0, "SB", p_vis, p_home)
        self.print_player_apparatus(boxscore.cs_list, 0, "CS", p_vis, p_home)
        self.print_player_apparatus(boxscore.sh_list, 0, "SH", p_vis, p_home)
        self.print_player_apparatus(boxscore.sf_list, 0, "SF", p_vis, p_home)
        self.print_hbp(boxscore.hp_list, p_vis, p_home)
        self.print_player_apparatus(boxscore.wp_list, 0, "WP", p_vis, p_home)
        self.print_player_apparatus(boxscore.bk_list, 0, "Balk", p_vis, p_home)
        self.print_player_apparatus(boxscore.pb_list, 1, "PB", p_vis, p_home)
        self.print_time_of_game(p_game)
        self.print_attendance(p_game)

    # void cwbox_print_pitcher(CWGame * game, CWBoxPitcher * pitcher, CWRoster * roster, int * note_count)
    def print_pitcher( self, p_game:pointer, p_pitcher:pointer, p_roster:pointer ):
        self.lgr.info("print_pitcher():\n----------------------------------")
        # Output one pitcher's pitching line. The parameter 'note_count' keeps track of how many apparatus notes
        # have been emitted (for pitchers who do not record an out in an inning)
        bio = None
        roster = p_roster.contents
        pitcher = p_pitcher.contents
        player_id = pitcher.player_id.decode("UTF8")
        self.lgr.info(F"player id = {player_id}")
        self.lgr.debug(F"type(player id) = {type(player_id)}")
        if roster:
            bio = MyCwlib.cwlib_roster_player_find(p_roster, bytes(pitcher.player_id))
        if bio:
            name = c_char_p_to_str(bio.contents.last_name) + " " + c_char_p_to_str(bio.contents.first_name, 1)
        else:
            name = pitcher.name
        self.lgr.info(F"pitcher name = {name}")

        game = p_game.contents
        wp = MyCwlib.cwlib_game_info_lookup(game, b"wp")
        self.lgr.info(F"winning pitcher id = {wp}")
        self.lgr.debug(F"type(wp) = {type(wp)}")
        lp = MyCwlib.cwlib_game_info_lookup(game, b"lp")
        self.lgr.info(F"losing pitcher id = {lp}")
        save = MyCwlib.cwlib_game_info_lookup(game, b"save")
        self.lgr.info(F"save pitcher id = {save}")
        if wp and wp == player_id:
            name += " (W)"
        elif lp and lp == player_id:
            name += " (L)"
        elif save and save == player_id:
            name += " (S)"

        pitching = pitcher.pitching.contents
        if pitching.xbinn > 0 and pitching.xb > 0:
            for i in range(0, (self.note_count // 3)+1):
                name += MARKERS[self.note_count % 3]
            self.note_count += 1

        print(F"{name:20} {pitching.outs // 3:2}.{pitching.outs % 3} {pitching.h:2} {pitching.r:2}", end = '')
        print(F"{pitching.er:3}" if pitching.er >= 0 else "   ", end = '')
        print(F"{pitching.bb:3}" if pitching.bb >= 0 else "   ", end = '')
        print(F"{pitching.so:3}" if pitching.so >= 0 else "   ", end = '')
        print(F"{pitching.pitches:4}" if pitching.pitches >= 0 else "    ", end = '')
        print(F"{pitching.strikes:3}" if pitching.strikes >= 0 else "   ", end = '')
        print(F"{pitching.gb:3}" if pitching.gb >= 0 else "   ", end = '')
        print(F"{pitching.fb:3}" if pitching.fb >= 0 else "   ")

    # void cwbox_print_double_play(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_double_plays(self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer):
        self.lgr.info("print_double_plays():\n----------------------------------")
        dp = p_box.contents.dp
        if dp[0] == 0 and dp[1] == 0:
            return
        print("DP -- ", end = '')
        vis_city = c_char_p_to_str(p_vis.contents.city) if p_vis else MyCwlib.cwlib_game_info_lookup(p_game, b"visteam")
        home_city = c_char_p_to_str(p_home.contents.city) if p_home else MyCwlib.cwlib_game_info_lookup(p_game, b"hometeam")

        if dp[0] > 0 and dp[1] == 0:
            print(F"{vis_city} {dp[0]}")
        elif dp[0] == 0 and dp[1] > 0:
            print(F"{home_city} {dp[1]}")
        else:
            print(F"{vis_city} {dp[0]}, {home_city} {dp[1]}")

    # void cwbox_print_triple_play(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_triple_plays(self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer):
        self.lgr.info("print_triple_plays():\n----------------------------------")
        tp = p_box.contents.tp
        if tp[0] == 0 and tp[1] == 0:
            return
        print("TP -- ", end = '')
        vis_city = c_char_p_to_str(p_vis.contents.city) if p_vis else MyCwlib.cwlib_game_info_lookup(p_game, b"visteam")
        home_city = c_char_p_to_str(p_home.contents.city) if p_home else MyCwlib.cwlib_game_info_lookup(p_game, b"hometeam")
        if tp[0] > 0 and tp[1] == 0:
            print(F"{vis_city} {tp[0]}")
        elif tp[0] == 0 and tp[1] > 0:
            print(F"{home_city} {tp[1]}")
        else:
            print(F"{vis_city} {tp[0]}, {home_city} {tp[1]}")

    # void cwbox_print_hbp_apparatus(CWGame *game, CWBoxEvent *list,  CWRoster *visitors, CWRoster *home)
    def print_hbp(self, p_event:pointer, p_vis:pointer, p_home:pointer):
        self.lgr.info("print_hbp():\n----------------------------------")
        if not p_event:
            return
        event = p_event
        comma = 0
        print("HBP -- ", end = '')
        while event:
            search_event = event
            batter = pitcher = None
            batter_name = pitcher_name = ""
            count = 0
            if event.contents.mark > 0:
                event = event.contents.next
                continue

            while search_event:
                if event.contents.players[0] == search_event.contents.players[0] \
                        and event.contents.players[1] == search_event.contents.players[1]:
                    count += 1
                    search_event.contents.mark = 1
                search_event = search_event.contents.next

            if p_vis:
                batter = MyCwlib.cwlib_roster_player_find(p_vis, event.contents.players[0])
            if not batter and p_home:
                batter = MyCwlib.cwlib_roster_player_find(p_home, event.contents.players[0])
            if not batter:
                batter_name = event.contents.players[0].decode('UTF8')
                self.lgr.warning("roster NOT available for batter!")
            if p_vis:
                pitcher = MyCwlib.cwlib_roster_player_find(p_vis, event.contents.players[1])
            if not pitcher and p_home:
                pitcher = MyCwlib.cwlib_roster_player_find(p_home, event.contents.players[1])
            if not pitcher:
                self.lgr.warning("roster NOT available for pitcher!")
                pitcher_name = event.contents.players[1].decode('UTF8')
            if comma: print(", ", end = '')

            if pitcher:
                print(F"by {c_char_p_to_str(pitcher.contents.last_name)} "
                      F"{pitcher.contents.first_name[0].decode('UTF8')} ", end = '')
            else:
                print(F"by {pitcher_name if pitcher_name else c_char_p_to_str(event.contents.players[1])} ", end = '')
            if batter:
                print(F"({c_char_p_to_str(batter.contents.last_name)} "
                      F"{batter.contents.first_name[0].decode('UTF8')})", end = '')
            else:
                print(F"({batter_name if batter_name else c_char_p_to_str(event.contents.players[0])})", end = '')
            if count != 1:
                print(" %d", count)
            comma = 1
        print("")
        # NOTE: reset events.mark >> NEEDED in Python?
        event = p_event
        while event:
            event.contents.mark = 0
            event = event.contents.next

    # void cwbox_print_lob(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_lob(self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer):
        self.lgr.info("print_lob():\n----------------------------------")
        lob = p_box.contents.lob
        if lob[0] == 0 and lob[1] == 0:
            return
        vis_city = c_char_p_to_str(p_vis.contents.city) if p_vis else MyCwlib.cwlib_game_info_lookup(p_game, b"visteam")
        home_city = c_char_p_to_str(p_home.contents.city) if p_home else MyCwlib.cwlib_game_info_lookup(p_game, b"hometeam")
        print(F"LOB -- {vis_city} {lob[0]}, {home_city} {lob[1]}")

    # void cwbox_print_pitcher_apparatus(CWBoxscore * boxscore)
    def print_pitcher_apparatus(self, p_box:pointer):
        # Output the pitching apparatus (list of pitchers who did not record an out in an inning)
        self.lgr.info("print_pitcher_apparatus():\n----------------------------------")

        count = 0
        for t in range(0, 2):
            pitcher = MyCwlib.cwlib_box_get_starting_pitcher(p_box, t)
            while pitcher:
                pitching = pitcher.contents.pitching.contents
                if pitching.xbinn > 0 and pitching.xb > 0:
                    print("  ", end = '')
                    for i in range(0, (count // 3)+1):
                        print(F"{MARKERS[count % 3]}", end = '')
                    print(F" Pitched to {pitching.xb} batter{'' if pitching.xb == 1 else 's'} in {pitching.xbinn}", end = '')
                    if pitching.xbinn % 10 == 1 and pitching.xbinn != 11:
                        print("st")
                    elif pitching.xbinn % 10 == 2 and pitching.xbinn != 12:
                        print("nd")
                    elif pitching.xbinn % 10 == 3 and pitching.xbinn != 13:
                        print("rd")
                    else:
                        print("th")
                    count += 1
                pitcher = pitcher.contents.next

# END class MyChadwickTools


def process_args():
    arg_parser = ArgumentParser(description="Print boxscore(s) from retrosheet data for the specified team and date range",
                                prog='main_chadwick_py3.py')
    # required arguments
    required = arg_parser.add_argument_group('REQUIRED')
    required.add_argument('-t', '--team', required=True, help="Retrosheet 3-character id for a team, e.g. TOR, LAN")
    required.add_argument('-y', '--year', type=int, required=True, help="year to find games to print out (yyyy)")
    # optional arguments
    arg_parser.add_argument('-s', '--start', help="start date to print out games (mmdd)")
    arg_parser.add_argument('-e', '--end', help="end date to print out games (mmdd)")
    arg_parser.add_argument('-p', '--post', action="store_true", help="find postseason games instead of regular season")
    arg_parser.add_argument('-q', '--quiet', action="store_true", help="NO logging")
    arg_parser.add_argument('-l', '--level', default="INFO", help="set LEVEL of logging output")

    return arg_parser


def process_input_parameters(argx:list):
    args = process_args().parse_args(argx)
    loglevel = "CRITICAL" if args.quiet else args.level
    try:
        getattr( logging, loglevel.strip().upper() )
    except AttributeError as ae:
        print(F"Problem with log level: {repr(ae)}")
        loglevel = "INFO"

    logging.basicConfig(level = loglevel)
    logging.warning(F"process_input_parameters(): Level = {loglevel}\n--------------------------------------")
    logging.info(F"args = \n{args}")

    # TODO: process 'postseason' flag

    team = args.team.strip().upper() if args.team.isalpha() and len(args.team.strip()) >= 3 else "TOR"
    if len(team) > 3:
        team = team[:3]
    logging.warning(F"team = {team}")

    year = str(args.year) if 1871 <= args.year <= 2020 else "1993"
    logging.warning(F"year = {year}")

    if args.start:
        start = args.start.strip()
        if not start.isdecimal() or not len(start) == 4:
            start = "9999"
    else:
        start = "0301"
    logging.warning(F"start = {start}")

    if args.end:
        end = args.end.strip()
        if not end.isdecimal() or not len(end) == 4:
            end = "0000"
    else:
        end = "1031"
    logging.warning(F"end = {end}")

    return team, year, start, end, loglevel


def main_chadwick_py3(args:list):
    lgr = logging.getLogger("MyChadwick")

    team, year, start, end, loglevel = process_input_parameters(args)

    lgr.setLevel(loglevel)
    lgr.debug( str(lgr.handlers) )
    lgr.warning(F" team = {team}; year = {year}")

    cwtools = MyChadwickTools(lgr)
    try:
        # get the team files
        team_file_name = REGULAR_SEASON_FOLDER + "TEAM" + year
        lgr.info(F"team file name = {team_file_name}")
        with open(team_file_name, newline = '') as csvfile:
            teamreader = csv.reader(csvfile)
            for row in teamreader:
                rteam = row[0]
                lgr.info(F"Found team {rteam}")
                if rteam == team:
                    lgr.info(F"\t-- league is {row[1]}L; city is {row[2]}; nickname is {row[3]}")
                # create the rosters
                cwtools.rosters[rteam] = MyCwlib.cwlib_roster_create(rteam, int(year), row[1]+"L", row[2], row[3])
                roster_file = ROSTERS_FOLDER + rteam + year + ".ROS"
                lgr.debug(F"roster file name = {roster_file}")
                if not os.path.exists(roster_file):
                    raise FileNotFoundError(F"CANNOT find roster file {roster_file}!")
                roster_fptr = chadwick.fopen( bytes(roster_file, "utf8") )
                # fill the rosters
                roster_read_result = MyCwlib.cwlib_roster_read(cwtools.rosters[rteam], roster_fptr)
                lgr.info("roster read result = " + ("Success." if roster_read_result > 0 else "Failure!"))
                chadwick.fclose(roster_fptr)
                # find and store the event file paths
                event_file = REGULAR_SEASON_FOLDER + year + rteam + ".EV" + row[1]
                if not os.path.exists(event_file):
                    raise FileNotFoundError(F"CANNOT find event file {event_file}!")
                cwtools.event_files[rteam] = event_file

        for item in cwtools.rosters.values():
            lgr.debug(item)
        for item in cwtools.event_files.values():
            lgr.debug(item)

        start_id = year + start
        lgr.info(F"start id = {start_id}")
        end_id = year + end
        lgr.info(F"end id = {end_id}")

        # get all the games for the requested team in the supplied date range
        for evteam in cwtools.event_files:
            lgr.info(F"found events for team = {evteam}")
            cwgames = chadwick.games( cwtools.event_files[evteam] )
            for game in cwgames:
                game_id = game.contents.game_id.decode(encoding='UTF-8')
                game_date = game_id[3:11]
                lgr.debug(F" Found game id = {game_id}; date = {game_date}")

                if end_id >= game_date >= start_id:
                    results = tuple( chadwick.process_game(game) )
                    home_team = results[0]['HOME_TEAM_ID']
                    away_team = results[0]['AWAY_TEAM_ID']
                    if home_team == team or away_team == team:
                        lgr.warning(F" Found game id = {game_id}")
                        cwtools.games[game_id[3:]] = game

        # sort the games and print out the information
        for key in sorted( cwtools.games.keys() ):
            game = cwtools.games[key]
            box = MyCwlib.cwlib_box_create(game)
            events = chadwick.process_game(game)
            results = tuple(events)

            away_team = results[0]['AWAY_TEAM_ID']
            visitor = cwtools.rosters[away_team]
            home_team = results[0]['HOME_TEAM_ID']
            home = cwtools.rosters[home_team]

            cwtools.print_text(game, box, visitor, home)

    except Exception as ex:
        lgr.exception(F"Exception: {repr(ex)}")


if __name__ == "__main__":
    run_start_time = dt.now()
    if '-q' not in sys.argv:
        logging.critical(F"Run Start time = {run_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    main_chadwick_py3(sys.argv[1:])
    if '-q' not in sys.argv:
        run_time = (dt.now() - run_start_time).total_seconds()
        logging.critical(F" Running time = {(run_time // 60)} minutes, {(run_time % 60):2.3} seconds")
    exit()
