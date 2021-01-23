##############################################################################################################################
# coding=utf-8
#
# printBattingStats.py -- print batting stats for a player using Retrosheet data
#
# Original C code Copyright (c) 2002-2020
# Dr T L Turocy, Chadwick Baseball Bureau (ted.turocy@gmail.com)
#
# Port to Python3, additions & modifications Copyright (c) 2019-2021 Mark Sattolo <epistemik@gmail.com>

__author__       = "Mark Sattolo"
__author_email__ = "epistemik@gmail.com"
__created__ = "2021-01-21"
__updated__ = "2021-01-23"

import copy
import csv
import sys
from argparse import ArgumentParser
from datetime import datetime as dt
from cwLibWrappers import chadwick, cwlib
from cwTools import *

BATTING_KEYS = ["01g","02pa","03ab","04r","05h","06b2","07b3","08hr","09bi","10so","11bb","12ibb","13sb","14cs"]
BATTING_HDRS = {"01":" G ", "02":" PA", "03":" AB", "04":" R ", "05":" H ", "06":" B2", "07":" B3", "08":" HR", "09":"RBI",
                "10":" SO", "11":" BB", "12":"IBB", "13":" SB", "14":" CS", "15":" BA"}


def clear(stats:dict, totals:dict):
    for item in stats.keys():
        totals[item] += stats[item]
        stats[item] = 0


class PrintBattingStats:
    def __init__(self, cwt:MyChadwickTools, logger:logging.Logger):
        self.cwtools = cwt
        self.lgr = logger
        self.lgr.warning(F" Start {self.__class__.__name__}")
        self.event_files = {}
        self.games = {}
        self.year_stats = {}

    def collect_stats( self, p_box:pointer, play_id:str, stats:dict, year:str ):
        self.lgr.debug(F"player = {play_id}; collect stats for year = {year}")
        bk = BATTING_KEYS
        slots = [1,1]
        players = list()
        players.insert( 0, MyCwlib.box_get_starter(p_box, 0, 1) )
        players.insert( 1, MyCwlib.box_get_starter(p_box, 1, 1) )

        while slots[0] <= 9 or slots[1] <= 9 :
            for t in range(0,2):
                if slots[t] <= 9:
                    player = players[t].contents.player_id.decode("UTF-8")
                    self.lgr.debug(F"player = {player}")
                    if player == play_id:
                        self.lgr.debug(F"found player = {play_id}")
                        # NOTE: misspelling 'battiing' in the python wrapper file
                        batting = players[t].contents.battiing.contents
                        stats[ bk[0] ] += batting.g
                        stats[ bk[1] ] += batting.pa
                        stats[ bk[2] ] += batting.ab
                        stats[ bk[3] ] += batting.r
                        stats[ bk[4] ] += batting.h
                        stats[ bk[5] ] += batting.b2
                        stats[ bk[6] ] += batting.b3
                        stats[ bk[7] ] += batting.hr
                        if batting.bi != -1:
                            stats[ bk[8] ] += batting.bi
                        else:
                            stats[ bk[8] ] = -1
                        stats[ bk[9] ] += batting.bb
                        stats[ bk[10] ] += batting.ibb
                        stats[ bk[11] ] += batting.so
                        stats[ bk[12] ] += batting.sb
                        stats[ bk[13] ] += batting.cs
                    players[t] = players[t].contents.next
                    if not players[t]:
                        while slots[t] <= 9 and not players[t]:
                            slots[t] += 1
                            if slots[t] <= 9:
                                players[t] = cwlib.cw_box_get_starter(p_box, t, slots[t])

    def print_stats(self, playid, name, yrstart, yrend):
        # CWBoxBatting: int g, pa, ab, r, h, b2, b3, hr, hrslam, bi, bi2out, gw, bb, ibb, so, gdp, hp, sh, sf, sb, cs, xi;
        # Baseball Ref:     G  PA  AB  R  H  2B  3B  HR  RBI  SB  CS  BB  SO  BA  OBP  SLG  OPS  OPS+  TB  GDP  HBP  SH  SF IBB
        bk = BATTING_KEYS
        stats = { bk[0]:0, bk[1]:0, bk[2]:0, bk[3]:0, bk[4]:0, bk[5]:0, bk[6]:0, bk[7]:0, bk[8]:0, bk[9]:0,
                  bk[10]:0, bk[11]:0, bk[12]:0, bk[13]:0}
        totals = copy.copy(stats)

        print(F"\t{name} Stats:")
        print(F"{''}".rjust(STD_PRINT_SPACE), end = '')
        for key in sorted( BATTING_HDRS ):
            print(F"{BATTING_HDRS[key]}".rjust(STD_PRINT_SPACE), end = '')
        print(" ")
        print(F"{''}".rjust(STD_PRINT_SPACE), end = '')
        for sp in range(0,len(BATTING_HDRS)):
            print(F"{'---'}".rjust(STD_PRINT_SPACE), end = '')
        print(" ")

        # get all the games in the supplied date range
        for year in range(yrstart, yrend+1):
            self.lgr.info(F"collect stats for year: {year}")
            if str(year) not in self.event_files.keys():
                continue
            for efile in self.event_files[str(year)]:
                self.lgr.info(F"found events for team/year = {efile[-11:-4]}")
                cwgames = chadwick.games(efile)
                for game in cwgames:
                    game_id = game.contents.game_id.decode(encoding = 'UTF-8')
                    game_date = game_id[3:11]
                    self.lgr.info(F" Found game id = {game_id}; date = {game_date}")

                    box = MyCwlib.box_create(game)
                    self.collect_stats(box, playid, stats, str(year))

            self.print_stat_line(str(year), stats)
            clear(stats, totals)

        print(F"{''}".rjust(STD_PRINT_SPACE), end = '')
        for sp in range(0,len(stats)):
            print(F"{'---'}".rjust(STD_PRINT_SPACE), end = '')
        print(" ")
        print(F"{''}".rjust(STD_PRINT_SPACE), end = '')
        for key in sorted( BATTING_HDRS ):
            print(F"{BATTING_HDRS[key]}".rjust(STD_PRINT_SPACE), end = '')
        print(" ")
        print(F"{''}".rjust(STD_PRINT_SPACE), end = '')
        for sp in range(0,len(BATTING_HDRS)):
            print(F"{'---'}".rjust(STD_PRINT_SPACE), end = '')
        print(" ")
        self.print_stat_line("Total", totals)
        print("")

    def print_stat_line(self, year:str, bat:dict):
        self.lgr.info(F"print stats for year = {year}")
        print(F"{year.ljust(STD_PRINT_SPACE)}", end = '')
        for key in sorted( bat.keys() ):
            print(F"{bat[key]}".rjust(STD_PRINT_SPACE) if bat[key] >= 0 else F"{''}".rjust(STD_PRINT_SPACE), end = '')
        print(" ")

# END class PrintPlayerStats


def process_args():
    arg_parser = ArgumentParser(description="Print player combined stats from Retrosheet data for the specified years",
                                prog='main_chadwick_py3.py')
    # required arguments
    required = arg_parser.add_argument_group('REQUIRED')
    required.add_argument('-i', '--player_id', required=True, help="Retrosheet id for a player, e.g. aaroh101, bondb101")
    required.add_argument('-s', '--start', required=True, type=int, help="start year to find stats (yyyy)")
    # optional arguments
    arg_parser.add_argument('-e', '--end', type=int, help="end year to find stats (yyyy)")
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
         args.player_id[:5].isalpha() and args.player_id[5:8].isdecimal() else "maysw101"
    if len(playid) > 8:
        playid = playid[:8]
    logging.warning(F"id = {playid}")

    start = args.start if 1871 <= args.start <= 2020 else 1954
    logging.warning(F"start = {start}")

    end = args.end if args.end and 1871 <= args.end <= 2020 else start
    if end < start: end = start
    logging.warning(F"end = {end}")

    return playid, start, end, loglevel


def main_batting_stats(args:list):
    lgr = logging.getLogger("PrintPlayerStats")

    playid, start, end, loglevel = process_input_parameters(args)

    lgr.setLevel(loglevel)
    lgr.debug( str(lgr.handlers) )
    lgr.warning(F" id = {playid}; years = {start}->{end}")

    cwtools = MyChadwickTools(lgr)
    bat_stats = PrintBattingStats(cwtools, lgr)
    need_name = True
    fam_name = playid
    giv_name = ""
    try:
        for year in range(start, end+1):
            year_events = list()
            # get the team files
            team_file_name = REGULAR_SEASON_FOLDER + "TEAM" + str(year)
            lgr.info(F"team file name = {team_file_name}")
            if not os.path.exists(team_file_name):
                lgr.exception(F"CANNOT find team file {team_file_name}!")
                continue
            with open(team_file_name, newline = '') as team_csvfile:
                team_reader = csv.reader(team_csvfile)
                for trow in team_reader:
                    rteam = trow[0]
                    lgr.info(F"Found team {rteam}")
                    # search rosters for the player's full name
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
                    # find and store the event file paths for the requested years
                    event_file = REGULAR_SEASON_FOLDER + str(year) + rteam + ".EV" + trow[1]
                    if not os.path.exists(event_file):
                        raise FileNotFoundError(F"CANNOT find event file {event_file}!")
                    year_events.append(event_file)
            bat_stats.event_files[str(year)] = year_events

        name = F"{giv_name} {fam_name}"
        lgr.warning(F"name = {name}")
        lgr.warning(F"found {len(bat_stats.event_files)} year-event files")
        for item in bat_stats.event_files:
            lgr.debug(item)

        bat_stats.print_stats(playid, name, start, end)

    except Exception as ex:
        lgr.exception(F"Exception: {repr(ex)}")


if __name__ == "__main__":
    run_start_time = dt.now()
    if '-q' not in sys.argv:
        logging.critical(F"Run Start time = {run_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    main_batting_stats(sys.argv[1:])
    if '-q' not in sys.argv:
        run_time = (dt.now() - run_start_time).total_seconds()
        logging.critical(F" Running time = {(run_time // 60)} minutes, {(run_time % 60):2.3} seconds")
    exit()
