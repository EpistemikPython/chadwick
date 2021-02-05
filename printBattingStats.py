##############################################################################################################################
# coding=utf-8
#
# printBattingStats.py -- print batting stats for a player using Retrosheet data
#
# Original C code Copyright (c) 2002-2021
# Dr T L Turocy, Chadwick Baseball Bureau (ted.turocy@gmail.com)
#
# Port to Python3, additions & modifications Copyright (c) 2019-2021 Mark Sattolo <epistemik@gmail.com>

__author__       = "Mark Sattolo"
__author_email__ = "epistemik@gmail.com"
__created__ = "2021-01-21"
__updated__ = "2021-02-05"

import copy
import csv
import glob
import sys
from argparse import ArgumentParser
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
LAST = GDP+1  # end of available counting stats
# CWBoxBatting: int g, pa, ab, r, h, b2, b3, hr, hrslam, bi, bi2out, gw, bb, ibb, so, gdp, hp, sh, sf, sb, cs, xi;
# baseball-ref.com: G  PA  AB  R  H  2B  3B  HR  RBI  SB  CS  BB  SO  BA  OBP  SLG  OPS  OPS+  TB  GDP  HBP  SH  SF IBB
STATS_DICT = { "G ":0, "PA":0, "AB":0, "R ":0, "H ":0, "2B":0, "3B":0, "HR":0, "XBH":0, "RBI":0, "SO":0,
               "BB":0, "IBB":0, "SB":0, "CS":0, "SH":0, "SF":0, "HBP":0, "GDP":0, "TB":0, "BA":0, "OBP":0,
               "SLG":0, "OPS":0 }
BATTING_HDRS = list( STATS_DICT.keys() )

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
    for key in BATTING_HDRS:
        print(F"{key}".rjust(STD_BAT_SPACE), end = '')
    print(" ")
    print_ul()


class PrintBattingStats:
    """print batting stats for a player using Retrosheet data"""
    def __init__(self, logger:logging.Logger):
        self.lgr = logger
        self.lgr.warning(F" Start {self.__class__.__name__}")
        self.event_files = {}
        self.num_years = 0

    def collect_stats( self, p_box:pointer, play_id:str, stats:dict, year:str ):
        self.lgr.debug(F"player = {play_id}; collect stats for year = {year}")
        hdrs = BATTING_HDRS
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
                        batting = players[t].contents.batting.contents
                        stats[ hdrs[GM] ]  += batting.g
                        stats[ hdrs[PA] ]  += batting.pa
                        stats[ hdrs[AB] ]  += batting.ab
                        stats[ hdrs[RUN] ] += batting.r
                        stats[ hdrs[HIT] ] += batting.h
                        stats[ hdrs[B2] ]  += batting.b2
                        stats[ hdrs[B3] ]  += batting.b3
                        stats[ hdrs[HR] ]  += batting.hr
                        stats[ hdrs[XBH] ] += (batting.b2 + batting.b3 + batting.hr)
                        if batting.bi != -1:
                            stats[ hdrs[RBI] ] += batting.bi
                        else:
                            stats[ hdrs[RBI] ] = -1
                        stats[ hdrs[BB] ]  += batting.bb
                        stats[ hdrs[IBB] ] += batting.ibb
                        stats[ hdrs[SO] ]  += batting.so
                        stats[ hdrs[SB] ]  += batting.sb
                        stats[ hdrs[CS] ]  += batting.cs
                        stats[ hdrs[SH] ]  += batting.sh
                        stats[ hdrs[SF] ]  += batting.sf
                        stats[ hdrs[HBP] ] += batting.hp
                        stats[ hdrs[GDP] ] += batting.gdp
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

        print(F"\n\t{name.upper()} {season} Stats:")
        print_hdr()

        # get all the games in the supplied date range
        for year in range(yrstart, yrend+1):
            self.lgr.info(F"collect stats for year: {year}")
            if str(year) not in self.event_files.keys():
                continue
            for efile in self.event_files[str(year)]:
                self.lgr.info(F"found events for team/year = {get_basename(efile)}")
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
        self.print_ave_line(totals)
        print("")

    def print_ave_line(self, totals:dict):
        # NOTE: ave for each 150 games ?
        averages = copy.copy(STATS_DICT)
        for item in totals.keys():
            averages[item] = round(totals[item] / self.num_years)
        print("Ave".ljust(STD_BAT_SPACE), end = '')
        for key in BATTING_HDRS:
            if key == BATTING_HDRS[LAST]:
                break
            print(F"{averages[key]}".rjust(STD_BAT_SPACE), end = '')
        # add Total Bases average
        tb = totals[BATTING_HDRS[HIT]] + totals[BATTING_HDRS[B2]] + totals[BATTING_HDRS[B3]]*2 + totals[BATTING_HDRS[HR]]*3
        tbave = round(tb / self.num_years)
        print( F"{tbave}".rjust(STD_BAT_SPACE) )
        print(F"\nprinted Average of each counting stat for {self.num_years} ACTIVE years")

    def print_stat_line(self, year:str, bat:dict):
        self.lgr.info(F"print stat line for year = {year}")
        print(F"{year.ljust(STD_BAT_SPACE)}", end = '')
        hdrs = BATTING_HDRS

        # print all the counting stats from the retrosheet data
        for key in hdrs:
            if key == BATTING_HDRS[LAST]:
                break
            print(F"{bat[key]}".rjust(STD_BAT_SPACE) if bat[key] >= 0 else F"{''}".rjust(STD_BAT_SPACE), end = '')
        # add Total Bases
        tb = bat[ hdrs[HIT] ] + bat[ hdrs[B2] ] + bat[ hdrs[B3] ]*2 + bat[ hdrs[HR] ]*3
        print(F"{tb}".rjust(STD_BAT_SPACE) if tb >= 0 else F"{''}".rjust(STD_BAT_SPACE), end = '')

        # calculate and print the rate stats
        games = bat[ hdrs[GM] ]
        # keep track of ACTIVE years
        if year != TOTAL and games > 0: self.num_years += 1

        ba = bat[ hdrs[HIT] ] / bat[ hdrs[AB] ] * 10000 if bat[ hdrs[AB] ] > 0 else 0.0
        pba = str(int(ba))[:4] if ba > 0.0 else 'x' if games == 0 else "00"
        if pba != 'x' and len(pba) < 4: pba = '0' + pba
        print(F"{pba}".rjust(STD_BAT_SPACE), end = '')

        obp_num = bat[ hdrs[HIT] ] + bat[ hdrs[BB] ] + bat[ hdrs[HBP] ]
        obp_denom = bat[ hdrs[AB] ] + bat[ hdrs[BB] ] + bat[ hdrs[HBP] ] + bat[ hdrs[SF] ]
        obp = obp_num / obp_denom * 10000 if obp_denom > 0 else 0.0
        pobp = str(int(obp))[:4] if obp > 0.0 else 'x' if games == 0 else "00"
        if pobp != 'x' and len(pobp) < 4: pobp = '0' + pobp
        print(F"{pobp}".rjust(STD_BAT_SPACE), end = '')

        slg = tb / bat[ hdrs[AB] ] * 10000 if bat[ hdrs[AB] ] > 0 else 0.0
        pslg = str(int(slg))[:4] if slg > 0.0 else 'x' if games == 0 else "00"
        if pslg != 'x' and len(pslg) < 4: pslg = '0' + pslg
        print(F"{pslg}".rjust(STD_BAT_SPACE), end = '')

        ops = int( obp + slg )
        pops = str(ops)[:5] if ops > 10000 else str(ops)[:4] if ops > 0 else 'x' if games == 0 else "00"
        if pops != 'x' and len(pops) < 4: pops = '0' + pops
        print( F"{pops}".rjust(STD_BAT_SPACE) )

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
    arg_parser.add_argument('-l', '--level', default=DEFAULT_LOG_LEVEL, help="set LEVEL of logging output")

    return arg_parser


def process_input_parameters(argx:list):
    args = process_args().parse_args(argx)
    loglevel = QUIET_LOG_LEVEL if args.quiet else args.level.strip().upper()
    try:
        getattr( logging, loglevel )
    except AttributeError as ae:
        print(F"Problem with log level: {repr(ae)}")
        loglevel = DEFAULT_LOG_LEVEL

    playid = args.player_id.strip() if len(args.player_id) >= 8 and \
                args.player_id[:5].isalpha() and args.player_id[5:8].isdecimal() else "maysw101"
    if len(playid) > 8:
        playid = playid[:8]

    start = args.start if 1871 <= args.start <= 2020 else 1954

    end = args.end if args.end and 1871 <= args.end <= 2020 else start
    if end < start: end = start

    return playid, start, end, args.post, loglevel


def main_batting_stats(args:list):

    playid, start, end, post, loglevel = process_input_parameters(args)

    lgr = get_logger(__file__, file_ts, loglevel)
    lgr.debug(F"loglevel = {repr(loglevel)}")
    lgr.warning(F" id = {playid}; years = {start}->{end}")

    bat_stats = PrintBattingStats(lgr)
    season = "post-season" if post else "regular season"
    need_name = True
    fam_name = playid
    giv_name = ""
    num_files = 0
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
                        rfile = REGULAR_SEASON_FOLDER + str(year) + rteam + ".EV" + trow[1]
                        if not os.path.exists(rfile):
                            raise FileNotFoundError(F"CANNOT find {season} event file {rfile}!")
                        year_events.append(rfile)
                        num_files += 1

            if post:
                # find and store the event file paths for the requested years
                post_files = POST_SEASON_FOLDER + str(year) + "*"
                for pfile in glob.glob(post_files):
                    lgr.debug(F"pfile name = {pfile}")
                    if not os.path.exists(pfile):
                        raise FileNotFoundError(F"CANNOT find {season} event file {pfile}!")
                    year_events.append(pfile)
                    num_files += 1

            bat_stats.event_files[str(year)] = year_events

        name = F"{giv_name} {fam_name}"
        lgr.warning(F"name = {name}")
        lgr.warning(F"found {num_files} {season} event files over {len(bat_stats.event_files)} years.")
        for item in bat_stats.event_files:
            lgr.debug(item)

        bat_stats.print_stats(playid, name, season, start, end)

    except Exception as ex:
        lgr.exception(F"Exception: {repr(ex)}")


if __name__ == "__main__":
    run_start_time = dt.now()
    if '-q' not in sys.argv:
        print(F"Run Start time = {run_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    main_batting_stats(sys.argv[1:])
    if '-q' not in sys.argv:
        run_time = (dt.now() - run_start_time).total_seconds()
        print(F" Running time = {(run_time // 60)} minutes, {(run_time % 60):2.3} seconds")
    exit()
