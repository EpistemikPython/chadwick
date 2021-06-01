##############################################################################################################################
# coding=utf-8
#
# cwTools.py -- my Chadwick baseball tools coded in Python3
#
# The data processed by this software was obtained free of charge from and is copyrighted by Retrosheet.
# Interested parties may contact Retrosheet at 20 Sunset Rd., Newark, DE 19711.
#
# Original C code Copyright (c) 2002-2021
# Dr T L Turocy, Chadwick Baseball Bureau (ted.turocy@gmail.com)
#
# Port to Python3, additions & modifications Copyright (c) 2019-2021 Mark Sattolo <epistemik@gmail.com>

__author__       = "Mark Sattolo"
__author_email__ = "epistemik@gmail.com"
__created__ = "2019-11-07"
__updated__ = "2021-06-01"

import csv
import glob
import sys
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from ctypes import c_char_p, pointer
from cwLibWrappers import MyCwlib, chadwick
sys.path.append("/newdata/dev/git/Python/utils")
from mhsUtils import lg, get_base_filename, osp
from mhsLogging import DEFAULT_CONSOLE_LEVEL, QUIET_LOG_LEVEL

POSITIONS = ["", "p", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf", "dh", "ph", "pr"]
MARKERS = ['*', '+', '#']
LABEL_TOTAL  = "Total"
STD_HDR_SIZE = 4

RETROSHEET_FOLDER     = "/newdata/dev/git/fork/ChadwickBureau/retrosheet/"
ROSTERS_FOLDER        = RETROSHEET_FOLDER + "rosters/"
REGULAR_SEASON_FOLDER = RETROSHEET_FOLDER + "event/regular/"
POST_SEASON_FOLDER    = RETROSHEET_FOLDER + "event/post/"
BOXSCORE_FOLDER       = "/newdata/dev/Retrosheet/data/boxscores/"

def c_char_p_to_str(lpcc:c_char_p, maxlen:int = 32) -> str:
    """Convert a C-type char array to a python string:
       convert and concatenate the values until hit the null terminator or the char limit"""
    limit = 1 if maxlen <= 1 else min(maxlen, 256)
    bytez = lpcc[:limit]
    result = ''
    if len(bytez) == 0:
        return result
    if len(bytez) == 1:
        return chr(bytez[0])
    ct = 0
    for b in bytez:
        if b == 0 or ct == limit:
            return result.strip()
        result += chr(b)
        ct += 1

def get_print_str(num:float, games:int, prec:int, lim:int = STD_HDR_SIZE) -> str:
    if games == 0: return 'x'
    if num == 0.0: return ".000"
    rnum = round(num, prec)
    if rnum <= 0.0: return ".000"
    high = prec + 2
    low = high - lim
    if low < 0: low = 0
    if rnum >= 10.0: high += 1
    return float_to_sized_str(rnum, low, high, lim)

def float_to_sized_str(num:float, low:int, high:int, lim:int) -> str:
    snum = str(num)[low:high]
    len_str = len(snum)
    if len_str < lim:
        for r in range(lim - len_str):
            snum += '0'
    return snum


class PrintStats(ABC):
    """print batting or pitching stats for a specified player using Retrosheet data"""
    def __init__(self, logger:lg.Logger):
        self.lgr = logger
        self.lgr.warning(F"Start {self.__class__.__name__}")
        self.event_files = dict()
        self.game_ids = list()
        self.num_years = 0
        self.stats = None
        self.totals = None
        self.std_space = 0
        self.hdrs = None
        self.num_files = 0
        self.fam_name = self.giv_name = ""

    def get_num_files(self):
        return self.num_files

    def get_giv_name(self):
        return self.giv_name

    def get_fam_name(self):
        return self.fam_name

    def sum_and_clear(self):
        for item in self.stats.keys():
            self.totals[item] += self.stats[item]
            self.stats[item] = 0

    def print_hdr_uls(self):
        print(''.rjust(self.std_space), end = '')
        for spx in range(len(self.hdrs)):
            print("---".rjust(self.std_space), end = '')
        print(" ")

    def print_header(self):
        print(''.rjust(self.std_space), end = '')
        for item in self.hdrs:
            print(item.rjust(self.std_space), end = '')
        print(" ")
        self.print_hdr_uls()

    def print_stats(self, player_id:str, name:str, season:str, yrstart:int, yrend:int):
        """print regular or post-season stats for player {player_id} in years {yrstart} to {yrend}"""
        self.lgr.debug(F"print {season} stats for years {yrstart} to {yrend}")
        print(F"\n\t{name} {season} Stats:")
        self.print_header()

        # get all the games in the supplied date range
        for year in range(yrstart, yrend + 1):
            self.lgr.info(F"collect stats for year: {year}")
            self.game_ids.clear()
            str_year = str(year)
            if str_year not in self.event_files.keys():
                continue
            for efile in self.event_files[str_year]:
                self.lgr.debug(F"found events for year/team = {get_base_filename(efile)}")
                cwgames = chadwick.games(efile)
                for game in cwgames:
                    game_id = game.contents.game_id.decode(encoding = 'UTF-8')
                    game_date = game_id[3:11]
                    self.lgr.debug(F" Found game id = {game_id}; date = {game_date}")

                    box = MyCwlib.box_create(game)
                    self.collect_stats(box, player_id, str_year, game_id)

            self.lgr.info(F"found {len(self.game_ids)} games with {player_id} stats.")

            if year < 1974 and "regular" in season:
                self.check_boxscores(player_id, str_year)

            self.print_stat_line(str_year)
            self.sum_and_clear()

        if self.num_years > 1:
            self.print_hdr_uls()
            self.print_header()
            self.print_stat_line(LABEL_TOTAL)
            self.print_ave_line()
        print('')

    def get_events(self, post:bool, pers_id:str, start:int, end:int):
        """get the required event files for batching and pitching stats"""
        season = "post-season" if post else "regular season"
        self.lgr.info(F"get the {season} events for player {pers_id} in years {start}->{end}")
        need_name = True
        self.fam_name = pers_id
        try:
            for year in range(start, end+1):
                year_events = list()
                # get the team files
                team_file_name = REGULAR_SEASON_FOLDER + "TEAM" + str(year)
                self.lgr.debug(F"team file name = {team_file_name}")
                if not osp.exists(team_file_name):
                    self.lgr.exception(F"CANNOT find team file {team_file_name}!")
                    continue
                with open(team_file_name, newline = '') as team_csvfile:
                    team_reader = csv.reader(team_csvfile)
                    for trow in team_reader:
                        rteam = trow[0]
                        self.lgr.debug(F"Found team {rteam}")
                        # search rosters for the player's full name
                        if need_name:
                            roster_file = ROSTERS_FOLDER + rteam + str(year) + ".ROS"
                            self.lgr.debug(F"roster file name = {roster_file}")
                            if not osp.exists(roster_file):
                                raise FileNotFoundError(F"CANNOT find roster file {roster_file}!")
                            with open(roster_file, newline = '') as roster_csvfile:
                                ros_reader = csv.reader(roster_csvfile)
                                for rrow in ros_reader:
                                    if pers_id == rrow[0]:
                                        self.fam_name = rrow[1]
                                        self.giv_name = rrow[2]
                                        need_name = False
                                        break
                        if not post:
                            # find and store the event file paths for the requested years
                            rfile = REGULAR_SEASON_FOLDER + str(year) + rteam + ".EV" + trow[1]
                            if not osp.exists(rfile):
                                raise FileNotFoundError(F"CANNOT find {season} event file {rfile}!")
                            year_events.append(rfile)
                            self.num_files += 1

                if post:
                    # find and store the event file paths for the requested years
                    post_files = POST_SEASON_FOLDER + str(year) + "*"
                    for pfile in glob.glob(post_files):
                        self.lgr.debug(F"{season} file name = {pfile}")
                        if not osp.exists(pfile):
                            raise FileNotFoundError(F"CANNOT find {season} event file {pfile}!")
                        year_events.append(pfile)
                        self.num_files += 1

                self.event_files[str(year)] = year_events

        except Exception as ex:
            self.lgr.exception(F"Exception: {repr(ex)}")

    @abstractmethod
    def collect_stats(self, p_box:pointer, player_id:str, year:str, game_id:str):
        pass

    @abstractmethod
    def check_boxscores(self, player_id:str, year:str):
        pass

    @abstractmethod
    def print_stat_line(self, year:str):
        pass

    @abstractmethod
    def print_ave_line(self):
        pass

# END class PrintStats

def process_bp_args(desc:str, exe:str, id_help:str):
    """use ArgumentParser to specify command line arguments for batching and pitching stats"""
    arg_parser = ArgumentParser(description = desc, prog = exe)
    # required arguments
    required = arg_parser.add_argument_group('REQUIRED')
    required.add_argument('-i', '--player_id', required=True, help=id_help)
    required.add_argument('-s', '--start', required=True, type=int, help="start year to find stats (yyyy)")
    # optional arguments
    arg_parser.add_argument('-e', '--end', type=int, help="end year to find stats (yyyy)")
    arg_parser.add_argument('-p', '--post', action="store_true", help="find postseason games instead of regular season")
    arg_parser.add_argument('-q', '--quiet', action="store_true", help="NO logging")
    arg_parser.add_argument('-l', '--level', default=lg.getLevelName(DEFAULT_CONSOLE_LEVEL), help="set LEVEL of logging output")

    return arg_parser


def process_bp_input(argl:list, default_id:str, default_yr:int, desc:str, prog:str, id_help:str):
    """process command line input for batching and pitching stats"""
    argp = process_bp_args(desc, prog, id_help).parse_args(argl)
    loglevel = lg.getLevelName(QUIET_LOG_LEVEL) if argp.quiet else argp.level.strip().upper()
    try:
        getattr( lg, loglevel )
    except AttributeError as ae:
        print(F"Problem with log level: {repr(ae)}")
        loglevel = DEFAULT_CONSOLE_LEVEL

    if len(argp.player_id) >= 8 and argp.player_id[:5].isalpha() and argp.player_id[5:8].isdecimal():
        player_id = argp.player_id.strip()
    else:
        print(F">>> IMPROPER player id '{argp.player_id}'! Using default value = {default_id}.\n")
        player_id = default_id
    if len(player_id) > 8:
        player_id = player_id[:8]

    if 1871 <= argp.start <= 2020:
        start = argp.start
    else:
        print(F">>> INVALID start year '{argp.start}'! Using default year = {default_yr}.\n")
        start = default_yr

    if argp.end and 1871 <= argp.end <= 2020 and argp.end >= start:
        end = argp.end
    else:
        if argp.end:
            print(F">>> INVALID end year '{argp.end}'! Using end year = {start}.\n")
        end = start

    return player_id, start, end, argp.post, loglevel


class GameSummary:
    """common functions for printing game summaries"""
    def __init__(self, logger):
        self._lgr = logger
        self._lgr.warning(F" Start {self.__class__.__name__}")
        self.note_count = 0

    # void cwbox_print_timeofgame(CWGame * game)
    def print_time_of_game(self, p_game:pointer):
        self._lgr.info("\n----------------------------------")
        tog = int(MyCwlib.game_info_lookup(p_game, b'timeofgame'))
        if tog and tog > 0:
            minutes = str(tog % 60)
            if len(minutes) == 1: minutes = "0" + minutes
            print(F"T -- {tog // 60}:{minutes}")

    # void cwbox_print_attendance(CWGame * game)
    def print_attendance(self, p_game:pointer):
        self._lgr.info("\n----------------------------------")
        print(F"A -- {MyCwlib.game_info_lookup(p_game, b'attendance')}")

    # void cwbox_print_player(CWBoxPlayer *player, CWRoster *roster)
    def print_player( self, p_player:pointer, p_roster:pointer ):
        self._lgr.info("\n----------------------------------")

        bio = None
        posstr = ''

        player = p_player.contents
        if p_roster:
            bio = MyCwlib.roster_player_find(p_roster, player.player_id)

        if bio:
            name = c_char_p_to_str(bio.contents.last_name) + " " + c_char_p_to_str(bio.contents.first_name, 1)
        else:
            name = player.name
        self._lgr.info(F"player name = {name}")

        if player.ph_inn > 0 and player.positions[0] != 11:
            posstr = "ph"
        elif player.pr_inn > 0 and player.positions[0] != 12:
            posstr = "pr"

        for pos in range( player.num_positions ):
            if len(posstr) > 0:
                posstr += '-'
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

        self._lgr.info(F"outstr = {outstr}")

        batting = player.batting.contents
        print(F"{outstr:20}{batting.pa:3}{batting.ab:4}{batting.h:4}{batting.bb:4}{batting.so:4}{batting.r:3}", end = '')
        print(F"{batting.bi:3}" if batting.bi >= 0 else "", end = '')

    # void
    # cwbox_print_player_apparatus(CWGame *game, CWBoxEvent *list, int index, char *label, CWRoster *visitors, CWRoster *home)
    def print_player_apparatus(self, p_events:pointer, index:int, label:str, p_vis:pointer, p_home:pointer):
        # Generic output for list of events (2B, 3B, WP, etc)
        self._lgr.info("\n----------------------------------")
        if not p_events:
            return
        event = p_events.contents
        comma = 0
        print(F"{label} -- ", end = '')
        while event:
            search_event = event
            bio = None
            name = ''
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
                name = event.players[index].decode("UTF8")
                self._lgr.warning("bio NOT available!")
            if comma:
                print(", ", end = '')
            if count == 1:
                if bio:
                    print( c_char_p_to_str(bio.contents.last_name) + " "
                           + c_char_p_to_str(bio.contents.first_name[0],1), end = '' )
                elif name:
                    print(name, end = '')
                else:
                    print(event.players[index].decode("UTF8"), end = '')
            else:
                if bio:
                    print(F"{c_char_p_to_str(bio.contents.last_name)} "
                          F"{c_char_p_to_str(bio.contents.first_name[0],1)} {count}", end = '')
                elif name:
                    print(F"{name} {count}", end = '')
                else:
                    print(F"{event.players[index].decode('UTF8')} {count}", end = '')
            comma = 1
        print('')
        # NOTE: reset events.mark >> NEEDED in Python?
        event = p_events.contents
        while event:
            event.mark = 0
            event = event.next.contents if event.next else None

    # void cwbox_print_apparatus(CWGame * game, CWBoxscore * boxscore, CWRoster * visitors, CWRoster * home)
    def print_apparatus( self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer ):
        # Output the apparatus (list of events and other miscellaneous game information)
        self._lgr.info("\n----------------------------------")

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
        self._lgr.info("\n----------------------------------")
        # Output one pitcher's pitching line. The parameter 'note_count' keeps track of how many apparatus notes
        # have been emitted (for pitchers who do not record an out in an inning)
        bio = None
        roster = p_roster.contents
        pitcher = p_pitcher.contents
        player_id = pitcher.player_id.decode("UTF8")
        self._lgr.info(F"player id = {player_id}")
        self._lgr.debug(F"type(player id) = {type(player_id)}")
        if roster:
            bio = MyCwlib.roster_player_find(p_roster, bytes(pitcher.player_id))
        if bio:
            name = c_char_p_to_str(bio.contents.last_name) + " " + c_char_p_to_str(bio.contents.first_name, 1)
        else:
            name = pitcher.name
        self._lgr.info(F"pitcher name = {name}")

        game = p_game.contents
        wp = MyCwlib.game_info_lookup(game, b"wp")
        self._lgr.info(F"winning pitcher id = {wp}")
        self._lgr.debug(F"type(wp) = {type(wp)}")
        lp = MyCwlib.game_info_lookup(game, b"lp")
        self._lgr.info(F"losing pitcher id = {lp}")
        save = MyCwlib.game_info_lookup(game, b"save")
        self._lgr.info(F"save pitcher id = {save}")
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
        self._lgr.info("\n----------------------------------")
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
        self._lgr.info("\n----------------------------------")
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
        self._lgr.info("\n----------------------------------")
        if not p_event:
            return
        event = p_event
        comma = 0
        print("HBP -- ", end = '')
        while event:
            search_event = event
            batter = pitcher = None
            batter_name = pitcher_name = ''
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
                batter_name = event.contents.players[0].decode("UTF8")
                self._lgr.warning("roster NOT available for batter!")
            if not pitcher:
                pitcher_name = event.contents.players[1].decode("UTF8")
                self._lgr.warning("roster NOT available for pitcher!")
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
                print(F" {count}")
            comma = 1
        print('')
        # NOTE: reset events.mark >> NEEDED in Python?
        event = p_event
        while event:
            event.contents.mark = 0
            event = event.contents.next

    # void cwbox_print_lob(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_lob(self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer):
        self._lgr.info("\n----------------------------------")
        lob = p_box.contents.lob
        if lob[0] == 0 and lob[1] == 0:
            return
        vis_city = c_char_p_to_str(p_vis.contents.city) if p_vis else MyCwlib.game_info_lookup(p_game, b"visteam")
        home_city = c_char_p_to_str(p_home.contents.city) if p_home else MyCwlib.game_info_lookup(p_game, b"hometeam")
        print(F"LOB -- {vis_city} {lob[0]}, {home_city} {lob[1]}")

    # void cwbox_print_pitcher_apparatus(CWBoxscore * boxscore)
    def print_pitcher_apparatus(self, p_box:pointer):
        # Output the pitching apparatus (list of pitchers who did not record an out in an inning)
        self._lgr.info("\n----------------------------------")

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

# END class GameSummary
