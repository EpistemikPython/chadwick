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
__updated__ = "2021-08-22"

import sys
sys.path.append("/home/marksa/git/Python/utils")
import copy
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
LAST = GDP+1  # end of available counting stats
# CWBoxBatting: int g, pa, ab, r, h, b2, b3, hr, hrslam, bi, bi2out, gw, bb, ibb, so, gdp, hp, sh, sf, sb, cs, xi;
# baseball-ref.com: G  PA  AB  R  H  2B  3B  HR  RBI  SB  CS  BB  SO  BA  OBP  SLG  OPS  OPS+  TB  GDP  HBP  SH  SF IBB
STATS_DICT = { "G ":0, "PA":0, "AB":0, "R ":0, "H ":0, "2B":0, "3B":0, "HR":0, "XBH":0, "RBI":0, "SO":0, "BB":0, "IBB":0,
               "SB":0, "CS":0, "SH":0, "SF":0, "HBP":0, "GDP":0,"TB":0, "BA":0, "OBP":0, "SLG":0, "OPS":0 }
BATTING_HDRS = list( STATS_DICT.keys() )
DEFAULT_STAT = BATTING_HDRS[RBI]


class PrintBattingLeaders(PrintStats):
    """Print batting stats for a player using Retrosheet data."""
    def __init__(self, logger:lg.Logger):
        super().__init__(logger)
        self.stats = copy.copy(STATS_DICT)
        self.totals = copy.copy(STATS_DICT)
        self.std_space = BAT_STD_SPACE
        self.hdrs = BATTING_HDRS

    def collect_stats(self, p_box:pointer, bat_id:str, year:str, game_id:str):
        self.lgr.debug(F"search for '{bat_id}' in year = {year}")
        slots = [1,1]
        players = list()
        players.append( MyCwlib.box_get_starter(p_box,0,1) )
        players.append( MyCwlib.box_get_starter(p_box,1,1) )

        while slots[0] <= 9 or slots[1] <= 9 :
            for t in range(2):
                if slots[t] <= 9:
                    player = players[t].contents.player_id.decode(UTF8_ENCODING)
                    if player == bat_id:
                        self.lgr.info(F"found player '{bat_id}' in game {game_id}")
                        self.game_ids.append(game_id)
                        batting = players[t].contents.batting.contents
                        self.stats[ self.hdrs[GM] ]  += batting.g
                        self.stats[ self.hdrs[PA] ]  += batting.pa
                        self.stats[ self.hdrs[AB] ]  += batting.ab
                        self.stats[ self.hdrs[RUN] ] += batting.r
                        self.stats[ self.hdrs[HIT] ] += batting.h
                        self.stats[ self.hdrs[B2] ]  += batting.b2
                        self.stats[ self.hdrs[B3] ]  += batting.b3
                        self.stats[ self.hdrs[HR] ]  += batting.hr
                        self.stats[ self.hdrs[XBH] ] += (batting.b2 + batting.b3 + batting.hr)
                        if batting.bi > 0:
                            self.stats[ self.hdrs[RBI] ] += batting.bi
                        self.stats[ self.hdrs[BB] ]  += batting.bb
                        self.stats[ self.hdrs[IBB] ] += batting.ibb
                        self.stats[ self.hdrs[SO] ]  += batting.so
                        self.stats[ self.hdrs[SB] ]  += batting.sb
                        self.stats[ self.hdrs[CS] ]  += batting.cs
                        self.stats[ self.hdrs[SH] ]  += batting.sh
                        self.stats[ self.hdrs[SF] ]  += batting.sf
                        self.stats[ self.hdrs[HBP] ] += batting.hp
                        self.stats[ self.hdrs[GDP] ] += batting.gdp
                    players[t] = players[t].contents.next
                    if not players[t]:
                        while slots[t] <= 9 and not players[t]:
                            slots[t] += 1
                            if slots[t] <= 9:
                                players[t] = cwlib.cw_box_get_starter(p_box, t, slots[t])

    def print_ldr_stats(self, stat:str, season:str, yrstart:int, yrend:int):
        """Print regular or post-season stats for player 'player_id' in years <yrstart> to <yrend>."""
        self.lgr.debug(F"print {season} stats for years {yrstart} to {yrend}")
        print(F"\n\t{stat} {season} Stats:")
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
                    self.collect_stats(box, stat, str_year, game_id)

            self.lgr.info(F"found {len(self.game_ids)} {year} games with {stat} stats.")

            if year < RETROSHEET_AVAIL_YEAR and season == REG_SEASON:
                self.check_boxscores(stat, str_year)

            self.print_stat_line(str_year)
            self.sum_and_clear()

        if self.num_years > 1:
            self.print_hdr_uls()
            if self.num_years > 5:
                self.print_header()
            self.print_stat_line(LABEL_TOTAL)
            self.print_ave_line()
        print('')

    def check_boxscores(self, bat_id:str, year:str):
        """Check the Retrosheet boxscore files for batting stats missing from the event files."""
        self.lgr.debug(F"check boxscore files for year = {year}")
        box_year = osp.join(BOXSCORE_FOLDER, year)
        boxscore_files = [box_year + osp.extsep + "EBN", box_year + osp.extsep + "EBA"]
        for bfile in boxscore_files:
            try:
                with open(bfile, newline = '') as box_csvfile:
                    self.lgr.info(F"search boxscore file {bfile}")
                    box_reader = csv.reader(box_csvfile)
                    find_player = False
                    for brow in box_reader:
                        if brow[0] == "id":
                            current_id = brow[1]
                            if current_id in self.game_ids:
                                self.lgr.warning(F"found duplicate game '{current_id}' in Boxscore file.")
                                find_player = False
                                continue
                            else:
                                self.lgr.info(F"found NEW game '{current_id}' in Boxscore file.")
                                find_player = True
                        elif find_player:
                            if brow[1] == "bline" and brow[2] == bat_id:
                                self.lgr.info(F"found player '{bat_id}' in boxscore game {current_id}")
                                # parse boxscore batting stat line
                                # key: 'stat','bline',id,side,pos,seq,ab,r,h,2b,3b,hr,rbi,sh,sf,hbp,bb,ibb,k, sb,cs,gidp,int
                                #       0      1      2  3    4   5   6  7 8 9  10 11 12  13 14 15  16 17  18 19 20  21  22
                                self.stats[self.hdrs[GM]]  += 1
                                self.stats[self.hdrs[PA]]  += ( int(brow[6]) + int(brow[13]) + int(brow[14]) + int(brow[15])
                                                                + int(brow[16]) + int(brow[22]) )
                                self.stats[self.hdrs[AB]]  += int(brow[6])
                                self.stats[self.hdrs[RUN]] += int(brow[7])
                                self.stats[self.hdrs[HIT]] += int(brow[8])
                                self.stats[self.hdrs[B2]]  += int(brow[9])
                                self.stats[self.hdrs[B3]]  += int(brow[10])
                                self.stats[self.hdrs[HR]]  += int(brow[11])
                                self.stats[self.hdrs[XBH]] += ( int(brow[9]) + int(brow[10]) + int(brow[11]) )
                                if int(brow[12]) > 0:
                                    self.stats[self.hdrs[RBI]] += int(brow[12])
                                self.stats[self.hdrs[BB]]  += int(brow[16])
                                if int(brow[17]) > 0:
                                    self.stats[self.hdrs[IBB]] += int(brow[17])
                                self.stats[self.hdrs[SO]]  += int(brow[18])
                                self.stats[self.hdrs[SB]]  += int(brow[19])
                                self.stats[self.hdrs[CS]]  += int(brow[20])
                                self.stats[self.hdrs[SH]]  += int(brow[13])
                                self.stats[self.hdrs[SF]]  += int(brow[14])
                                self.stats[self.hdrs[HBP]] += int(brow[15])
                                self.stats[self.hdrs[GDP]] += int(brow[21])
                                find_player = False
            except FileNotFoundError:
                continue

    def print_stat_line(self, year:str):
        self.lgr.info(F"print stat line for year = {year}")
        bat_stats = self.totals if year == LABEL_TOTAL else self.stats
        print(year.ljust(self.std_space), end = '')

        # print all the counting stats from the retrosheet data
        for key in self.hdrs:
            if key == BATTING_HDRS[LAST]:
                break
            print(F"{bat_stats[key]}".rjust(self.std_space) if bat_stats[key] > 0 else '0'.rjust(self.std_space), end = '')
        # add Total Bases
        tb = bat_stats[ self.hdrs[HIT] ] + bat_stats[ self.hdrs[B2] ] \
             + bat_stats[ self.hdrs[B3] ]*2 + bat_stats[ self.hdrs[HR] ]*3
        print(F"{tb}".rjust(self.std_space) if tb > 0 else '0'.rjust(self.std_space), end = '')

        # keep track of ACTIVE years
        games = bat_stats[ self.hdrs[GM] ]
        if year != LABEL_TOTAL and games > 0: self.num_years += 1

        # calculate and print the rate stats
        ab = bat_stats[ self.hdrs[AB] ]
        hits = bat_stats[self.hdrs[HIT]]
        bb_hbp = bat_stats[self.hdrs[BB]] + bat_stats[self.hdrs[HBP]]

        ba = hits / ab if ab > 0 else 0.0
        pba = get_print_strx(ba, games, prec = BAT_RND_PRECISION)
        self.lgr.debug(F"pba = {pba}")
        print( pba.rjust(self.std_space), end = '' )

        obp_num = hits + bb_hbp
        obp_denom = ab + bb_hbp + bat_stats[self.hdrs[SF]]
        obp = obp_num / obp_denom if obp_denom > 0 else 0.0
        self.lgr.debug(F"obp = '{obp}'")
        pobp = get_print_strx(obp, games, prec = BAT_RND_PRECISION)
        print( pobp.rjust(self.std_space), end = '' )

        slg = tb / ab if ab > 0 else 0.0
        self.lgr.debug(F"slg = '{slg}'")
        pslg = get_print_strx(slg, games, prec = BAT_RND_PRECISION)
        print( pslg.rjust(self.std_space), end = '' )

        ops = obp + slg
        self.lgr.debug(F"ops = '{ops}'")
        pops = get_print_strx(ops, games, prec = BAT_RND_PRECISION)
        print( pops.rjust(self.std_space) )

    def print_ave_line(self):
        # NOTE: ave for each 150 games ?
        averages = copy.copy(STATS_DICT)
        for item in self.totals.keys():
            averages[item] = round(self.totals[item] / self.num_years)
        print("Ave".ljust(self.std_space), end = '')
        for key in BATTING_HDRS:
            if key == BATTING_HDRS[LAST]:
                break
            print(str(averages[key]).rjust(self.std_space), end = '')
        # add Total Bases average
        tb = self.totals[BATTING_HDRS[HIT]] + self.totals[BATTING_HDRS[B2]] + self.totals[BATTING_HDRS[B3]] * 2 \
             + self.totals[BATTING_HDRS[HR]] * 3
        tbave = round(tb / self.num_years)
        print(F"{tbave}".rjust(BAT_STD_SPACE))
        print(F"\nprinted Average of each counting stat for {self.num_years} ACTIVE years")

# END class PrintBattingLeaders


def process_bl_args():
    """Use ArgumentParser to specify command line arguments for batting leaders."""
    arg_parser = ArgumentParser(description = PROGRAM_DESC, prog = PROGRAM_NAME)
    # required arguments
    required = arg_parser.add_argument_group('REQUIRED')
    required.add_argument('-y', '--start_year', required = True, type = int, help = "start year to find stats (yyyy)")
    required.add_argument('-s', '--stat', required = True, help = F"batting stat to find: {BATTING_HDRS}")
    # optional arguments
    arg_parser.add_argument('-e', '--end_year', type = int, help = "end year to find stats (yyyy)")
    arg_parser.add_argument('-l', '--limit', type = int,
                            help = F"number of players to print; default = {DEFAULT_LIMIT}, MAX = {MAX_LIMIT}")
    arg_parser.add_argument('-p', '--post', action = "store_true", help = F"find {POST_SEASON} games instead of {REG_SEASON}")
    arg_parser.add_argument('-q', '--quiet', action = "store_true", help = "NO logging")
    arg_parser.add_argument('-c', '--levcon', default = lg.getLevelName(DEFAULT_CONSOLE_LEVEL),
                            help = "set LEVEL of console logging output")
    arg_parser.add_argument('-f', '--levfile', default = lg.getLevelName(DEFAULT_FILE_LEVEL),
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

    if RETROSHEET_START_YEAR <= argp.start <= RETROSHEET_END_YEAR:
        start = argp.start
    else:
        print(F">>> INVALID start year '{argp.start}'! Using default year = {DEFAULT_YEAR}.\n")
        start = DEFAULT_YEAR

    if argp.end and RETROSHEET_START_YEAR <= argp.end <= RETROSHEET_END_YEAR and argp.end >= start:
        end = argp.end
    else:
        if argp.end:
            print(F">>> INVALID end year '{argp.end}'! Using end year = {start}.\n")
        end = start

    return stat, start, end, limit, argp.post, con_level, file_level


def main_batting_leaders(args:list):
    stat, start, end, limit, post, conlevel, filelevel = process_bl_input(args)

    lg_ctrl = MhsLogger( __file__, con_level = conlevel, file_level = filelevel, folder = osp.join("logs", "leaders") )
    lgr = lg_ctrl.get_logger()
    lgr.info(F"Logging: console level = {repr(conlevel)}; file level = {repr(filelevel)}")
    lgr.warning(F" stat = {stat}; years: {start} -> {end}")

    ldr_stats = PrintBattingLeaders(lgr)
    ldr_stats.get_events(post, 'x', start, end)

    season = POST_SEASON if post else REG_SEASON
    lgr.warning(F"found {ldr_stats.get_num_files()} {season} event files over {len(ldr_stats.event_files)} years.")

    ldr_stats.print_ldr_stats(stat, season, start, end)


if __name__ == "__main__":
    if '-q' not in sys.argv:
        print(F"\n\tStart time = {run_ts}\n")
    main_batting_leaders(sys.argv[1:])
    if '-q' not in sys.argv:
        run_time = (dt.now() - now_dt).total_seconds()
        print(F"\tRunning time = {(run_time // 60)} minutes, {(run_time % 60):2.3} seconds")
    exit()
