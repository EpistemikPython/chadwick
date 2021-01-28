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
__updated__ = "2021-01-27"

import copy
import csv
import glob
import sys
from argparse import ArgumentParser
from datetime import datetime as dt
from cwLibWrappers import chadwick, cwlib
from cwTools import *

STD_BAT_SPACE = 6

GM  = 0       # 0
PA  = GM+1    # 1
AB  = PA+1    # 2
RUN = AB+1    # 3
HIT = RUN+1   # 4
B2  = HIT+1   # 5
B3  = B2+1    # 6
HR  = B3+1    # 7
XBH = HR+1    # 8
RBI = XBH+1   # 9
SO  = RBI+1   # 10
BB  = SO+1    # 11
IBB = BB+1    # 12
SB  = IBB+1   # 13
CS  = SB+1    # 14
SH  = CS+1    # 15
SF  = SH+1    # 16
HBP = SF+1    # 17
GDP = HBP+1   # 18
# CWBoxBatting: int g, pa, ab, r, h, b2, b3, hr, hrslam, bi, bi2out, gw, bb, ibb, so, gdp, hp, sh, sf, sb, cs, xi;
# baseball-ref.com: G  PA  AB  R  H  2B  3B  HR  RBI  SB  CS  BB  SO  BA  OBP  SLG  OPS  OPS+  TB  GDP  HBP  SH  SF IBB
STATS_DICT = { "01G":0, "02PA":0, "03AB":0, "04R":0, "05H":0, "062B":0, "073B":0, "08HR":0, "09XBH":0, "10RBI":0,
               "11SO":0, "12BB":0, "13IBB":0, "14SB":0, "15CS":0, "16SH":0, "17SF":0, "18HBP":0, "19GDP":0 }
BATTING_KEYS = list( STATS_DICT.keys() )
BATTING_HDRS = { BATTING_KEYS[GM][:2] :F"{BATTING_KEYS[GM][2:]} ",
                 BATTING_KEYS[PA][:2] :F"{BATTING_KEYS[PA][2:]}",
                 BATTING_KEYS[AB][:2] :F"{BATTING_KEYS[AB][2:]}",
                 BATTING_KEYS[RUN][:2]:F"{BATTING_KEYS[RUN][2:]} ",
                 BATTING_KEYS[HIT][:2]:F"{BATTING_KEYS[HIT][2:]} ",
                 BATTING_KEYS[B2][:2] :F"{BATTING_KEYS[B2][2:]}",
                 BATTING_KEYS[B3][:2] :F"{BATTING_KEYS[B3][2:]}",
                 BATTING_KEYS[HR][:2] :F"{BATTING_KEYS[HR][2:]}",
                 BATTING_KEYS[XBH][:2]:F"{BATTING_KEYS[XBH][2:]}",
                 BATTING_KEYS[RBI][:2]:F"{BATTING_KEYS[RBI][2:]}",
                 BATTING_KEYS[SO][:2] :F"{BATTING_KEYS[SO][2:]}",
                 BATTING_KEYS[BB][:2] :F"{BATTING_KEYS[BB][2:]}",
                 BATTING_KEYS[IBB][:2]:F"{BATTING_KEYS[IBB][2:]}",
                 BATTING_KEYS[SB][:2] :F"{BATTING_KEYS[SB][2:]}",
                 BATTING_KEYS[CS][:2] :F"{BATTING_KEYS[CS][2:]}",
                 BATTING_KEYS[SH][:2] :F"{BATTING_KEYS[SH][2:]}",
                 BATTING_KEYS[SF][:2] :F"{BATTING_KEYS[SF][2:]}",
                 BATTING_KEYS[HBP][:2]:F"{BATTING_KEYS[HBP][2:]}",
                 BATTING_KEYS[GDP][:2]:F"{BATTING_KEYS[GDP][2:]}",
                 F"{str(GDP+2)}":" TB", F"{str(GDP+3)}":" BA", F"{str(GDP+4)}":"OBP",
                 F"{str(GDP+5)}":"SLG", F"{str(GDP+6)}":"OPS" }

def clear(stats:dict, totals:dict):
    for item in stats.keys():
        totals[item] += stats[item]
        stats[item] = 0

def print_ul():
    print(F"{''}".rjust(STD_BAT_SPACE), end = '')
    for sp in range( len(BATTING_HDRS) ):
        print(F"{'---'}".rjust(STD_BAT_SPACE), end = '')
    print(" ")

def print_hdr():
    print(F"{''}".rjust(STD_BAT_SPACE), end = '')
    for key in sorted(BATTING_HDRS):
        print(F"{BATTING_HDRS[key]}".rjust(STD_BAT_SPACE), end = '')
    print(" ")
    print_ul()


class PrintBattingStats:
    """print batting stats for a player using Retrosheet data"""
    def __init__(self, logger:logging.Logger):
        self.lgr = logger
        self.lgr.warning(F" Start {self.__class__.__name__}")
        self.event_files = {}

    def collect_stats( self, p_box:pointer, play_id:str, stats:dict, year:str ):
        self.lgr.debug(F"player = {play_id}; collect stats for year = {year}")
        bk = BATTING_KEYS
        slots = [1,1]
        players = list()
        players.insert( 0, MyCwlib.box_get_starter(p_box,0,1) )
        players.insert( 1, MyCwlib.box_get_starter(p_box,1,1) )

        while slots[0] <= 9 or slots[1] <= 9 :
            for t in range(2):
                if slots[t] <= 9:
                    player = players[t].contents.player_id.decode("UTF-8")
                    self.lgr.debug(F"player = {player}")
                    if player == play_id:
                        self.lgr.debug(F"found player = {play_id}")
                        # NOTE: misspelling 'battiing' in the python wrapper file
                        batting = players[t].contents.battiing.contents
                        stats[ bk[GM] ]  += batting.g
                        stats[ bk[PA] ]  += batting.pa
                        stats[ bk[AB] ]  += batting.ab
                        stats[ bk[RUN] ] += batting.r
                        stats[ bk[HIT] ] += batting.h
                        stats[ bk[B2] ]  += batting.b2
                        stats[ bk[B3] ]  += batting.b3
                        stats[ bk[HR] ]  += batting.hr
                        stats[ bk[XBH] ] += (batting.b2 + batting.b3 + batting.hr)
                        if batting.bi != -1:
                            stats[ bk[RBI] ] += batting.bi
                        else:
                            stats[ bk[RBI] ] = -1
                        stats[ bk[BB] ]  += batting.bb
                        stats[ bk[IBB] ] += batting.ibb
                        stats[ bk[SO] ]  += batting.so
                        stats[ bk[SB] ]  += batting.sb
                        stats[ bk[CS] ]  += batting.cs
                        stats[ bk[SH] ]  += batting.sh
                        stats[ bk[SF] ]  += batting.sf
                        stats[ bk[HBP] ] += batting.hp
                        stats[ bk[GDP] ] += batting.gdp
                    players[t] = players[t].contents.next
                    if not players[t]:
                        while slots[t] <= 9 and not players[t]:
                            slots[t] += 1
                            if slots[t] <= 9:
                                players[t] = cwlib.cw_box_get_starter(p_box, t, slots[t])

    def print_stats(self, playid:str, name:str, season:str, yrstart:int, yrend:int):
        self.lgr.info(F"print {season} stats for years {yrstart}->{yrend}")
        stats = copy.copy(STATS_DICT)
        totals = copy.copy(STATS_DICT)

        print(F"\t{name} {season} Stats:")
        print_hdr()

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
                    self.lgr.debug(F" Found game id = {game_id}; date = {game_date}")

                    box = MyCwlib.box_create(game)
                    self.collect_stats(box, playid, stats, str(year))

            self.print_stat_line(str(year), stats)
            clear(stats, totals)

        print_ul()
        print_hdr()
        self.print_stat_line("Total", totals)
        self.print_ave_line(totals, yrend-yrstart+1)
        print("")

    def print_ave_line(self, totals:dict, period:int):
        self.lgr.info(F"print average of each counting stat over span of {period} years")
        averages = copy.copy(STATS_DICT)
        for item in totals.keys():
            averages[item] = round(totals[item] / period)
        print("Ave".ljust(STD_BAT_SPACE), end = '')
        for key in sorted( averages.keys() ):
            print(F"{averages[key]}".rjust(STD_BAT_SPACE), end = '')
        # add Total Bases average
        tb = totals[BATTING_KEYS[HIT]] + totals[BATTING_KEYS[B2]] + totals[BATTING_KEYS[B3]]*2 + totals[BATTING_KEYS[HR]]*3
        tbave = round(tb / period)
        print(F"{tbave}".rjust(STD_BAT_SPACE), end = '')
        print(" ")

    def print_stat_line(self, year:str, bat:dict):
        self.lgr.info(F"print stat line for year = {year}")
        print(F"{year.ljust(STD_BAT_SPACE)}", end = '')
        # print all the counting stats from the retrosheet data
        for key in sorted( bat.keys() ):
            print(F"{bat[key]}".rjust(STD_BAT_SPACE) if bat[key] >= 0 else F"{''}".rjust(STD_BAT_SPACE), end = '')
        # add Total Bases
        tb = bat[BATTING_KEYS[HIT]] + bat[BATTING_KEYS[B2]] + bat[BATTING_KEYS[B3]]*2 + bat[BATTING_KEYS[HR]]*3
        print(F"{tb}".rjust(STD_BAT_SPACE) if tb >= 0 else F"{''}".rjust(STD_BAT_SPACE), end = '')
        # calculate and print the rate stats
        games = bat[BATTING_KEYS[GM]]
        ba = bat[ BATTING_KEYS[HIT] ] / bat[ BATTING_KEYS[AB] ] * 10000 if bat[ BATTING_KEYS[AB] ] > 0 else 0.0
        pba = str(int(ba))[:4] if ba > 0.0 else 'x' if games == 0 else "00"
        if pba != 'x' and len(pba) < 4: pba = '0' + pba
        print(F"{pba}".rjust(STD_BAT_SPACE), end = '')
        obp_num = bat[ BATTING_KEYS[HIT] ] + bat[ BATTING_KEYS[BB] ] + bat[ BATTING_KEYS[HBP] ]
        obp_denom = bat[ BATTING_KEYS[AB] ] + bat[ BATTING_KEYS[BB] ] + bat[ BATTING_KEYS[HBP] ] + bat[ BATTING_KEYS[SF] ]
        obp = obp_num / obp_denom * 10000 if obp_denom > 0 else 0.0
        pobp = str(int(obp))[:4] if obp > 0.0 else 'x' if games == 0 else "00"
        if pobp != 'x' and len(pobp) < 4: pobp = '0' + pobp
        print(F"{pobp}".rjust(STD_BAT_SPACE), end = '')
        slg = tb / bat[ BATTING_KEYS[AB] ] * 10000 if bat[ BATTING_KEYS[AB] ] > 0 else 0.0
        pslg = str(int(slg))[:4] if slg > 0.0 else 'x' if games == 0 else "00"
        if pslg != 'x' and len(pslg) < 4: pslg = '0' + pslg
        print(F"{pslg}".rjust(STD_BAT_SPACE), end = '')
        ops = obp + slg
        pops = str(int(ops))[:5] if ops > 10000 else str(ops)[:4] if ops > 0.0 else 'x' if games == 0 else "00"
        if pops != 'x' and len(pops) < 4: pops = '0' + pops
        print(F"{pops}".rjust(STD_BAT_SPACE), end = '')
        print(" ")

# END class PrintBattingStats


def process_args():
    arg_parser = ArgumentParser(
        description="Print batting stats, totals & averages from Retrosheet data for the specified years",
        prog='main_batting_stats.py' )
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
    loglevel = "CRITICAL" if args.quiet else args.level.strip().upper()
    try:
        getattr( logging, loglevel )
    except AttributeError as ae:
        print(F"Problem with log level: {repr(ae)}")
        loglevel = "INFO"

    logging.basicConfig(level = loglevel)
    logging.warning(F"process_input_parameters(): Level = {loglevel}\n--------------------------------------")
    logging.info(F"args = \n{args}")

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

    return playid, start, end, args.post, loglevel


def main_batting_stats(args:list):
    lgr = logging.getLogger("PrintBattingStats")

    playid, start, end, post, loglevel = process_input_parameters(args)

    lgr.setLevel(loglevel)
    lgr.debug( str(lgr.handlers) )
    lgr.warning(F" id = {playid}; years = {start}->{end}")

    bat_stats = PrintBattingStats(lgr)
    season = "post-season" if post else "regular season"
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
                    lgr.debug(F"Found team {rteam}")
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
                    if not post:
                        # find and store the event file paths for the requested years
                        event_file = REGULAR_SEASON_FOLDER + str(year) + rteam + ".EV" + trow[1]
                        if not os.path.exists(event_file):
                            raise FileNotFoundError(F"CANNOT find {season} event file {event_file}!")
                        year_events.append(event_file)

            if post:
                # find and store the event file paths for the requested years
                post_files = POST_SEASON_FOLDER + str(year) + "*"
                for pfile in glob.glob(post_files):
                    lgr.debug(F"pfile name = {pfile}")
                    if not os.path.exists(pfile):
                        raise FileNotFoundError(F"CANNOT find {season} event file {pfile}!")
                    year_events.append(pfile)

            bat_stats.event_files[str(year)] = year_events

        name = F"{giv_name} {fam_name}"
        lgr.warning(F"name = {name}")
        lgr.warning(F"found {len(bat_stats.event_files)} {season} event files")
        for item in bat_stats.event_files:
            lgr.debug(item)

        bat_stats.print_stats(playid, name, season, start, end)

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
