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
__updated__ = "2021-08-08"

import csv
import glob
import sys
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from ctypes import c_char_p, pointer
from cwLibWrappers import MyCwlib, chadwick
sys.path.append("/home/marksa/git/Python/utils")
from mhsUtils import lg, get_base_filename, osp, UTF8_ENCODING, BASE_DEV_FOLDER, BASE_GIT_FOLDER
from mhsLogging import DEFAULT_CONSOLE_LEVEL, DEFAULT_FILE_LEVEL, QUIET_LOG_LEVEL

LABEL_TOTAL = "Total"
POST_SEASON = "post-season"
REG_SEASON  = "regular season"
POSITIONS = ["", "p", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf", "dh", "ph", "pr"]
MARKERS   = ['*', '+', '#']
STD_SPACE_SIZE = 6
STD_HDR_SIZE   = 4

RETROSHEET_START_YEAR = 1871
RETROSHEET_AVAIL_YEAR = 1974
RETROSHEET_END_YEAR   = 2021
RETROSHEET_ID_SIZE    = 8
RETROSHEET_ID_ALPHA   = 5

RETROSHEET_FOLDER  = osp.join(BASE_GIT_FOLDER, "clone" + osp.sep + "ChadwickBureau" + osp.sep + "retrosheet")
ROSTERS_FOLDER     = osp.join(RETROSHEET_FOLDER, "rosters")
EVENTS_FOLDER      = osp.join(RETROSHEET_FOLDER, "event")
REG_SEASON_FOLDER  = osp.join(EVENTS_FOLDER, "regular")
POST_SEASON_FOLDER = osp.join(EVENTS_FOLDER, "post")
BOXSCORE_FOLDER    = osp.join(BASE_DEV_FOLDER, "Retrosheet" + osp.sep + "data" + osp.sep + "boxscores")

def c_char_p_to_str(lpcc:c_char_p, maxlen:int = 32) -> str:
    """Obtain a python string from a C-type char array:
           convert and concatenate the values until hit the null terminator or the char limit."""
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

def get_print_strx(num:float, games:int, prec:int, lim:int = STD_SPACE_SIZE, lead_zero:bool = False) -> str:
    """Round a stat number to the requested precision and convert to a formatted string."""
    if games == 0: return 'x'
    rnum = round(num, prec)
    pnum = F"{rnum:-{lim}.{prec}f}"
    return pnum if lead_zero else pnum.lstrip(" 0")


class PrintStats(ABC):
    """Print batting or pitching stats for a specified player using Retrosheet data."""
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
        """Print regular or post-season stats for player 'player_id' in years <yrstart> to <yrend>."""
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
                    game_id = game.contents.game_id.decode(encoding = UTF8_ENCODING)
                    game_date = game_id[3:11]
                    self.lgr.debug(F" Found game id = {game_id}; date = {game_date}")

                    box = MyCwlib.box_create(game)
                    self.collect_stats(box, player_id, str_year, game_id)

            self.lgr.info(F"found {len(self.game_ids)} {year} games with {player_id} stats.")

            if year < RETROSHEET_AVAIL_YEAR and season == REG_SEASON:
                self.check_boxscores(player_id, str_year)

            self.print_stat_line(str_year)
            self.sum_and_clear()

        if self.num_years > 1:
            self.print_hdr_uls()
            if self.num_years > 5:
                self.print_header()
            self.print_stat_line(LABEL_TOTAL)
            self.print_ave_line()
        print('')

    def get_events(self, post:bool, pers_id:str, start:int, end:int):
        """Get the required event files for batting and pitching stats."""
        season = POST_SEASON if post else REG_SEASON
        self.lgr.info(F"get the {season} events for player {pers_id} in years {start}->{end}")
        need_name = True
        self.fam_name = pers_id
        try:
            for year in range(start, end+1):
                year_events = list()
                # get the team files
                team_file_name = osp.join(REG_SEASON_FOLDER, "TEAM" + str(year))
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
                            roster_file = osp.join(ROSTERS_FOLDER, rteam + str(year) + osp.extsep + "ROS")
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
                            rfile = osp.join(REG_SEASON_FOLDER, str(year) + rteam + osp.extsep + "EV" + trow[1])
                            if not osp.exists(rfile):
                                raise FileNotFoundError(F"CANNOT find {season} event file {rfile}!")
                            year_events.append(rfile)
                            self.num_files += 1

                if post:
                    # find and store the event file paths for the requested years
                    post_files = osp.join(POST_SEASON_FOLDER, str(year) + "*")
                    for pfile in glob.glob(post_files):
                        self.lgr.debug(F"{season} file name = {pfile}")
                        if not osp.exists(pfile):
                            raise FileNotFoundError(F"CANNOT find {season} event file {pfile}!")
                        year_events.append(pfile)
                        self.num_files += 1

                self.event_files[str(year)] = year_events

        except Exception as ex:
            raise ex

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
    """Use ArgumentParser to specify command line arguments for batting and pitching stats."""
    arg_parser = ArgumentParser(description = desc, prog = exe)
    # required arguments
    required = arg_parser.add_argument_group('REQUIRED')
    required.add_argument('-i', '--player_id', required=True, help=id_help)
    required.add_argument('-s', '--start', required=True, type=int, help="start year to find stats (yyyy)")
    # optional arguments
    arg_parser.add_argument('-e', '--end', type=int, help="end year to find stats (yyyy)")
    arg_parser.add_argument('-p', '--post', action="store_true", help=F"find {POST_SEASON} games instead of {REG_SEASON}")
    arg_parser.add_argument('-q', '--quiet', action="store_true", help="NO logging")
    arg_parser.add_argument('-c', '--levcon', default=lg.getLevelName(DEFAULT_CONSOLE_LEVEL),
                            help="set LEVEL of console logging output")
    arg_parser.add_argument('-f', '--levfile', default=lg.getLevelName(DEFAULT_FILE_LEVEL),
                            help="set LEVEL of file logging output")

    return arg_parser


def process_bp_input(argl:list, default_id:str, default_yr:int, desc:str, prog:str, id_help:str):
    """Process command line input for batting and pitching stats."""
    argp = process_bp_args(desc, prog, id_help).parse_args(argl)

    con_level = lg.getLevelName(QUIET_LOG_LEVEL) if argp.quiet else argp.levcon.strip().upper()
    try:
        getattr( lg, con_level )
    except AttributeError as ae:
        print(F"Problem with console log level: {repr(ae)}")
        con_level = DEFAULT_CONSOLE_LEVEL
    file_level = argp.levfile.strip().upper()
    try:
        getattr( lg, file_level )
    except AttributeError as ae:
        print(F"Problem with file log level: {repr(ae)}")
        file_level = DEFAULT_FILE_LEVEL

    if len(argp.player_id) >= RETROSHEET_ID_SIZE and argp.player_id[:RETROSHEET_ID_ALPHA].isalpha() \
            and argp.player_id[RETROSHEET_ID_ALPHA:RETROSHEET_ID_SIZE].isdecimal():
        player_id = argp.player_id.strip()
    else:
        print(F">>> IMPROPER player id '{argp.player_id}'! Using default value = {default_id}.\n")
        player_id = default_id
    if len(player_id) > RETROSHEET_ID_SIZE:
        player_id = player_id[:RETROSHEET_ID_SIZE]

    if RETROSHEET_START_YEAR <= argp.start <= RETROSHEET_END_YEAR:
        start = argp.start
    else:
        print(F">>> INVALID start year '{argp.start}'! Using default year = {default_yr}.\n")
        start = default_yr

    if argp.end and RETROSHEET_START_YEAR <= argp.end <= RETROSHEET_END_YEAR and argp.end >= start:
        end = argp.end
    else:
        if argp.end:
            print(F">>> INVALID end year '{argp.end}'! Using end year = {start}.\n")
        end = start

    return player_id, start, end, argp.post, con_level, file_level
