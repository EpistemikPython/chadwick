##############################################################################################################################
# coding=utf-8
#
# printPitchingStats.py -- print pitching stats for a player using Retrosheet data
#
# Original C code Copyright (c) 2002-2020
# Dr T L Turocy, Chadwick Baseball Bureau (ted.turocy@gmail.com)
#
# Port to Python3, additions & modifications Copyright (c) 2019-2021 Mark Sattolo <epistemik@gmail.com>

__author__       = "Mark Sattolo"
__author_email__ = "epistemik@gmail.com"
__created__ = "2021-01-25"
__updated__ = "2021-01-26"

import copy
import csv
import sys
from argparse import ArgumentParser
from datetime import datetime as dt
from cwLibWrappers import chadwick
from cwTools import *

STD_PITCH_SPACE = 6
TOTAL = "Total"

GM  = 0         # 0
GS  = GM + 1    # 1
GF  = GS + 1    # 2
CG  = GF + 1    # 3
SHO = CG + 1    # 4
OUT = SHO + 1   # 5
HIT = OUT + 1   # 6
RUN = HIT + 1   # 7
ER  = RUN + 1   # 8
HR  = ER + 1    # 9
SO  = HR + 1    # 10
BB  = SO + 1    # 11
IBB = BB + 1    # 12
BF  = IBB + 1   # 13
WIN = BF + 1    # 14
LOS = WIN + 1   # 15
SAV = LOS + 1   # 16
GB  = SAV + 1   # 17
FB  = GB + 1    # 18
WP  = FB + 1    # 19
HBP = WP + 1    # 20
BK  = HBP + 1   # 21
PIT = BK + 1    # 22
STR = PIT + 1   # 23
# CWBoxPitching: g, gs, cg, sho, gf, outs, ab, r, er, h, b2, b3, hr, hrslam, bb, ibb, so, bf, bk, wp, hb;
#                gdp, sh, sf, xi, pk, w, l, sv, inr, inrs, gb, fb, pitches, strikes
# baseball-ref.com: W L W-L% ERA G GS GF CG SHO SV IP H R ER HR BB IBB SO HBP BK WP BF ERA+ FIP WHIP H9 HR9 BB9 SO9 SO/BB
# G GS GF CG SHO outs/IP H R ER HR SO BB IBB BF W L SV GB FB WP HBP BK pit/TP str/TS
STATS_DICT = { "01G":0, "02GS":0, "03GF":0, "04CG":0, "05SHO":0, "06IP":0, "07H":0, "08R":0, "09ER":0, "10HR":0,
               "11SO":0, "12BB":0, "13IBB":0, "14BF":0, "15W":0, "16L":0, "17SV":0, "18GBO":0, "19FBO":0, "20WP":0,
               "21HBP":0, "22BK":0, "23TP":0, "24TS":0 }
PITCHING_KEYS = list(STATS_DICT.keys())
PITCHING_HDRS = { PITCHING_KEYS[GM][:2] :F"{PITCHING_KEYS[GM][2:]} ",
                  PITCHING_KEYS[GS][:2] :F"{PITCHING_KEYS[GS][2:]}",
                  PITCHING_KEYS[GF][:2] :F"{PITCHING_KEYS[GF][2:]}",
                  PITCHING_KEYS[CG][:2] :F"{PITCHING_KEYS[CG][2:]}",
                  PITCHING_KEYS[SHO][:2]:F"{PITCHING_KEYS[SHO][2:]}",
                  PITCHING_KEYS[OUT][:2]:F"{PITCHING_KEYS[OUT][2:]}",
                  PITCHING_KEYS[HIT][:2]:F"{PITCHING_KEYS[HIT][2:]} ",
                  PITCHING_KEYS[RUN][:2]:F"{PITCHING_KEYS[RUN][2:]} ",
                  PITCHING_KEYS[ER][:2] :F"{PITCHING_KEYS[ER][2:]}",
                  PITCHING_KEYS[HR][:2] :F"{PITCHING_KEYS[HR][2:]}",
                  PITCHING_KEYS[SO][:2] :F"{PITCHING_KEYS[SO][2:]}",
                  PITCHING_KEYS[BB][:2] :F"{PITCHING_KEYS[BB][2:]}",
                  PITCHING_KEYS[IBB][:2]:F"{PITCHING_KEYS[IBB][2:]}",
                  PITCHING_KEYS[BF][:2] :F"{PITCHING_KEYS[BF][2:]}",
                  PITCHING_KEYS[WIN][:2]:F"{PITCHING_KEYS[WIN][2:]} ",
                  PITCHING_KEYS[LOS][:2]:F"{PITCHING_KEYS[LOS][2:]} ",
                  PITCHING_KEYS[SAV][:2]:F"{PITCHING_KEYS[SAV][2:]}",
                  PITCHING_KEYS[GB][:2] :F"{PITCHING_KEYS[GB][2:]}",
                  PITCHING_KEYS[FB][:2] :F"{PITCHING_KEYS[FB][2:]}",
                  PITCHING_KEYS[WP][:2] :F"{PITCHING_KEYS[WP][2:]}",
                  PITCHING_KEYS[HBP][:2]:F"{PITCHING_KEYS[HBP][2:]}",
                  PITCHING_KEYS[BK][:2] :F"{PITCHING_KEYS[BK][2:]}",
                  PITCHING_KEYS[PIT][:2]:F"{PITCHING_KEYS[PIT][2:]}",
                  PITCHING_KEYS[STR][:2]:F"{PITCHING_KEYS[STR][2:]}",
                  F"{str(STR + 2)}":"ERA", F"{str(STR + 3)}":"WHIP", F"{str(STR + 4)}":"H9", F"{str(STR + 5)}":"HR9",
                  F"{str(STR + 6)}":"SO9", F"{str(STR + 7)}":"BB9" , F"{str(STR + 8)}":"SO/BB", F"{str(STR + 9)}":"WL%"}

def clear(stats:dict, totals:dict):
    for item in stats.keys():
        totals[item] += stats[item]
        stats[item] = 0

def print_ul():
    print(F"{''}".rjust(STD_PITCH_SPACE), end = '')
    for sp in range( len(PITCHING_HDRS) ):
        print(F"{'---'}".rjust(STD_PITCH_SPACE), end = '')
    print(" ")

def print_hdr():
    # print(F"{'':18}   IP  H  R ER BB SO  TP TS GB FB")
    print(F"{''}".rjust(STD_PITCH_SPACE), end = '')
    for key in sorted(PITCHING_HDRS):
        print(F"{PITCHING_HDRS[key]}".rjust(STD_PITCH_SPACE), end = '')
    print(" ")
    print_ul()


class PrintPitchingStats:
    """print pitching stats for a player using Retrosheet data"""
    def __init__(self, logger:logging.Logger):
        self.lgr = logger
        self.lgr.warning(F" Start {self.__class__.__name__}")
        self.event_files = {}

    def collect_stats(self, p_box:pointer, pit_id:str, stats:dict, year:str):
        self.lgr.debug(F"player = {pit_id}; collect stats for year = {year}")
        pk = PITCHING_KEYS
        for t in range(2):
            p_pitcher = MyCwlib.box_get_starting_pitcher(p_box, t)
            while p_pitcher:
                pitcher = p_pitcher.contents
                pitcher_id = pitcher.player_id.decode("UTF8")
                self.lgr.debug(F"pitcher = {pitcher_id}")
                if pitcher_id == pit_id:
                    self.lgr.debug(F"found pitcher = {pit_id}")
                    pitching = pitcher.pitching.contents
                    stats[pk[GM]]  += pitching.g
                    stats[pk[GS]]  += pitching.gs
                    stats[pk[GF]]  += pitching.gf
                    stats[pk[CG]]  += pitching.cg
                    stats[pk[SHO]] += pitching.sho
                    stats[pk[OUT]] += pitching.outs
                    stats[pk[HIT]] += pitching.h
                    stats[pk[RUN]] += pitching.r
                    stats[pk[ER]]  += pitching.er
                    stats[pk[HR]]  += pitching.hr
                    stats[pk[BB]]  += pitching.bb
                    stats[pk[IBB]] += pitching.ibb
                    stats[pk[SO]]  += pitching.so
                    stats[pk[BF]]  += pitching.bf
                    stats[pk[WIN]] += pitching.w
                    stats[pk[LOS]] += pitching.l
                    stats[pk[SAV]] += pitching.sv
                    stats[pk[GB]]  += pitching.gb
                    stats[pk[FB]]  += pitching.fb
                    stats[pk[WP]]  += pitching.wp
                    stats[pk[HBP]] += pitching.hb
                    stats[pk[BK]]  += pitching.bk
                    stats[pk[PIT]] += pitching.pitches
                    stats[pk[STR]] += pitching.strikes
                p_pitcher = p_pitcher.contents.next

    def print_stats(self, persid:str, name:str, yrstart:int, yrend:int):
        self.lgr.info(F"print stats for years {yrstart}->{yrend}")
        stats = copy.copy(STATS_DICT)
        totals = copy.copy(STATS_DICT)

        print(F"\t{name} Stats:")
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
                    self.collect_stats(box, persid, stats, str(year))

            self.print_stat_line(str(year), stats)
            clear(stats, totals)

        print_ul()
        print_hdr()
        self.print_stat_line(TOTAL, totals)
        self.print_ave_line(totals, yrend-yrstart+1)
        print("")

    def print_ave_line(self, totals:dict, period:int):
        self.lgr.info(F"print average of each counting stat over span of {period} years")
        diff = 0
        averages = copy.copy(STATS_DICT)
        for key in totals.keys():
            # adjust from outs to innings pitched
            if key == PITCHING_KEYS[OUT]:
                outs = round(totals[key] / period)
                averages[key] = (outs // 3) + (outs % 3)/10
            else:
                averages[key] = round(totals[key] / period)
        print("Ave".ljust(STD_PITCH_SPACE), end = '')
        for key in sorted( averages.keys() ):
            if key == PITCHING_KEYS[OUT]:
                diff = -1 # have to adjust for the extra space required to print IP
                print(F"{averages[key]}".rjust(STD_PITCH_SPACE+1), end = '')
            else:
                print(F"{averages[key]}".rjust(STD_PITCH_SPACE+diff), end = '')
                diff = 0
        print(" ")

    def print_stat_line(self, year:str, pitch:dict):
        self.lgr.info(F"print stat line for year = {year}")
        pk = PITCHING_KEYS
        diff = 0
        print(F"{year.ljust(STD_PITCH_SPACE)}", end = '')
        # print all the counting stats from the retrosheet data
        for key in sorted( pitch.keys() ):
            # adjust from outs to innings pitched
            if key == PITCHING_KEYS[OUT]:
                diff = 1 # have to adjust for the extra space required to print IP
                outs = pitch[key]
                print(F"{outs // 3}.{outs % 3}".rjust(STD_PITCH_SPACE+diff), end = '')
                diff = -1
            else:
                print(F"{pitch[key]}".rjust(STD_PITCH_SPACE+diff) if pitch[key] >= 0 else F"{''}".rjust(STD_PITCH_SPACE+diff),
                      end = '')
                diff = 0
        # calculate and print the rate stats: ERA, WHIP, H9, HR9, SO9, BB9, SO/BB, WL%
        era = round( (pitch[pk[ER]] * 27 / pitch[pk[OUT]]), 2 ) if pitch[pk[OUT]] > 0 else 0
        print(F"{era}".rjust(STD_PITCH_SPACE), end = '')
        whip = (pitch[pk[BB]] + pitch[pk[HIT]]) / pitch[pk[OUT]] * 3 if pitch[pk[OUT]] > 0 else 0
        pwhip = round(whip,3)
        print(F"{pwhip}".rjust(STD_PITCH_SPACE), end = '')
        h9 = round( (pitch[pk[HIT]] * 27 / pitch[pk[OUT]]), 2 ) if pitch[pk[OUT]] > 0 else 0
        print(F"{h9}".rjust(STD_PITCH_SPACE), end = '')
        hr9 = round( (pitch[pk[HR]] * 27 / pitch[pk[OUT]]), 2 ) if pitch[pk[OUT]] > 0 else 0
        print(F"{hr9}".rjust(STD_PITCH_SPACE), end = '')
        so9 = round( (pitch[pk[SO]] * 27 / pitch[pk[OUT]]), 2 ) if pitch[pk[OUT]] > 0 else 0
        print(F"{so9}".rjust(STD_PITCH_SPACE), end = '')
        bb9 = round( (pitch[pk[BB]] * 27 / pitch[pk[OUT]]), 2 ) if pitch[pk[OUT]] > 0 else 0
        print(F"{bb9}".rjust(STD_PITCH_SPACE), end = '')
        sobb = round( (pitch[pk[SO]] / pitch[pk[BB]]), 2 ) if pitch[pk[BB]] > 0 else 0
        print(F"{sobb}".rjust(STD_PITCH_SPACE), end = '')
        wlp = round( (pitch[pk[WIN]] / (pitch[pk[WIN]] + pitch[pk[LOS]])), 3 ) * 100 if pitch[pk[WIN]] > 0 else 0
        print(F"{wlp}"[:4].rjust(STD_PITCH_SPACE), end = '')
        print(" ")

# END class PrintPitchingStats


def process_args():
    arg_parser = ArgumentParser(
        description="Print pitching stats, totals & averages from Retrosheet data for the specified years",
        prog='main_pitching_stats.py' )
    # required arguments
    required = arg_parser.add_argument_group('REQUIRED')
    required.add_argument('-i', '--pitcher_id', required=True, help="Retrosheet id for a pitcher, e.g. spahw101, kersc001")
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

    # TODO: process 'postseason' flag

    pitcher_id = args.pitcher_id.strip() if len(args.pitcher_id) >= 8 and \
                 args.pitcher_id[:5].isalpha() and args.pitcher_id[5:8].isdecimal() else "kersc001"
    if len(pitcher_id) > 8:
        pitcher_id = pitcher_id[:8]
    logging.warning(F"id = {pitcher_id}")

    start = args.start if 1871 <= args.start <= 2020 else 2014
    logging.warning(F"start = {start}")

    end = args.end if args.end and 1871 <= args.end <= 2020 else start
    if end < start: end = start
    logging.warning(F"end = {end}")

    return pitcher_id, start, end, loglevel


def main_pitching_stats(args:list):
    lgr = logging.getLogger("PrintPitchingStats")

    pers_id, start, end, loglevel = process_input_parameters(args)

    lgr.setLevel(loglevel)
    lgr.debug( str(lgr.handlers) )
    lgr.warning(F" id = {pers_id}; years = {start}->{end}")

    pitch_stats = PrintPitchingStats(lgr)
    need_name = True
    fam_name = pers_id
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
                                if pers_id == rrow[0]:
                                    fam_name = rrow[1]
                                    giv_name = rrow[2]
                                    need_name = False
                                    break
                    # find and store the event file paths for the requested years
                    event_file = REGULAR_SEASON_FOLDER + str(year) + rteam + ".EV" + trow[1]
                    if not os.path.exists(event_file):
                        raise FileNotFoundError(F"CANNOT find event file {event_file}!")
                    year_events.append(event_file)
            pitch_stats.event_files[str(year)] = year_events

        name = F"{giv_name} {fam_name}"
        lgr.warning(F"name = {name}")
        lgr.warning(F"found {len(pitch_stats.event_files)} year-event files")
        for item in pitch_stats.event_files:
            lgr.debug(item)

        pitch_stats.print_stats(pers_id, name, start, end)

    except Exception as ex:
        lgr.exception(F"Exception: {repr(ex)}")


if __name__ == "__main__":
    run_start_time = dt.now()
    if '-q' not in sys.argv:
        logging.critical(F"Run Start time = {run_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    main_pitching_stats(sys.argv[1:])
    if '-q' not in sys.argv:
        run_time = (dt.now() - run_start_time).total_seconds()
        logging.critical(F" Running time = {(run_time // 60)} minutes, {(run_time % 60):2.3} seconds")
    exit()
