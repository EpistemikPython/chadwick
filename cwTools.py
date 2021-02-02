##############################################################################################################################
# coding=utf-8
#
# cwTools.py -- Chadwick baseball tools coded in Python3
#
# Original C code Copyright (c) 2002-2021
# Dr T L Turocy, Chadwick Baseball Bureau (ted.turocy@gmail.com)
#
# Port to Python3, additions & modifications Copyright (c) 2019-2021 Mark Sattolo <epistemik@gmail.com>

__author__       = "Mark Sattolo"
__author_email__ = "epistemik@gmail.com"
__created__ = "2019-11-07"
__updated__ = "2021-02-02"

import logging
import os
from datetime import datetime as dt
from ctypes import c_char_p, pointer
from cwLibWrappers import MyCwlib

FXN_DATE_STR:str  = "%Y-%m-%d"
FXN_TIME_STR:str  = "%H:%M:%S:%f"
FILE_DATE_STR:str = "D%Y-%m-%d"
FILE_TIME_STR:str = "T%Hh%M"
FILE_DATETIME_FORMAT = FILE_DATE_STR + FILE_TIME_STR
RUN_DATETIME_FORMAT  = FXN_DATE_STR + '_' + FXN_TIME_STR

start_dt:dt = dt.now()
run_ts:str  = start_dt.strftime(RUN_DATETIME_FORMAT)
file_ts:str = start_dt.strftime(FILE_DATETIME_FORMAT)

POSITIONS = ["", "p", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf", "dh", "ph", "pr"]
MARKERS = ['*', '+', '#']

RETROSHEET_FOLDER = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/"
ROSTERS_FOLDER = RETROSHEET_FOLDER + "rosters/"
REGULAR_SEASON_FOLDER = RETROSHEET_FOLDER + "event/regular/"
POST_SEASON_FOLDER = RETROSHEET_FOLDER + "event/post/"


def get_basename(filename:str) ->str:
    _, fname = os.path.split(filename)
    basename, _ = os.path.splitext(fname)
    return basename


def get_logger(name:str, file_time:str, level:str) -> logging.Logger:
    _, fname = os.path.split(name)
    basename, _ = os.path.splitext(fname)

    lgr = logging.getLogger(basename)
    # default for logger: all messages DEBUG or higher
    lgr.setLevel(logging.DEBUG)

    fh = logging.FileHandler("logs/" + basename + '_' + file_time + ".log")
    # default for filehandler: all messages DEBUG or higher
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler() # console handler
    # only log in console to the level requested on the command line
    ch.setLevel(level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter("%(levelname)s - %(asctime)s | %(funcName)s > %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add handlers to the logger
    lgr.addHandler(ch)
    lgr.addHandler(fh)
    return lgr


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


class MyChadwickTools:
    def __init__(self, logger):
        self.lgr = logger
        self.lgr.warning(F" Start {self.__class__.__name__}")
        self.note_count = 0

    # void cwbox_print_timeofgame(CWGame * game)
    def print_time_of_game(self, p_game:pointer):
        self.lgr.info("\n----------------------------------")
        tog = int(MyCwlib.game_info_lookup(p_game, b'timeofgame'))
        if tog and tog > 0:
            minutes = str(tog % 60)
            if len(minutes) == 1: minutes = "0" + minutes
            print(F"T -- {tog // 60}:{minutes}")

    # void cwbox_print_attendance(CWGame * game)
    def print_attendance(self, p_game:pointer):
        self.lgr.info("\n----------------------------------")
        print(F"A -- {MyCwlib.game_info_lookup(p_game, b'attendance')}")

    # void cwbox_print_player(CWBoxPlayer *player, CWRoster *roster)
    def print_player( self, p_player:pointer, p_roster:pointer ):
        self.lgr.info("\n----------------------------------")

        bio = None
        posstr = ""

        player = p_player.contents
        if p_roster:
            bio = MyCwlib.roster_player_find(p_roster, player.player_id)

        if bio:
            name = c_char_p_to_str(bio.contents.last_name) + " " + c_char_p_to_str(bio.contents.first_name, 1)
        else:
            name = player.name
        self.lgr.info(F"player name = {name}")

        if player.ph_inn > 0 and player.positions[0] != 11:
            posstr = "ph"
        elif player.pr_inn > 0 and player.positions[0] != 12:
            posstr = "pr"

        for pos in range( player.num_positions ):
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

        batting = player.batting.contents
        print(F"{outstr:20}{batting.pa:3}{batting.ab:4}{batting.h:4}{batting.bb:4}{batting.so:4}{batting.r:3}", end = '')
        print(F"{batting.bi:3}" if batting.bi >= 0 else "", end = '')

    # void
    # cwbox_print_player_apparatus(CWGame *game, CWBoxEvent *list, int index, char *label, CWRoster *visitors, CWRoster *home)
    def print_player_apparatus(self, p_events:pointer, index:int, label:str, p_vis:pointer, p_home:pointer):
        # Generic output for list of events (2B, 3B, WP, etc)
        self.lgr.info("\n----------------------------------")
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
                bio = MyCwlib.roster_player_find(p_vis, event.players[index])
            if not bio and p_home:
                bio = MyCwlib.roster_player_find(p_home, event.players[index])
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
        self.lgr.info("\n----------------------------------")

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
        self.lgr.info("\n----------------------------------")
        # Output one pitcher's pitching line. The parameter 'note_count' keeps track of how many apparatus notes
        # have been emitted (for pitchers who do not record an out in an inning)
        bio = None
        roster = p_roster.contents
        pitcher = p_pitcher.contents
        player_id = pitcher.player_id.decode("UTF8")
        self.lgr.info(F"player id = {player_id}")
        self.lgr.debug(F"type(player id) = {type(player_id)}")
        if roster:
            bio = MyCwlib.roster_player_find(p_roster, bytes(pitcher.player_id))
        if bio:
            name = c_char_p_to_str(bio.contents.last_name) + " " + c_char_p_to_str(bio.contents.first_name, 1)
        else:
            name = pitcher.name
        self.lgr.info(F"pitcher name = {name}")

        game = p_game.contents
        wp = MyCwlib.game_info_lookup(game, b"wp")
        self.lgr.info(F"winning pitcher id = {wp}")
        self.lgr.debug(F"type(wp) = {type(wp)}")
        lp = MyCwlib.game_info_lookup(game, b"lp")
        self.lgr.info(F"losing pitcher id = {lp}")
        save = MyCwlib.game_info_lookup(game, b"save")
        self.lgr.info(F"save pitcher id = {save}")
        if wp and wp == player_id:
            name += " (W)"
        elif lp and lp == player_id:
            name += " (L)"
        elif save and save == player_id:
            name += " (S)"

        pitching = pitcher.pitching.contents
        if pitching.xbinn > 0 and pitching.xb > 0:
            for i in range( (self.note_count // 3)+1 ):
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
        self.lgr.info("\n----------------------------------")
        dp = p_box.contents.dp
        if dp[0] == 0 and dp[1] == 0:
            return
        print("DP -- ", end = '')

        vis_city = c_char_p_to_str(p_vis.contents.city) if p_vis else MyCwlib.game_info_lookup(p_game, b"visteam")
        home_city = c_char_p_to_str(p_home.contents.city) if p_home else MyCwlib.game_info_lookup(p_game, b"hometeam")

        if dp[0] > 0 and dp[1] == 0:
            print(F"{vis_city} {dp[0]}")
        elif dp[0] == 0 and dp[1] > 0:
            print(F"{home_city} {dp[1]}")
        else:
            print(F"{vis_city} {dp[0]}, {home_city} {dp[1]}")

    # void cwbox_print_triple_play(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_triple_plays(self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer):
        self.lgr.info("\n----------------------------------")
        tp = p_box.contents.tp
        if tp[0] == 0 and tp[1] == 0:
            return
        print("TP -- ", end = '')

        vis_city = c_char_p_to_str(p_vis.contents.city) if p_vis else MyCwlib.game_info_lookup(p_game, b"visteam")
        home_city = c_char_p_to_str(p_home.contents.city) if p_home else MyCwlib.game_info_lookup(p_game, b"hometeam")

        if tp[0] > 0 and tp[1] == 0:
            print(F"{vis_city} {tp[0]}")
        elif tp[0] == 0 and tp[1] > 0:
            print(F"{home_city} {tp[1]}")
        else:
            print(F"{vis_city} {tp[0]}, {home_city} {tp[1]}")

    # void cwbox_print_hbp_apparatus(CWGame *game, CWBoxEvent *list,  CWRoster *visitors, CWRoster *home)
    def print_hbp(self, p_event:pointer, p_vis:pointer, p_home:pointer):
        self.lgr.info("\n----------------------------------")
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
                batter = MyCwlib.roster_player_find(p_vis, event.contents.players[0])
                pitcher = MyCwlib.roster_player_find(p_vis, event.contents.players[1])
            if p_home:
                if not batter: batter = MyCwlib.roster_player_find(p_home, event.contents.players[0])
                if not pitcher: pitcher = MyCwlib.roster_player_find(p_home, event.contents.players[1])
            if not batter:
                batter_name = event.contents.players[0].decode('UTF8')
                self.lgr.warning("roster NOT available for batter!")
            if not pitcher:
                pitcher_name = event.contents.players[1].decode('UTF8')
                self.lgr.warning("roster NOT available for pitcher!")
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
        self.lgr.info("\n----------------------------------")
        lob = p_box.contents.lob
        if lob[0] == 0 and lob[1] == 0:
            return
        vis_city = c_char_p_to_str(p_vis.contents.city) if p_vis else MyCwlib.game_info_lookup(p_game, b"visteam")
        home_city = c_char_p_to_str(p_home.contents.city) if p_home else MyCwlib.game_info_lookup(p_game, b"hometeam")
        print(F"LOB -- {vis_city} {lob[0]}, {home_city} {lob[1]}")

    # void cwbox_print_pitcher_apparatus(CWBoxscore * boxscore)
    def print_pitcher_apparatus(self, p_box:pointer):
        # Output the pitching apparatus (list of pitchers who did not record an out in an inning)
        self.lgr.info("\n----------------------------------")

        count = 0
        for t in range(2):
            pitcher = MyCwlib.box_get_starting_pitcher(p_box, t)
            while pitcher:
                pitching = pitcher.contents.pitching.contents
                if pitching.xbinn > 0 and pitching.xb > 0:
                    print("  ", end = '')
                    for i in range( (count // 3)+1 ):
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
