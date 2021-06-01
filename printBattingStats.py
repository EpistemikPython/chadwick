##############################################################################################################################
# coding=utf-8
#
# printBattingStats.py -- print batting stats for a player using Retrosheet data
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
__created__ = "2021-01-21"
__updated__ = "2021-06-01"

import copy
from mhsUtils import dt, run_ts, now_dt
from mhsLogging import MhsLogger
from cwLibWrappers import cwlib
from cwTools import *

DEFAULT_BAT_ID = "maysw101"
DEFAULT_BAT_YR = 1954
PROGRAM_DESC   = "Print batting stats, totals & averages from Retrosheet data for the specified years."
PROGRAM_NAME   = "printBattingStats.py"
ID_HELP_DESC   = "Retrosheet id for a player, e.g. aaroh101, bondb101"
BAT_STD_SPACE  = 6
BAT_RD_PRECISION = 3

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
STATS_DICT = { "G ":0, "PA":0, "AB":0, "R ":0, "H ":0, "2B":0, "3B":0, "HR":0, "XBH":0, "RBI":0,
               "SO":0, "BB":0, "IBB":0, "SB":0, "CS":0, "SH":0, "SF":0, "HBP":0, "GDP":0,
               "TB":0, "BA":0, "OBP":0, "SLG":0, "OPS":0 }
BATTING_HDRS = list( STATS_DICT.keys() )


class PrintBattingStats(PrintStats):
    """print batting stats for a player using Retrosheet data"""
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
        players.insert( 0, MyCwlib.box_get_starter(p_box,0,1) )
        players.insert( 1, MyCwlib.box_get_starter(p_box,1,1) )

        while slots[0] <= 9 or slots[1] <= 9 :
            for t in range(2):
                if slots[t] <= 9:
                    player = players[t].contents.player_id.decode("UTF-8")
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

    def check_boxscores(self, bat_id:str, year:str):
        """check the Retrosheet boxscore files for self.stats missing from the event files"""
        self.lgr.debug(F"check boxscore files for year = {year}")
        boxscore_files = [BOXSCORE_FOLDER + year + ".EBN", BOXSCORE_FOLDER + year + ".EBA"]
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
                                self.lgr.info(F"found duplicate game '{current_id}' in Boxscore file.")
                                find_player = False
                                continue
                            else:
                                self.lgr.info(F"found NEW game '{current_id}' in Boxscore file.")
                                find_player = True
                        elif find_player:
                            if brow[1] == "bline" and brow[2] == bat_id:
                                self.lgr.info(F"found player '{bat_id}' in boxscore game {current_id}")
                                # parse self.stats
                                # Syntax: stat, bline, id,  side, pos, seq, ab, r,   h, 2b,
                                #         3b,   hr,    rbi, sh,   sf,  hbp, bb, ibb, k, sb,
                                #         cs,   gidp,  int
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
        # ba = round(bat_stats[self.hdrs[HIT]] / ab, BAT_RD_PRECISION) if ab > 0 else 0.0
        # pba = str(ba)[1:STD_HDR_SIZE+1] if ba > 0.0 else 'x' if games == 0 else ".000"
        # pba = set_str_size(pba)
        ba = hits / ab if ab > 0 else 0.0
        pba = get_print_str(ba, games, BAT_RD_PRECISION)
        # len_pba = len(pba)
        # if pba != 'x' and len_pba < STD_HDR_SIZE:
        #     addn = "00" if len_pba <= (STD_HDR_SIZE - 2) else '0'
        #     pba += addn
        print( pba.rjust(self.std_space), end = '' )

        obp_num = hits + bat_stats[self.hdrs[BB]] + bat_stats[self.hdrs[HBP]]
        obp_denom = ab + bat_stats[self.hdrs[BB]] + bat_stats[self.hdrs[HBP]] + bat_stats[self.hdrs[SF]]
        obp = obp_num / obp_denom if obp_denom > 0 else 0.0
        self.lgr.debug(F"obp = '{obp}'")
        pobp = get_print_str(obp, games, BAT_RD_PRECISION)
        # robp = round(obp, BAT_RD_PRECISION)
        # pobp = str(robp)[1:STD_HDR_SIZE+1] if robp > 0.0 else 'x' if games == 0 else ".000"
        # pobp = set_str_size(pobp)
        # len_pobp = len(pobp)
        # if pobp != 'x' and len_pobp < STD_HDR_SIZE:
        #     addn = "00" if len_pobp <= (STD_HDR_SIZE - 2) else '0'
        #     pobp += addn
            # if len_pobp == STD_HDR_SIZE - 2: pobp += "00"
            # elif len_pobp == STD_HDR_SIZE - 1: pobp += '0'
        print( pobp.rjust(self.std_space), end = '' )

        slg = tb / ab if ab > 0 else 0.0
        self.lgr.debug(F"slg = '{slg}'")
        pslg = get_print_str(slg, games, BAT_RD_PRECISION)
        # rslg = round(slg, BAT_RD_PRECISION)
        # pslg = str(rslg)[1:STD_HDR_SIZE+1] if rslg > 0.0 else 'x' if games == 0 else ".000"
        # pslg = set_str_size(pslg)
        # len_pslg = len(pslg)
        # if pslg != 'x' and len_pslg < STD_HDR_SIZE:
        #     addn = "00" if len_pslg <= (STD_HDR_SIZE - 2) else '0'
        #     pslg += addn
            # if len_pslg == STD_HDR_SIZE - 2: pslg += "00"
            # elif len_pslg == STD_HDR_SIZE - 1: pslg += '0'
        print( pslg.rjust(self.std_space), end = '' )

        ops = obp + slg
        self.lgr.debug(F"ops = '{ops}'")
        pops = get_print_str(ops, games, BAT_RD_PRECISION, STD_HDR_SIZE + 1)
        # rops = round(ops, BAT_RD_PRECISION)
        # stat_size = STD_HDR_SIZE + 1 if rops > 1.0 else STD_HDR_SIZE
        # pops = str(rops)[:stat_size] if rops > 1.0 else str(rops)[1:stat_size+1] if rops > 0.0 \
        #         else 'x' if games == 0 else ".000"
        # pops = set_str_size(pops, stat_size)
        # len_pops = len(pops)
        # if pops != 'x' and len_pops < stat_size:
        #     addn = "00" if len_pops <= (stat_size - 2) else '0'
        #     pops += addn
            # if len_pops == stat_size - 2: pops += "00"
            # elif len_pops == stat_size - 1: pops += '0'
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

# END class PrintBattingStats


def main_batting_stats(args:list):
    pers_id, start, end, post, loglevel = process_bp_input(args, DEFAULT_BAT_ID, DEFAULT_BAT_YR,
                                                           PROGRAM_DESC, PROGRAM_NAME, ID_HELP_DESC)

    lg_ctrl = MhsLogger(__file__, con_level = loglevel, folder = "logs/batting")
    lgr = lg_ctrl.get_logger()
    lgr.debug(F"loglevel = {repr(loglevel)}")
    lgr.warning(F" id = {pers_id}; years = {start}->{end}")

    bat_stats = PrintBattingStats(lgr)
    bat_stats.get_events(post, pers_id, start, end)

    name = F"{bat_stats.get_giv_name()} {bat_stats.get_fam_name()}"
    lgr.warning(F"name = {name}")
    season = "post-season" if post else "regular season"
    lgr.warning(F"found {bat_stats.get_num_files()} {season} event files over {len(bat_stats.event_files)} years.")

    bat_stats.print_stats(pers_id, name, season, start, end)


if __name__ == "__main__":
    if '-q' not in sys.argv:
        print(F"\n\tStart time = {run_ts}\n")
    main_batting_stats(sys.argv[1:])
    if '-q' not in sys.argv:
        run_time = (dt.now() - now_dt).total_seconds()
        print(F"\tRunning time = {(run_time // 60)} minutes, {(run_time % 60):2.3} seconds")
    exit()
