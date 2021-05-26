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
# Port to Python3, additions & modifications Copyright (c) 2019-2021 Mark Sattolo <epistemik@gmail.com>

__author__       = "Mark Sattolo"
__author_email__ = "epistemik@gmail.com"
__created__ = "2021-01-25"
__updated__ = "2021-05-26"

import copy
from cwTools import *

STD_PITCH_SPACE = 6

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
    """print pitching stats for a player using Retrosheet data"""
    def __init__(self, logger:lg.Logger):
        super().__init__(logger)
        self.stats = copy.copy(STATS_DICT)
        self.totals = copy.copy(STATS_DICT)
        self.std_space = STD_PITCH_SPACE
        self.hdrs = PITCHING_HDRS

    # def print_stats(self, pit_id:str, name:str, season:str, yrstart:int, yrend:int):
    #     self.lgr.info(F"print {season} stats for years {yrstart}->{yrend}")
    #     stats = copy.copy(STATS_DICT)
    #     totals = copy.copy(STATS_DICT)
    #
    #     print(F"\t{name.upper()} {season} Stats:")
    #     print_header(STD_PITCH_SPACE, PITCHING_HDRS)
    #
    #     # get all the games in the supplied date range
    #     for year in range(yrstart, yrend+1):
    #         str_year = str(year)
    #         self.lgr.info(F"collect stats for year: {str_year}")
    #         self.game_ids.clear()
    #         if str_year not in self.event_files.keys():
    #             continue
    #         for efile in self.event_files[str_year]:
    #             self.lgr.debug(F"found events for team/year = {get_base_filename(efile)}")
    #             cwgames = chadwick.games(efile)
    #             for game in cwgames:
    #                 game_id = game.contents.game_id.decode(encoding = 'UTF-8')
    #                 game_date = game_id[3:11]
    #                 self.lgr.debug(F"Found game id = {game_id}; date = {game_date}")
    #
    #                 box = MyCwlib.box_create(game)
    #                 self.collect_stats(box, pit_id, stats, str_year, game_id)
    #
    #         self.lgr.info(F"found {len(self.game_ids)} games with {pit_id} stats.")
    #
    #         if year < 1974:
    #             self.check_boxscores(pit_id, str_year, stats)
    #
    #         self.print_stat_line(str_year, stats)
    #         sum_and_clear(stats, totals)
    #
    #     if yrstart != yrend:
    #         print_hdr_uls(STD_PITCH_SPACE, PITCHING_HDRS)
    #         print_header(STD_PITCH_SPACE, PITCHING_HDRS)
    #         self.print_stat_line(TOTAL, totals)
    #         self.print_ave_line(totals)
    #     print("")

    def collect_stats(self, p_box:pointer, pit_id:str, stats:dict, year:str, game_id:str):
        self.lgr.debug(F"player = {pit_id} for year = {year}")
        for t in range(2):
            p_pitcher = MyCwlib.box_get_starting_pitcher(p_box, t)
            while p_pitcher:
                pitcher = p_pitcher.contents
                pitcher_id = pitcher.player_id.decode("UTF8")
                self.lgr.debug(F"pitcher = {pitcher_id}")
                if pitcher_id == pit_id:
                    self.lgr.info(F"found pitcher = {pit_id} in game = {game_id}")
                    self.game_ids.append(game_id)
                    pitching = pitcher.pitching.contents
                    stats[self.hdrs[GM]]  += pitching.g
                    stats[self.hdrs[GS]]  += pitching.gs
                    stats[self.hdrs[GF]]  += pitching.gf
                    stats[self.hdrs[CG]]  += pitching.cg
                    stats[self.hdrs[SHO]] += pitching.sho
                    stats[self.hdrs[OUT]] += pitching.outs
                    stats[self.hdrs[HIT]] += pitching.h
                    stats[self.hdrs[RUN]] += pitching.r
                    stats[self.hdrs[ER]]  += pitching.er
                    stats[self.hdrs[HR]]  += pitching.hr
                    stats[self.hdrs[BB]]  += pitching.bb
                    stats[self.hdrs[IBB]] += pitching.ibb
                    stats[self.hdrs[SO]]  += pitching.so
                    stats[self.hdrs[BF]]  += pitching.bf
                    stats[self.hdrs[WIN]] += pitching.w
                    stats[self.hdrs[LOS]] += pitching.l
                    stats[self.hdrs[SAV]] += pitching.sv
                    stats[self.hdrs[GB]]  += pitching.gb
                    stats[self.hdrs[FB]]  += pitching.fb
                    stats[self.hdrs[WP]]  += pitching.wp
                    stats[self.hdrs[HBP]] += pitching.hb
                    stats[self.hdrs[BK]]  += pitching.bk
                    stats[self.hdrs[PIT]] += pitching.pitches
                    stats[self.hdrs[STR]] += pitching.strikes
                p_pitcher = p_pitcher.contents.next

    def check_boxscores(self, pit_id:str, year:str, stats:dict):
        """check the Retrosheet boxscore files for stats missing from the event files"""
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
                                self.lgr.info(F"found duplicate game = {current_id} in Boxscore file.")
                                find_player = False
                                continue
                            else:
                                find_player = True
                        elif find_player:
                            if brow[0] == "info":
                                if brow[1] == "wp" and brow[2] == pit_id:
                                    stats[self.hdrs[WIN]] += 1
                                if brow[1] == "lp" and brow[2] == pit_id:
                                    stats[self.hdrs[LOS]] += 1
                                if brow[1] == "save" and brow[2] and brow[2] == pit_id:
                                    stats[self.hdrs[SAV]] += 1
                            if brow[1] == "pline" and brow[2] == pit_id:
                                self.lgr.info(F"found player {pit_id} in game {current_id}")
                                # parse stats
                                # order: stat, pline, id, side, seq, ip*3, no-out, bfp, h, 2b, 3b, hr, r, er, bb, ibb, k, hbp,
                                #        wp, balk, sh, sf
                                stats[self.hdrs[GM]]  += 1
                                if brow[4] == '1':
                                    stats[self.hdrs[GS]] += 1
                                stats[self.hdrs[OUT]] += int(brow[5])
                                stats[self.hdrs[HIT]] += int(brow[8])
                                stats[self.hdrs[RUN]] += int(brow[12])
                                stats[self.hdrs[ER]]  += int(brow[13])
                                stats[self.hdrs[HR]]  += int(brow[11])
                                stats[self.hdrs[BB]]  += int(brow[14])
                                stats[self.hdrs[IBB]] += int(brow[15])
                                stats[self.hdrs[SO]]  += int(brow[16])
                                stats[self.hdrs[BF]]  += ( int(brow[5]) + int(brow[6]) ) # approximation
                                stats[self.hdrs[WP]]  += int(brow[18])
                                stats[self.hdrs[HBP]] += int(brow[17])
                                stats[self.hdrs[BK]]  += int(brow[19])
                                stats[self.hdrs[PIT]] += int(brow[7])
                                stats[self.hdrs[STR]] += int(brow[16])*3 # approximation
                                find_player = False
            except FileNotFoundError:
                continue

    def print_stat_line(self, year:str, pitch:dict):
        self.lgr.info(F"print stat line for year = {year}")
        diff = 0
        print(year.ljust(self.std_space), end = '')

        # print all the counting stats from the retrosheet data
        for key in self.hdrs:
            if key == self.hdrs[LAST]:
                break
            # adjust from outs to innings pitched
            if key == self.hdrs[OUT]:
                diff = 1 # have to adjust for the extra space required to print IP
                outs = pitch[key]
                print(F"{outs // 3}.{outs % 3}".rjust(self.std_space+diff), end = '')
                diff = -1
            else:
                print(F"{pitch[key]}".rjust(self.std_space+diff) if pitch[key] >= 0 else F"{''}".rjust(self.std_space+diff),
                      end = '')
                diff = 0

        # calculate and print the rate stats: ERA, WHIP, H9, HR9, SO9, BB9, SO/BB, WL%
        games = pitch[ self.hdrs[GM] ]
        # keep track of ACTIVE years
        if year != TOTAL and games > 0: self.num_years += 1

        # NOTE: add TS% ?
        era = round( (pitch[self.hdrs[ER]] * 27 / pitch[self.hdrs[OUT]]), 2 ) if pitch[self.hdrs[OUT]] > 0 else 0
        print(F"{era}".rjust(self.std_space), end = '')
        whip = (pitch[self.hdrs[BB]] + pitch[self.hdrs[HIT]]) / pitch[self.hdrs[OUT]] * 3 if pitch[self.hdrs[OUT]] > 0 else 0
        pwhip = round(whip,3)
        print(F"{pwhip}".rjust(self.std_space), end = '')
        h9 = round( (pitch[self.hdrs[HIT]] * 27 / pitch[self.hdrs[OUT]]), 2 ) if pitch[self.hdrs[OUT]] > 0 else 0
        print(F"{h9}".rjust(self.std_space), end = '')
        hr9 = round( (pitch[self.hdrs[HR]] * 27 / pitch[self.hdrs[OUT]]), 2 ) if pitch[self.hdrs[OUT]] > 0 else 0
        print(F"{hr9}".rjust(self.std_space), end = '')
        so9 = round( (pitch[self.hdrs[SO]] * 27 / pitch[self.hdrs[OUT]]), 2 ) if pitch[self.hdrs[OUT]] > 0 else 0
        print(F"{so9}".rjust(self.std_space), end = '')
        bb9 = round( (pitch[self.hdrs[BB]] * 27 / pitch[self.hdrs[OUT]]), 2 ) if pitch[self.hdrs[OUT]] > 0 else 0
        print(F"{bb9}".rjust(self.std_space), end = '')
        sobb = round( (pitch[self.hdrs[SO]] / pitch[self.hdrs[BB]]), 2 ) if pitch[self.hdrs[BB]] > 0 else 0
        print(F"{sobb}".rjust(self.std_space), end = '')
        wlp = round( (pitch[self.hdrs[WIN]] / (pitch[self.hdrs[WIN]] + pitch[self.hdrs[LOS]])), 3 ) * 100 if pitch[self.hdrs[WIN]] > 0 else 0
        print(F"{wlp}"[:STD_HDR_SIZE].rjust(self.std_space))

    def print_ave_line(self, totals: dict):
        diff = 0
        averages = copy.copy(STATS_DICT)
        for key in totals.keys():
            # adjust from outs to innings pitched
            if key == PITCHING_HDRS[OUT]:
                outs = round(totals[key] / self.num_years)
                averages[key] = (outs // 3) + (outs % 3) / 10
            else:
                averages[key] = round(totals[key] / self.num_years)
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


# def process_args():
#     arg_parser = ArgumentParser(
#         description="Print pitching stats, totals & averages from Retrosheet data for the specified years",
#         prog='main_pitching_stats.py' )
#     # required arguments
#     required = arg_parser.add_argument_group('REQUIRED')
#     required.add_argument('-i', '--pitcher_id', required=True, help="Retrosheet id for a pitcher, e.g. spahw101, kersc001")
#     required.add_argument('-s', '--start', required=True, type=int, help="start year to find stats (yyyy)")
#     # optional arguments
#     arg_parser.add_argument('-e', '--end', type=int, help="end year to find stats (yyyy)")
#     arg_parser.add_argument('-p', '--post', action="store_true", help="find postseason games instead of regular season")
#     arg_parser.add_argument('-q', '--quiet', action="store_true", help="NO logging")
#     arg_parser.add_argument('-l', '--level', default=lg.getLevelName(DEFAULT_CONSOLE_LEVEL), help="set LEVEL of logging output")
#
#     return arg_parser
#
#
# def process_input_parameters(argl:list):
#     argp = process_args().parse_args(argl)
#     loglevel = lg.getLevelName(QUIET_LOG_LEVEL) if argp.quiet else argp.level.strip().upper()
#     try:
#         getattr( lg, loglevel )
#     except AttributeError as ae:
#         print(F"Problem with log level: {repr(ae)}")
#         loglevel = DEFAULT_CONSOLE_LEVEL
#
#     pitch_id = argp.pitcher_id.strip() if len(argp.pitcher_id) >= 8 and \
#                argp.pitcher_id[:5].isalpha() and argp.pitcher_id[5:8].isdecimal() else "kersc001"
#     if len(pitch_id) > 8:
#         pitch_id = pitch_id[:8]
#
#     start = argp.start if 1871 <= argp.start <= 2020 else 2014
#
#     end = argp.end if argp.end and 1871 <= argp.end <= 2020 else start
#     if end < start: end = start
#
#     return pitch_id, start, end, argp.post, loglevel


DEFAULT_PITCH_ID = "kersc001"
DEFAULT_PITCH_YR = 2014
PROGRAM_DESC = "Print pitching stats, totals & averages from Retrosheet data for the specified years."
PROGRAM_NAME = "printPitchingStats.py"
ID_HELP_DESC = "Retrosheet id for a pitcher, e.g. spahw101, kersc001"

def main_pitching_stats(args:list):
    pers_id, start, end, post, loglevel = process_bp_input(args, DEFAULT_PITCH_ID, DEFAULT_PITCH_YR,
                                                           PROGRAM_DESC, PROGRAM_NAME, ID_HELP_DESC)

    # lgr = get_simple_logger(__file__, level = loglevel)
    lg_ctrl = MhsLogger(__file__, con_level = loglevel, folder = "logs/pitching")
    lgr = lg_ctrl.get_logger()
    lgr.debug(F"loglevel = {repr(loglevel)}")
    lgr.warning(F" id = {pers_id}; years = {start}->{end}")

    pitch_stats = PrintPitchingStats(lgr)
    season = "post-season" if post else "regular season"
    giv_name, fam_name, num_files = get_events(pitch_stats, post, pers_id, start, end, lgr)
    # need_name = True
    # fam_name = pers_id
    # giv_name = ""
    # num_files = 0
    # try:
    #     for year in range(start, end+1):
    #         year_events = list()
    #         # get the team files
    #         team_file_name = REGULAR_SEASON_FOLDER + "TEAM" + str(year)
    #         lgr.debug(F"team file name = {team_file_name}")
    #         if not osp.exists(team_file_name):
    #             lgr.exception(F"CANNOT find team file {team_file_name}!")
    #             continue
    #         with open(team_file_name, newline = '') as team_csvfile:
    #             team_reader = csv.reader(team_csvfile)
    #             for trow in team_reader:
    #                 rteam = trow[0]
    #                 lgr.debug(F"Found team {rteam}")
    #                 # search rosters for the player's full name
    #                 if need_name:
    #                     roster_file = ROSTERS_FOLDER + rteam + str(year) + ".ROS"
    #                     lgr.debug(F"roster file name = {roster_file}")
    #                     if not osp.exists(roster_file):
    #                         raise FileNotFoundError(F"CANNOT find roster file {roster_file}!")
    #                     with open(roster_file, newline = '') as roster_csvfile:
    #                         ros_reader = csv.reader(roster_csvfile)
    #                         for rrow in ros_reader:
    #                             if pers_id == rrow[0]:
    #                                 fam_name = rrow[1]
    #                                 giv_name = rrow[2]
    #                                 need_name = False
    #                                 break
    #                 if not post:
    #                     # find and store the event file paths for the requested years
    #                     rfile = REGULAR_SEASON_FOLDER + str(year) + rteam + ".EV" + trow[1]
    #                     if not osp.exists(rfile):
    #                         raise FileNotFoundError(F"CANNOT find {season} event file {rfile}!")
    #                     year_events.append(rfile)
    #                     num_files += 1
    #
    #         if post:
    #             # find and store the event file paths for the requested years
    #             post_files = POST_SEASON_FOLDER + str(year) + "*"
    #             for pfile in glob.glob(post_files):
    #                 lgr.debug(F"{season} file name = {pfile}")
    #                 if not osp.exists(pfile):
    #                     raise FileNotFoundError(F"CANNOT find {season} event file {pfile}!")
    #                 year_events.append(pfile)
    #                 num_files += 1
    #
    #         pitch_stats.event_files[str(year)] = year_events

    name = F"{giv_name} {fam_name}"
    lgr.warning(F"name = {name}")
    lgr.warning(F"found {num_files} {season} event files over {len(pitch_stats.event_files)} years.")
    for item in pitch_stats.event_files:
        lgr.debug(item)

    pitch_stats.print_stats(pers_id, name, season, start, end)


if __name__ == "__main__":
    if '-q' not in sys.argv:
        print(F"Start time = {run_ts}")
    main_pitching_stats(sys.argv[1:])
    if '-q' not in sys.argv:
        run_time = (dt.now() - now_dt).total_seconds()
        print(F" Running time = {(run_time // 60)} minutes, {(run_time % 60):2.3} seconds")
    exit()
