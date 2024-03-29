##############################################################################################################################
# coding=utf-8
#
# printPitchingStats.py -- print pitching stats for a player using Retrosheet data
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
__created__ = "2021-01-25"
__updated__ = "2021-10-06"

import sys
sys.path.append("/home/marksa/git/Python/utils")
import copy
from mhsUtils import dt, now_dt, get_filename, get_current_time
from mhsLogging import MhsLogger
from cwTools import *

DEFAULT_PITCH_ID = "kersc001"
DEFAULT_PITCH_YR = 2014
PROGRAM_DESC = "Print pitching stats, totals & averages from Retrosheet data for the specified year(s)."
PROGRAM_NAME = get_filename(__file__)
ID_HELP_DESC = "Retrosheet id for a pitcher, e.g. spahw101, kersc001"
PITCH_STD_SPACE = STD_SPACE_SIZE
PITCH_RND_PRECISION = 2

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
LAST = STR + 1  # end of counting stat headers
# CWBoxPitching: g, gs, cg, sho, gf, outs, ab, r, er, h, b2, b3, hr, hrslam, bb, ibb, so, bf, bk, wp, hb;
#                gdp, sh, sf, xi, pk, w, l, sv, inr, inrs, gb, fb, pitches, strikes
# baseball-ref.com: W L W-L% ERA G GS GF CG SHO SV IP H R ER HR BB IBB SO HBP BK WP BF ERA+ FIP WHIP H9 HR9 BB9 SO9 SO/BB
STATS_DICT = { "G ":0, "GS":0, "GF":0, "CG":0, "SHO":0, "IP":0, "H ":0, "R ":0, "ER":0, "HR":0, "SO":0,
               "BB":0, "IBB":0, "BF":0, "W ":0, "L ":0, "SV":0, "GBO":0, "FBO":0, "WP":0, "HBP":0, "BK":0,
               "TP":0, "TS":0, "ERA":0, "WHIP":0, "H9":0, "HR9":0, "SO9":0, "BB9":0, "SO/BB":0, "WL%":0 }
PITCHING_HDRS = list( STATS_DICT.keys() )


class PrintPitchingStats(PrintStats):
    """Print pitching stats for a player using Retrosheet data."""
    def __init__(self, logger:lg.Logger):
        super().__init__(logger)
        self.stats = copy.copy(STATS_DICT)
        self.totals = copy.copy(STATS_DICT)
        self.std_space = PITCH_STD_SPACE
        self.hdrs = PITCHING_HDRS

    def collect_stats(self, p_box:pointer, pit_id:str, year:str, game_id:str):
        self.lgr.debug(F"search for '{pit_id}' in year = {year}")
        for t in range(2):
            p_pitcher = MyCwlib.box_get_starting_pitcher(p_box, t)
            while p_pitcher:
                pitcher = p_pitcher.contents
                pitcher_id = pitcher.player_id.decode(UTF8_ENCODING)
                self.lgr.debug(F"pitcher = {pitcher_id}")
                if pitcher_id == pit_id:
                    self.lgr.info(F"found pitcher '{pit_id}' in game {game_id}")
                    self.game_ids.append(game_id)
                    pitching = pitcher.pitching.contents
                    self.stats[self.hdrs[GM]]  += pitching.g
                    self.stats[self.hdrs[GS]]  += pitching.gs
                    self.stats[self.hdrs[GF]]  += pitching.gf
                    self.stats[self.hdrs[CG]]  += pitching.cg
                    self.stats[self.hdrs[SHO]] += pitching.sho
                    self.stats[self.hdrs[OUT]] += pitching.outs
                    self.stats[self.hdrs[HIT]] += pitching.h
                    self.stats[self.hdrs[RUN]] += pitching.r
                    self.stats[self.hdrs[ER]]  += pitching.er
                    self.stats[self.hdrs[HR]]  += pitching.hr
                    self.stats[self.hdrs[BB]]  += pitching.bb
                    self.lgr.info(F"pitching.ibb = {pitching.ibb}")
                    self.stats[self.hdrs[IBB]] += pitching.ibb
                    self.stats[self.hdrs[SO]]  += pitching.so
                    self.stats[self.hdrs[BF]]  += pitching.bf
                    self.stats[self.hdrs[WIN]] += pitching.w
                    self.stats[self.hdrs[LOS]] += pitching.l
                    self.stats[self.hdrs[SAV]] += pitching.sv
                    self.stats[self.hdrs[GB]]  += pitching.gb
                    self.stats[self.hdrs[FB]]  += pitching.fb
                    self.stats[self.hdrs[WP]]  += pitching.wp
                    self.stats[self.hdrs[HBP]] += pitching.hb
                    self.stats[self.hdrs[BK]]  += pitching.bk
                    # TODO: add marker to indicate incomplete data?
                    # estimates for missing data
                    strk_min = pitching.so * 3
                    ball_min = pitching.bb * 4
                    self.stats[self.hdrs[PIT]] += max(pitching.pitches, (pitching.bf + strk_min + ball_min + pitching.h))
                    self.stats[self.hdrs[STR]] += max(pitching.strikes, (strk_min + pitching.h))
                p_pitcher = p_pitcher.contents.next

    def check_boxscores(self, pit_id:str, year:str):
        """Check the Retrosheet boxscore files for pitching stats missing from the event files."""
        self.lgr.debug(F"check boxscore files for year = {year}")
        box_year = osp.join(BOXSCORE_FOLDER, year)
        boxscore_files = [box_year + osp.extsep + "EBN", box_year + osp.extsep + "EBA"]
        for bfile in boxscore_files:
            try:
                with open(bfile, newline = '') as box_csvfile:
                    self.lgr.debug(F"search boxscore file {bfile}")
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
                            if brow[0] == "info":
                                if brow[1] == "wp" and brow[2] == pit_id:
                                    self.stats[self.hdrs[WIN]] += 1
                                if brow[1] == "lp" and brow[2] == pit_id:
                                    self.stats[self.hdrs[LOS]] += 1
                                if brow[1] == "save" and brow[2] and brow[2] == pit_id:
                                    self.stats[self.hdrs[SAV]] += 1
                            if brow[1] == "pline" and brow[2] == pit_id:
                                self.lgr.info(F"found pitcher '{pit_id}' in boxscore game {current_id}")
                                # parse boxscore pitching stat line
                                # key: 'stat','pline',id,side,seq,ip*3,no-out,bfp,h,2b,3b,hr,r, er,bb,ibb,k,hbp,wp,balk,sh,sf
                                #       0      1      2  3    4   5    6      7   8 9  10 11 12 13 14 15  16 17 18 19   20 21
                                self.stats[self.hdrs[GM]]  += 1
                                if brow[4] == '1':
                                    self.stats[self.hdrs[GS]] += 1
                                self.stats[self.hdrs[OUT]] += int(brow[5])
                                bfp = 0
                                if int(brow[7]) > 0:
                                    bfp = int(brow[7])
                                    self.stats[self.hdrs[BF]] += bfp
                                hits = 0
                                if int(brow[8]) > 0:
                                    hits = int(brow[8])
                                    self.stats[self.hdrs[HIT]] += hits
                                self.stats[self.hdrs[RUN]] += int(brow[12])
                                self.stats[self.hdrs[ER]]  += int(brow[13])
                                self.stats[self.hdrs[HR]]  += int(brow[11])
                                self.stats[self.hdrs[BB]]  += int(brow[14])
                                ibb = int(brow[15])
                                if ibb > 0:
                                    self.stats[self.hdrs[IBB]] += ibb
                                    self.lgr.info(F"pitching.ibb = {ibb}")
                                self.stats[self.hdrs[SO]]  += int(brow[16])
                                self.stats[self.hdrs[WP]]  += int(brow[18])
                                self.stats[self.hdrs[HBP]] += int(brow[17])
                                self.stats[self.hdrs[BK]]  += int(brow[19])
                                # estimates for missing data
                                strk_min = int(brow[16]) * 3
                                self.stats[self.hdrs[PIT]] += (bfp + strk_min + (int(brow[14]) * 4) + hits)
                                self.stats[self.hdrs[STR]] += (strk_min + hits)
                                find_player = False
            except FileNotFoundError:
                continue

    def print_stat_line(self, year:str):
        self.lgr.info(F"print stat line for year = {year}")
        pitch_stats = self.totals if year == LABEL_TOTAL else self.stats
        diff = 0
        print(year.ljust(self.std_space), end = '')

        # print all the counting stats from the retrosheet data
        for key in self.hdrs:
            if key == self.hdrs[LAST]:
                break
            # adjust from outs to innings pitched
            if key == self.hdrs[OUT]:
                diff = 1 # have to adjust for the extra space required to print IP
                outs = pitch_stats[key]
                print(F"{outs // 3}.{outs % 3}".rjust(self.std_space+diff), end = '')
                diff = -1
            else:
                print(F"{pitch_stats[key]}".rjust(self.std_space+diff) if pitch_stats[key] > 0
                      else '0'.rjust(self.std_space+diff), end = '')
                diff = 0

        # keep track of ACTIVE years
        games = pitch_stats[ self.hdrs[GM] ]
        if year != LABEL_TOTAL and games > 0: self.num_years += 1

        # TODO: add FIP
        # NOTE: add SO%, TS% ?
        # calculate and print the rate stats: ERA, WHIP, H9, HR9, SO9, BB9, SO/BB, WL%
        hits  = pitch_stats[self.hdrs[HIT]]
        walks = pitch_stats[self.hdrs[BB]]
        sos   = pitch_stats[self.hdrs[SO]]
        outs  = pitch_stats[self.hdrs[OUT]]

        era = pitch_stats[self.hdrs[ER]] * 27 / outs if outs > 0 else 0.0
        pera = get_print_strx(era, games, PITCH_RND_PRECISION)
        print(pera.rjust(self.std_space), end = '')

        whip = (walks + hits) / outs * 3 if outs > 0 else 0.0
        pwhip = get_print_strx(whip, games, PITCH_RND_PRECISION + 1, STD_HDR_SIZE + 1)
        print(pwhip.rjust(self.std_space), end = '')

        h9 = hits * 27 / outs if outs > 0 else 0.0
        ph9 = get_print_strx(h9, games, PITCH_RND_PRECISION)
        print(ph9.rjust(self.std_space), end = '')

        hr9 = pitch_stats[self.hdrs[HR]] * 27 / outs if outs > 0 else 0.0
        phr9 = get_print_strx(hr9, games, PITCH_RND_PRECISION)
        print(phr9.rjust(self.std_space), end = '')

        so9 = sos * 27 / outs if outs > 0 else 0.0
        self.lgr.debug(F"so9 = '{so9}'")
        pso9 = get_print_strx(so9, games, PITCH_RND_PRECISION)
        print(pso9.rjust(self.std_space), end = '')

        bb9 = walks * 27 / outs if outs > 0 else 0.0
        pbb9 = get_print_strx(bb9, games, PITCH_RND_PRECISION)
        print(pbb9.rjust(self.std_space), end = '')

        sobb = sos / walks if walks > 0 else 0.0
        psobb = get_print_strx(sobb, games, PITCH_RND_PRECISION)
        print(psobb.rjust(self.std_space), end = '')

        wlp = pitch_stats[self.hdrs[WIN]] / (pitch_stats[self.hdrs[WIN]] + pitch_stats[self.hdrs[LOS]]) * 100.0 \
                if pitch_stats[self.hdrs[WIN]] > 0 else 0.0
        pwlp = get_print_strx(wlp, games, PITCH_RND_PRECISION - 1)
        print(pwlp.rjust(self.std_space))

    def print_ave_line(self):
        diff = 0
        averages = copy.copy(STATS_DICT)
        for key in self.totals.keys():
            # adjust from outs to innings pitched
            if key == PITCHING_HDRS[OUT]:
                outs = round(self.totals[key] / self.num_years)
                averages[key] = (outs // 3) + (outs % 3) / 10
            else:
                averages[key] = round(self.totals[key] / self.num_years)
        print("Ave".ljust(self.std_space), end = '')
        for key in PITCHING_HDRS:
            if key == PITCHING_HDRS[LAST]:
                print(F"\n\nprinted Average of each counting stat for {self.num_years} ACTIVE years")
                break
            if key == PITCHING_HDRS[OUT]:
                diff = -1  # have to adjust for the extra space required to print IP
                print(F"{averages[key]}".rjust(self.std_space + 1), end = '')
            else:
                print(F"{averages[key]}".rjust(self.std_space + diff), end = '')
                diff = 0

# END class PrintPitchingStats


def main_pitching_stats(args:list):
    pers_id, start, end, post, conlevel, filelevel = process_bp_input( args, DEFAULT_PITCH_ID, DEFAULT_PITCH_YR,
                                                                       PROGRAM_DESC, PROGRAM_NAME, ID_HELP_DESC )

    lg_ctrl = MhsLogger( __file__, con_level = conlevel, file_level = filelevel, folder = osp.join("logs", "pitching") )
    lgr = lg_ctrl.get_logger()
    lgr.info(F"Logging: console level = {repr(conlevel)}; file level = {repr(filelevel)}")
    lgr.warning(F" id = {pers_id}; years: {start} -> {end}")

    pitch_stats = PrintPitchingStats(lgr)
    pitch_stats.get_events(post, pers_id, start, end)

    name = F"{pitch_stats.get_giv_name()} {pitch_stats.get_fam_name()}"
    lgr.warning(F"name = {name}")
    season = POST_SEASON if post else REG_SEASON
    lgr.warning(F"found {pitch_stats.get_num_files()} {season} event files over {len(pitch_stats.event_files)} years.")

    pitch_stats.print_stats(pers_id, name, season, start, end)


if __name__ == "__main__":
    if '-q' not in sys.argv:
        print(F"\n\tStart time = {get_current_time()}\n")
    main_pitching_stats(sys.argv[1:])
    if '-q' not in sys.argv:
        run_time = (dt.now() - now_dt).total_seconds()
        print(F"\tRunning time = {(run_time // 60)} minutes, {(run_time % 60):2.3} seconds")
    exit()
