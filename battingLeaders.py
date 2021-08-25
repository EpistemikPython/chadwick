##############################################################################################################################
# coding=utf-8
#
# battingLeaders.py -- print leaders for a batting stat for a specified time period using Retrosheet data
#
# The data processed by this software was obtained free of charge from and is copyrighted by Retrosheet.
# Interested parties may contact Retrosheet at 20 Sunset Rd., Newark, DE 19711.
#
# Original C code Copyright (c) 2002-2021
# Dr T L Turocy, Chadwick Baseball Bureau (ted.turocy@gmail.com)
#
# Port to Python3, additions & modifications Copyright (c) 2021 Mark Sattolo <epistemik@gmail.com>

__author__       = "Mark Sattolo"
__author_email__ = "epistemik@gmail.com"
__created__ = "2021-08-22"
__updated__ = "2021-08-25"

import sys
sys.path.append("/home/marksa/git/Python/utils")
from mhsUtils import dt, run_ts, now_dt
from mhsLogging import MhsLogger
from cwLibWrappers import cwlib
from cwTools import *

MIN_LIMIT = 10
MAX_LIMIT = 120
DEFAULT_LIMIT = 30
DEFAULT_YEAR  = 1954
PROGRAM_DESC  = "Print leaders for a batting stat from Retrosheet data for the specified year(s)."
PROGRAM_NAME  = "battingLeaders.py"
BAT_STD_SPACE = STD_SPACE_SIZE
BAT_RND_PRECISION = 3

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
TB  = GDP+1   # 19
BA  = TB+1    # 20
LAST = BA+1   # end of available counting stats
# CWBoxBatting: int g, pa, ab, r, h, b2, b3, hr, hrslam, bi, bi2out, gw, bb, ibb, so, gdp, hp, sh, sf, sb, cs, xi;
# baseball-ref.com: G  PA  AB  R  H  2B  3B  HR  RBI  SB  CS  BB  SO  BA  OBP  SLG  OPS  OPS+  TB  GDP  HBP  SH  SF IBB
STATS_DICT = { "G ":0, "PA":0, "AB":0, "R ":0, "H ":0, "2B":0, "3B":0, "HR":0, "XBH":0, "RBI":0, "SO":0, "BB":0, "IBB":0,
               "SB":0, "CS":0, "SH":0, "SF":0, "HBP":0, "GDP":0,"TB":0, "BA":0, "OBP":0, "SLG":0, "OPS":0 }
BATTING_HDRS = list( STATS_DICT.keys() )
DEFAULT_STAT = BATTING_HDRS[RBI]


class PrintBattingLeaders:
    """Print leaders for a batting stat for a specified time period using Retrosheet data."""
    def __init__(self, p_stat:str, p_start:int, p_end:int, p_limit:int, logger:lg.Logger):
        self.lgr = logger
        self.lgr.warning(F"Start {self.__class__.__name__}")
        self.event_files = dict()
        self.game_ids = list()
        self.start = p_start
        self.end = p_end
        self.stat = p_stat
        self.stats = {}
        self.limit = p_limit
        self.num_files = 0

    def get_num_files(self):
        return self.num_files

    def get_events(self, post:bool):
        """Get the required event files for the specified year(s)."""
        season = POST_SEASON if post else REG_SEASON
        self.lgr.info(F"get the {season} events for years {self.start}->{self.end}")
        try:
            for year in range(self.start, self.end+1):
                year_events = list()
                # get the team files
                team_file_name = osp.join(REG_SEASON_FOLDER, "TEAM" + str(year))
                self.lgr.debug(F"team file name = {team_file_name}")
                if not osp.exists(team_file_name):
                    self.lgr.exception(F"CANNOT find team file {team_file_name}!")
                    continue
                if not post:
                    with open(team_file_name, newline = '') as team_csvfile:
                        team_reader = csv.reader(team_csvfile)
                        for trow in team_reader:
                            rteam = trow[0]
                            self.lgr.debug(F"Found team {rteam}")
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

    def get_ldr_stats(self, season:str):
        """Print regular or post-season stats for player 'player_id' in years <yrstart> to <yrend>."""
        self.lgr.debug(F"print {season} {self.stat} leaders for years {self.start} to {self.end}")

        # get all the games in the supplied date range
        for year in range(self.start, self.end + 1):
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
                    self.collect_stats(box, str_year, game_id)

            if year < RETROSHEET_AVAIL_YEAR and season == REG_SEASON:
                self.check_boxscores(str_year)
            
            self.lgr.info(F"found {len(self.game_ids)} {year} games with {self.stat} stats.")

    def collect_stats(self, p_box:pointer, year:str, game_id:str):
        stat = self.stat
        self.lgr.debug(F"search for '{stat}' in year = {year}")
        slots = [1,1]
        players = list()
        players.append( MyCwlib.box_get_starter(p_box,0,1) )
        players.append( MyCwlib.box_get_starter(p_box,1,1) )

        while slots[0] <= 9 or slots[1] <= 9 :
            for t in range(2):
                if slots[t] <= 9:
                    player = players[t].contents.player_id.decode(UTF8_ENCODING)
                    self.game_ids.append(game_id)
                    batting = players[t].contents.batting.contents
                    game_stat = 0
                    if stat == BATTING_HDRS[GM]: game_stat = batting.g
                    elif stat == BATTING_HDRS[PA]: game_stat = batting.pa
                    elif stat == BATTING_HDRS[AB]: game_stat = batting.ab
                    elif stat == BATTING_HDRS[RUN]: game_stat = batting.r
                    elif stat == BATTING_HDRS[HIT]: game_stat = batting.h
                    elif stat == BATTING_HDRS[B2]: game_stat = batting.b2
                    elif stat == BATTING_HDRS[B3]: game_stat = batting.b3
                    elif stat == BATTING_HDRS[HR]: game_stat = batting.hr
                    elif stat == BATTING_HDRS[XBH]: game_stat = (batting.b2 + batting.b3 + batting.hr)
                    elif stat == BATTING_HDRS[RBI] and batting.bi > 0:
                        game_stat = batting.bi
                    elif stat == BATTING_HDRS[BB]: game_stat = batting.bb
                    elif stat == BATTING_HDRS[IBB] and batting.ibb > 0:
                        game_stat = batting.ibb
                    elif stat == BATTING_HDRS[SO]: game_stat = batting.so
                    elif stat == BATTING_HDRS[SB]: game_stat = batting.sb
                    elif stat == BATTING_HDRS[CS]: game_stat = batting.cs
                    elif stat == BATTING_HDRS[SH]: game_stat = batting.sh
                    elif stat == BATTING_HDRS[SF]: game_stat = batting.sf
                    elif stat == BATTING_HDRS[HBP]: game_stat = batting.hp
                    elif stat == BATTING_HDRS[GDP]: game_stat = batting.gdp
                    elif stat == BATTING_HDRS[TB]: game_stat = batting.h + batting.b2 + (2 * batting.b3) + (3 * batting.hr)
                    elif stat == BATTING_HDRS[BA]:
                        game_stat = { BATTING_HDRS[HIT]:batting.h, BATTING_HDRS[AB]:batting.ab, BATTING_HDRS[PA]:batting.pa }
                    if player not in self.stats.keys():
                        self.stats[player] = game_stat
                    else:
                        if stat == BATTING_HDRS[BA]:
                            self.stats[player][BATTING_HDRS[HIT]] += batting.h
                            self.stats[player][BATTING_HDRS[AB]] += batting.ab
                            self.stats[player][BATTING_HDRS[PA]] += batting.pa
                        else:
                            self.stats[player] += game_stat
                    players[t] = players[t].contents.next
                    if not players[t]:
                        while slots[t] <= 9 and not players[t]:
                            slots[t] += 1
                            if slots[t] <= 9:
                                players[t] = cwlib.cw_box_get_starter(p_box, t, slots[t])

    def check_boxscores(self, year:str):
        """Check the Retrosheet boxscore files for batting stats missing from the event files."""
        self.lgr.debug(F"check boxscore files for year = {year}")
        stat = self.stat
        box_year = osp.join(BOXSCORE_FOLDER, year)
        boxscore_files = [box_year + osp.extsep + "EBN", box_year + osp.extsep + "EBA"]
        for bfile in boxscore_files:
            try:
                with open(bfile, newline = '') as box_csvfile:
                    self.lgr.info(F"search boxscore file {bfile}")
                    box_reader = csv.reader(box_csvfile)
                    find_results = False
                    for brow in box_reader:
                        if brow[0] == "id":
                            current_id = brow[1]
                            if current_id in self.game_ids:
                                self.lgr.info(F"found duplicate game '{current_id}' in Boxscore file.")
                                find_results = False
                                continue
                            else:
                                self.lgr.warning(F"found NEW game '{current_id}' in Boxscore file.")
                                # start incorporating the stats found in this boxscore game
                                find_results = True
                        if find_results and brow[1] == "bline":
                            player_id = brow[2]
                            self.lgr.debug(F"found player '{player_id}' in boxscore game {current_id}")
                            if player_id in self.stats.keys():
                                # parse boxscore batting stat line
                                # key: 'stat','bline',id,side,pos,seq,ab,r,h,2b,3b,hr,rbi,sh,sf,hbp,bb,ibb,k, sb,cs,gidp,int
                                #       0      1      2  3    4   5   6  7 8 9  10 11 12  13 14 15  16 17  18 19 20  21  22
                                if stat == BATTING_HDRS[GM]: self.stats[player_id] += 1
                                if stat == BATTING_HDRS[PA]:
                                    game_stat = int(brow[6]) + int(brow[13]) + int(brow[14]) + int(brow[15]) \
                                                + int(brow[16]) + int(brow[22])
                                    self.stats[player_id] += game_stat
                                if stat == BATTING_HDRS[AB]: self.stats[player_id] += int(brow[6])
                                if stat == BATTING_HDRS[RUN]: self.stats[player_id] += int(brow[7])
                                if stat == BATTING_HDRS[HIT]: self.stats[player_id] += int(brow[8])
                                if stat == BATTING_HDRS[B2]: self.stats[player_id] += int(brow[9])
                                if stat == BATTING_HDRS[B3]: self.stats[player_id] += int(brow[10])
                                if stat == BATTING_HDRS[HR] and int(brow[11]) > 0:
                                    self.lgr.warning(F"found {brow[11]} extra HRs for {player_id}!")
                                    self.stats[player_id] += int(brow[11])
                                if stat == BATTING_HDRS[XBH]:
                                    self.stats[player_id] += ( int(brow[9]) + int(brow[10]) + int(brow[11]) )
                                if stat == BATTING_HDRS[RBI] and int(brow[12]) > 0:
                                    self.lgr.warning(F"found {brow[12]} extra RBIs for {player_id}!")
                                    self.stats[player_id] += int(brow[12])
                                if stat == BATTING_HDRS[BB]: self.stats[player_id] += int(brow[16])
                                if stat == BATTING_HDRS[IBB] and int(brow[17]) > 0:
                                    self.stats[player_id] += int(brow[17])
                                if stat == BATTING_HDRS[SO]: self.stats[player_id] += int(brow[18])
                                if stat == BATTING_HDRS[SB]: self.stats[player_id] += int(brow[19])
                                if stat == BATTING_HDRS[CS]: self.stats[player_id] += int(brow[20])
                                if stat == BATTING_HDRS[SH]: self.stats[player_id] += int(brow[13])
                                if stat == BATTING_HDRS[SF]: self.stats[player_id] += int(brow[14])
                                if stat == BATTING_HDRS[HBP]: self.stats[player_id] += int(brow[15])
                                if stat == BATTING_HDRS[GDP]: self.stats[player_id] += int(brow[21])
                                elif stat == BATTING_HDRS[TB]:
                                    self.lgr.warning(F"found extra TBs for {player_id}!")
                                    self.stats[player_id] += ( int(brow[8]) + int(brow[9]) + (2 * int(brow[10]))
                                                               + (3 * int(brow[11])) )
                                elif stat == BATTING_HDRS[BA]:
                                    pa = int(brow[6]) + int(brow[13]) + int(brow[14]) + int(brow[15]) + int(brow[16]) + int(brow[22])
                                    if int(brow[8]) > 0:
                                        self.lgr.warning(F"AB: found {brow[8]} extra hits for {player_id}!")
                                        self.stats[player_id][BATTING_HDRS[HIT]] += int(brow[8])
                                    self.stats[player_id][BATTING_HDRS[AB]] += int(brow[6])
                                    self.stats[player_id][BATTING_HDRS[PA]] += pa
            except FileNotFoundError:
                continue

    def print_ldr_stats(self):
        print(F"\n{self.stat} leaders for {self.start}{':' if self.end == self.start else F' -> {self.end}:'}")

        # calculations for BA
        if self.stat == BATTING_HDRS[BA]:
            for key in self.stats:
                pa = self.stats[key][BATTING_HDRS[PA]]
                # if key == "ashbr101":
                #     print(F"Richie Ashburn: PA = {pa}, AB = {self.stats[key][BATTING_HDRS[AB]]}, hits = {self.stats[key][BATTING_HDRS[HIT]]}")
                if pa < 502:
                    self.stats[key] = 0.0
                else:
                    self.stats[key] = round( (self.stats[key][BATTING_HDRS[HIT]] / self.stats[key][BATTING_HDRS[AB]]), 3 )

        # sort the leaders DESC
        vals_sorted = { k:v for k, v in sorted(self.stats.items(), key = lambda x:x[1], reverse = True) }
        vals = {}
        ct = val = 0
        # get only the specified number of entries, plus ties
        for key in vals_sorted:
            if ct == self.limit:
                if vals_sorted[key] < val:
                    break
                else:
                    ct -= 1
            val = vals_sorted[key]
            vals[key] = val
            ct += 1

        # get the real names from roster
        vals_named = self.get_real_names(vals)
        vals_sorted = { k:v for k, v in sorted(vals_named.items(), key = lambda x:x[1], reverse = True) }

        # print the entries
        for key in vals_sorted:
            if vals_sorted[key] > 1:
                print(F"{key:20}{vals_sorted[key]}")
            else:
                print(F"{key:20}{vals_sorted[key]:0.3f}")
        print()

    def get_real_names(self, vals:dict):
        vwnames = {}
        try:
            for year in range(self.start, self.end+1):
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
                        # search rosters for the players full names
                        roster_file = osp.join(ROSTERS_FOLDER, rteam + str(year) + osp.extsep + "ROS")
                        self.lgr.debug(F"roster file name = {roster_file}")
                        if not osp.exists(roster_file):
                            raise FileNotFoundError(F"CANNOT find roster file {roster_file}!")
                        with open(roster_file, newline = '') as roster_csvfile:
                            ros_reader = csv.reader(roster_csvfile)
                            for rrow in ros_reader:
                                if rrow[0] in vals.keys():
                                    pers_name = F"{rrow[2]} {rrow[1]}"
                                    vwnames[pers_name] = vals[rrow[0]]
        except Exception as ex:
            raise ex
        return vwnames

# END class PrintBattingLeaders


def process_bl_args():
    """Use ArgumentParser to specify command line arguments for batting leaders."""
    arg_parser = ArgumentParser(description = PROGRAM_DESC, prog = PROGRAM_NAME)
    # required arguments
    required = arg_parser.add_argument_group('REQUIRED')
    required.add_argument('-y', '--start_year', required = True, type = int, metavar = "YEAR",
                          help = "start year to find stats (yyyy)")
    required.add_argument('-s', '--stat', required = True, help = F"batting stat to find: {BATTING_HDRS}")
    # optional arguments
    arg_parser.add_argument('-e', '--end_year', type = int, metavar = "YEAR", help = "end year to find stats (yyyy)")
    arg_parser.add_argument('-l', '--limit', type = int, default = DEFAULT_LIMIT,
                            help = F"# of players to print: default = {DEFAULT_LIMIT}, MIN = {MIN_LIMIT}, MAX = {MAX_LIMIT}")
    arg_parser.add_argument('-p', '--post', action = "store_true", help = F"find {POST_SEASON} games instead of {REG_SEASON}")
    arg_parser.add_argument('-q', '--quiet', action = "store_true", help = "NO logging")
    arg_parser.add_argument('-c', '--levcon', metavar = "LEVEL", default = lg.getLevelName(DEFAULT_CONSOLE_LEVEL),
                            help = "set LEVEL of console logging output")
    arg_parser.add_argument('-f', '--levfile', metavar = "LEVEL", default = lg.getLevelName(DEFAULT_FILE_LEVEL),
                            help = "set LEVEL of file logging output")
    return arg_parser


def process_bl_input(argl:list):
    """Process command line input for batting leaders."""
    argp = process_bl_args().parse_args(argl)

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

    if argp.stat in BATTING_HDRS:
        stat = argp.stat
    else:
        print(F">>> IMPROPER stat '{argp.stat}'! Using default value = {DEFAULT_STAT}.\n")
        stat = DEFAULT_STAT

    if MIN_LIMIT <= argp.limit <= MAX_LIMIT:
        limit = argp.limit
    else:
        print(F">>> IMPROPER limit '{argp.limit}'! Using default value = {DEFAULT_LIMIT}.\n")
        limit = DEFAULT_LIMIT

    if RETROSHEET_START_YEAR <= argp.start_year <= RETROSHEET_END_YEAR:
        start = argp.start_year
    else:
        print(F">>> INVALID start year '{argp.start_year}'! Using default year = {DEFAULT_YEAR}.\n")
        start = DEFAULT_YEAR

    if argp.end_year and RETROSHEET_START_YEAR <= argp.end_year <= RETROSHEET_END_YEAR and argp.end_year >= start:
        end = argp.end_year
    else:
        if argp.end_year:
            print(F">>> INVALID end year '{argp.end_year}'! Using end year = {start}.\n")
        end = start

    return stat, start, end, limit, argp.post, con_level, file_level


def main_batting_leaders(args:list):
    stat, start, end, limit, post, conlevel, filelevel = process_bl_input(args)

    lg_ctrl = MhsLogger( __file__, con_level = conlevel, file_level = filelevel, folder = osp.join("logs", "leaders") )
    lgr = lg_ctrl.get_logger()
    lgr.info(F"Logging: console level = {repr(conlevel)}; file level = {repr(filelevel)}")
    lgr.warning(F" stat = {stat}; years: {start} -> {end}; num = {limit}")

    ldr_stats = PrintBattingLeaders(stat, start, end, limit, lgr)
    ldr_stats.get_events(post)

    season = POST_SEASON if post else REG_SEASON
    lgr.warning(F"found {ldr_stats.get_num_files()} {season} event files over {len(ldr_stats.event_files)} years.")

    ldr_stats.get_ldr_stats(season)
    ldr_stats.print_ldr_stats()


if __name__ == "__main__":
    if '-q' not in sys.argv:
        print(F"\n\tStart time = {run_ts}\n")
    main_batting_leaders(sys.argv[1:])
    if '-q' not in sys.argv:
        run_time = (dt.now() - now_dt).total_seconds()
        print(F"\tRunning time = {(run_time // 60)} minutes, {(run_time % 60):2.3} seconds")
    exit()
