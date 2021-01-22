##############################################################################################################################
# coding=utf-8
#
# printPlayerStats.py -- print a summary of baseball game or games using Retrosheet data
#
# Original C code Copyright (c) 2002-2020
# Dr T L Turocy, Chadwick Baseball Bureau (ted.turocy@gmail.com)
#
# Port to Python3 and modifications Copyright (c) 2019-2021 Mark Sattolo <epistemik@gmail.com>

__author__       = "Mark Sattolo"
__author_email__ = "epistemik@gmail.com"
__created__ = "2021-01-21"
__updated__ = "2021-01-21"

import csv
import sys
from argparse import ArgumentParser
from datetime import datetime as dt
from cwLibWrappers import chadwick, cwlib
from cwTools import *


# noinspection PyAttributeOutsideInit
class PrintPlayerStats:
    def __init__(self, cwt:MyChadwickTools, logger:logging.Logger):
        self.cwtools = cwt
        self.lgr = logger
        self.lgr.warning(F" Start {self.__class__.__name__}")
        self.event_files = {}
        self.games = {}
        self.year_stats = {}
        self.clear()

    def clear(self, stats:dict=None):
        self.ab = [0,0]
        self.r  = [0,0]
        self.h  = [0,0]
        self.bi = [0,0]
        self.pa = [0,0]
        self.bb = [0,0]
        self.so = [0,0]
        if stats:
            stats["ab"] = 0
            stats["bb"] = 0
            stats["so"] = 0
            stats["pa"] = 0
            stats["bi"] = 0
            stats["h"] = 0
            stats["r"] = 0

    def collect_stats( self, p_box:pointer, play_id:str, stats:dict, year:str ):
        self.lgr.debug(F"collect stats for year = {year}")
        slots = [1,1]
        players = list()
        self.lgr.info(F"player = {play_id}")
        player0 = MyCwlib.box_get_starter(p_box, 0, 1)
        self.lgr.debug(F"type(player0) = {type(player0)}")
        players.insert(0, player0)
        player1 = MyCwlib.box_get_starter(p_box, 1, 1)
        self.lgr.debug(F"type(player1) = {type(player1)}")
        players.insert(1, player1)

        while slots[0] <= 9 or slots[1] <= 9 :
            for t in range(0,2):
                if slots[t] <= 9:
                    player = players[t].contents.player_id.decode("UTF-8")
                    # self.lgr.info(F"players[t] = {players[t]}")
                    self.lgr.debug(F"player = {player}")
                    if player == play_id:
                        self.lgr.info(F"found player {play_id}")
                        # NOTE: misspelling 'battiing' in the python wrapper file
                        batting = players[t].contents.battiing.contents
                        stats["ab"] += batting.ab
                        stats["bb"] += batting.bb
                        stats["so"] += batting.so
                        stats["pa"] += batting.pa
                        stats["h"] += batting.h
                        stats["r"] += batting.r
                        # self.ab[t] += batting.ab
                        # self.r[t]  += batting.r
                        # self.h[t]  += batting.h
                        # self.bb[t] += batting.bb
                        # self.pa[t] += batting.pa
                        # self.so[t] += batting.so
                        if batting.bi != -1:
                            stats["bi"] += batting.bi
                        else:
                            stats["bi"] = -1
                    players[t] = players[t].contents.next
                    if not players[t]:
                        # In some National Association games, teams played with 8 players.
                        # This generalization allows for printing boxscores when some batting slots are empty.
                        while slots[t] <= 9 and not players[t]:
                            slots[t] += 1
                            if slots[t] <= 9:
                                players[t] = cwlib.cw_box_get_starter(p_box, t, slots[t])

    def add(self, year:str, stats:dict):
        self.year_stats[year] = stats

    # void cwbox_print_text(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_stats(self, year:str, stats:dict):
        self.lgr.info(F"print stats for year = {year}")
        ab = stats["ab"]
        bb = stats["bb"]
        so = stats["so"]
        bi = stats["bi"]
        pa = stats["pa"]
        h = stats["h"]
        r = stats["r"]
        # ab = self.ab
        # pa = self.pa
        # bb = self.bb
        # so = self.so
        # bi = self.bi
        # h = self.h
        # r = self.r

        print(F"{year.ljust(4)}{pa:5}{ab:5}{h:5}{bb:5}{so:5}{r:5}", end = '')
        print(F"{bi:5} " if bi >= 0 else "    ", end = '')
        print("")

# END class PrintPlayerStats


def process_args():
    arg_parser = ArgumentParser(description="Print player combined stats from Retrosheet data for the specified years",
                                prog='main_chadwick_py3.py')
    # required arguments
    required = arg_parser.add_argument_group('REQUIRED')
    required.add_argument('-i', '--player_id', required=True, help="Retrosheet id for a player, e.g. aaroh101, bondb101")
    required.add_argument('-s', '--start', required=True, type=int, help="start year to find stats (yyyy)")
    required.add_argument('-e', '--end', required=True, type=int, help="end year to find stats (yyyy)")
    # optional arguments
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

    playid = args.player_id.strip() if len(args.player_id) >= 8 and \
         args.player_id[:5].isalpha() and args.player_id[5:8].isdecimal() else "maysw001"
    if len(playid) > 8:
        playid = playid[:8]
    logging.warning(F"id = {playid}")

    start = args.start if 1871 <= args.start <= 2020 else 1954
    logging.warning(F"start = {start}")

    end = args.end if 1871 <= args.end <= 2020 else 1955
    if args.end < args.start: end = start
    logging.warning(F"end = {end}")

    return playid, start, end, loglevel


def main_player_stats(args:list):
    lgr = logging.getLogger("PrintPlayerStats")

    playid, start, end, loglevel = process_input_parameters(args)

    lgr.setLevel(loglevel)
    lgr.debug( str(lgr.handlers) )
    lgr.warning(F" id = {playid}; years = {start}->{end}")

    cwtools = MyChadwickTools(lgr)
    player_stats = PrintPlayerStats(cwtools, lgr)
    need_name = True
    fam_name = playid
    giv_name = ""
    # TODO:
    #   get ALL the event files for the requested years
    #   go through each event line for the files and find where player == 'BAT_ID' and save these
    #   go through each file and look for the batting stats of the player and sum
    try:
        for year in range(start, end+1):
            year_events = list()
            # get the team files
            team_file_name = REGULAR_SEASON_FOLDER + "TEAM" + str(year)
            lgr.info(F"team file name = {team_file_name}")
            with open(team_file_name, newline = '') as team_csvfile:
                team_reader = csv.reader(team_csvfile)
                for trow in team_reader:
                    rteam = trow[0]
                    lgr.info(F"Found team {rteam}")
                    # get the rosters
                    if need_name:
                        roster_file = ROSTERS_FOLDER + rteam + str(year) + ".ROS"
                        lgr.debug(F"roster file name = {roster_file}")
                        if not os.path.exists(roster_file):
                            raise FileNotFoundError(F"CANNOT find roster file {roster_file}!")
                        with open(roster_file, newline = '') as roster_csvfile:
                            ros_reader = csv.reader(roster_csvfile)
                            for rrow in ros_reader:
                                if playid == rrow[0]:
                                    fam_name = rrow[1]
                                    giv_name = rrow[2]
                                    need_name = False
                                    break
                    # find and store the event file paths
                    event_file = REGULAR_SEASON_FOLDER + str(year) + rteam + ".EV" + trow[1]
                    if not os.path.exists(event_file):
                        raise FileNotFoundError(F"CANNOT find event file {event_file}!")
                    year_events.append(event_file)
            player_stats.event_files[str(year)] = year_events

        lgr.warning(F"name = {giv_name} {fam_name}")
        lgr.warning(F"found {len(player_stats.event_files)} year-event files")
        for item in player_stats.event_files:
            lgr.debug(item)

        print(F"\t{giv_name} {fam_name} Stats:")
        print(F"{'':4}   PA   AB    H   BB   SO    R  RBI")
        print(F"{''.ljust(4)}   --   --   --   --   --   --  ---")

        stats = {"ab":0, "bb":0, "so":0, "pa":0, "bi":0, "h":0, "r":0}
        # get all the games for the requested team in the supplied date range
        for year in range(start, end+1):
            lgr.info(F"collect stats for year: {year}")
            for evteam in player_stats.event_files[str(year)]:
                lgr.info(F"found events for team = {evteam}")
                cwgames = chadwick.games(evteam)
                for game in cwgames:
                    game_id = game.contents.game_id.decode(encoding='UTF-8')
                    game_date = game_id[3:11]
                    lgr.info(F" Found game id = {game_id}; date = {game_date}")

                    box = MyCwlib.box_create(game)
                    player_stats.collect_stats(box, playid, stats, str(year))

            player_stats.print_stats(str(year), stats)
            player_stats.clear(stats)

    except Exception as ex:
        lgr.exception(F"Exception: {repr(ex)}")


if __name__ == "__main__":
    run_start_time = dt.now()
    if '-q' not in sys.argv:
        logging.critical(F"Run Start time = {run_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    main_player_stats(sys.argv[1:])
    if '-q' not in sys.argv:
        run_time = (dt.now() - run_start_time).total_seconds()
        logging.critical(F" Running time = {(run_time // 60)} minutes, {(run_time % 60):2.3} seconds")
    exit()
