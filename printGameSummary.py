##############################################################################################################################
# coding=utf-8
#
# printGameSummary.py -- print a summary of baseball game or games using Retrosheet data
#
# Original C code Copyright (c) 2002-2020
# Dr T L Turocy, Chadwick Baseball Bureau (ted.turocy@gmail.com)
#
# Port to Python3 and modifications Copyright (c) 2019-2021 Mark Sattolo <epistemik@gmail.com>

__author__       = "Mark Sattolo"
__author_email__ = "epistemik@gmail.com"
__created__ = "2019-11-07"
__updated__ = "2021-01-21"

import csv
import sys
from argparse import ArgumentParser
from datetime import datetime as dt
from cwLibWrappers import chadwick, cwlib
from cwTools import *


class PrintGameSummary:
    def __init__(self, cwt:MyChadwickTools, logger:logging.Logger):
        self.cwtools = cwt
        self.lgr = logger
        self.lgr.warning(F" Start {self.__class__.__name__}")
        self.rosters = {}
        self.event_files = {}
        self.games = {}
        self.note_count = 0

    # void cwbox_print_header(CWGame *game, CWRoster *visitors, CWRoster *home)
    def print_header( self, p_game:pointer, p_vis:pointer, p_home:pointer ):
        self.lgr.info("print_header():\n----------------------------------")

        dn_code = "?"
        day_night = MyCwlib.game_info_lookup(p_game, b"daynight")
        if day_night:
            dn_code = "D" if day_night == "day" else "N" if day_night == "night" else day_night

        game_date = MyCwlib.game_info_lookup(p_game, b"date")
        self.lgr.info(F"game date = {game_date}")
        year, month, day = game_date.split('/')
        game_number = MyCwlib.game_info_lookup(p_game, b"number")
        self.lgr.info(F"game_number = {game_number}")
        game_number_str = "" if game_number == "0" else F", game #{game_number}"

        vis_city = p_vis.contents.city
        vis_city_text = c_char_p_to_str(vis_city)
        self.lgr.info(F"visitor = {vis_city_text}")

        home_city = p_home.contents.city
        home_city_text = c_char_p_to_str(home_city)
        self.lgr.info(F"home = {home_city_text}")

        print(F"\n\t\tGame of {month}/{day}/{year}{game_number_str} -- {vis_city_text} @ {home_city_text} ({dn_code})\n")

    # void cwbox_print_linescore(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_linescore( self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer ):
        self.lgr.info("print_linescore():\n----------------------------------")

        linescore = p_box.contents.linescore
        for t in range(0,2):
            runs = 0
            if t == 0:
                print(F"{c_char_p_to_str(p_vis.contents.city, 16):16}" if p_vis
                      else MyCwlib.game_info_lookup(p_game, b"visteam"), end = '')
            else:
                print(F"{c_char_p_to_str(p_home.contents.city, 16):16}" if p_home
                      else MyCwlib.game_info_lookup(p_game, b"hometeam"), end = '')

            for ix in range(1,32):
                if linescore[ix][t] >= 10:
                    print(F"({linescore[ix][t]})", end = '')
                    runs += linescore[ix][t]
                elif linescore[ix][t] >= 0:
                    print(F"{linescore[ix][t]}", end = '')
                    runs += linescore[ix][t]
                elif t == 0:
                    break
                elif linescore[ix][0] < 0:
                    break
                else:
                    print("x ", end = '')
                    break

                if ix % 3 == 0:
                    print(" ", end = '')

            print(F" -- {runs:2}")

        outs_at_end = p_box.contents.outs_at_end
        if outs_at_end != 3:
            if p_box.contents.walk_off:
                print(F"  {outs_at_end} out{'' if outs_at_end == 1 else 's'} when winning run scored.")
            else:
                print(F"  {outs_at_end} out{'' if outs_at_end == 1 else 's'} when game ended.")

    # void cwbox_print_text(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_summary( self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer ):
        self.lgr.info("print_game_summary():\n----------------------------------")

        self.note_count = 0
        slots = [1,1]
        players = list()
        ab = [0,0]
        r  = [0,0]
        h  = [0,0]
        bi = [0,0]
        pa = [0,0]
        bb = [0,0]
        so = [0,0]

        # ?? trying to use cwlib.cw_box_get_starter FAILS here as print_player() gets players[t] as an int... see below
        player0 = MyCwlib.box_get_starter(p_box, 0, 1)
        self.lgr.debug(F"type(player0) = {type(player0)}")
        players.insert(0, player0)
        player1 = MyCwlib.box_get_starter(p_box, 1, 1)
        self.lgr.debug(F"type(player1) = {type(player1)}")
        players.insert(1, player1)

        self.print_header(p_game, p_vis, p_home)

        vis_city = c_char_p_to_str(p_vis.contents.city) if p_vis else MyCwlib.game_info_lookup(p_game, b"visteam")
        home_city = c_char_p_to_str(p_home.contents.city) if p_home else MyCwlib.game_info_lookup(p_game, b"hometeam")

        print(F"  {vis_city:18} PA  AB   H  BB  SO  R RBI      {home_city:18} PA  AB   H  BB  SO  R RBI    ")

        while slots[0] <= 9 or slots[1] <= 9 :
            for t in range(0,2):
                if slots[t] <= 9:
                    self.cwtools.print_player(players[t], p_vis if (t == 0) else p_home)
                    # NOTE: misspelling 'battiing' in the python wrapper file
                    batting = players[t].contents.battiing.contents
                    ab[t] += batting.ab
                    r[t]  += batting.r
                    h[t]  += batting.h
                    bb[t] += batting.bb
                    pa[t] += batting.pa
                    so[t] += batting.so
                    if batting.bi != -1:
                        bi[t] += batting.bi
                    else:
                        bi[t] = -1
                    players[t] = players[t].contents.next
                    if not players[t]:
                        # In some National Association games, teams played with 8 players.
                        # This generalization allows for printing boxscores when some batting slots are empty.
                        while slots[t] <= 9 and not players[t]:
                            slots[t] += 1
                            if slots[t] <= 9:
                                self.lgr.debug("\ncwlib.cw_box_get_starter")
                                # ?? using this function WITHOUT the python wrapper works fine here
                                players[t] = cwlib.cw_box_get_starter(p_box, t, slots[t])
                else:
                    print(F"{''.ljust(45)}", end = '')
                print("     ", end = ''),
            print("")

        print(F"{''.ljust(20)} --  --  --  --  -- -- -- {''.ljust(24)} --  --  --  --  -- -- --")
        print(F"{''.ljust(20)}{pa[0]:3}{ab[0]:4}{h[0]:4}{bb[0]:4}{so[0]:4}{r[0]:3}", end = '')
        print(F"{bi[0]:3} " if bi[0] >= 0 else "    ", end = '')
        print(F"{''.ljust(24)}{pa[1]:3}{ab[1]:4}{h[1]:4}{bb[1]:4}{so[1]:4}{r[1]:3}", end = '')
        print(F"{bi[1]:3} " if bi[1] >= 0 else "    ")
        print("")

        self.print_linescore(p_game, p_box, p_vis, p_home)
        print("")

        for t in range(0, 2):
            pitcher = MyCwlib.box_get_starting_pitcher(p_box, t)
            if t == 0:
                print(F"  {vis_city:18}   IP  H  R ER BB SO  TP TS GB FB")
            else:
                print(F"  {home_city:18}   IP  H  R ER BB SO  TP TS GB FB")
            while pitcher:
                self.cwtools.print_pitcher( p_game, pitcher, (p_vis if (t == 0) else p_home) )
                pitcher = pitcher.contents.next
            if t == 0:
                print("")

        self.cwtools.print_pitcher_apparatus(p_box)
        print("")

        self.cwtools.print_apparatus(p_game, p_box, p_vis, p_home)
        print("")

# END class PrintGameSummary


def process_args():
    arg_parser = ArgumentParser(description="Print boxscore(s) from retrosheet data for the specified team and date range",
                                prog='main_chadwick_py3.py')
    # required arguments
    required = arg_parser.add_argument_group('REQUIRED')
    required.add_argument('-t', '--team', required=True, help="Retrosheet 3-character id for a team, e.g. TOR, LAN")
    required.add_argument('-y', '--year', type=int, required=True, help="year to find games to print out (yyyy)")
    # optional arguments
    arg_parser.add_argument('-s', '--start', help="start date to print out games (mmdd)")
    arg_parser.add_argument('-e', '--end', help="end date to print out games (mmdd)")
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

    team = args.team.strip().upper() if args.team.isalpha() and len(args.team.strip()) >= 3 else "TOR"
    if len(team) > 3:
        team = team[:3]
    logging.warning(F"team = {team}")

    year = str(args.year) if 1871 <= args.year <= 2020 else "1993"
    logging.warning(F"year = {year}")

    if args.start:
        start = args.start.strip()
        if not start.isdecimal() or not len(start) == 4:
            start = "9999"
    else:
        start = "0301"
    logging.warning(F"start = {start}")

    if args.end:
        end = args.end.strip()
        if not end.isdecimal() or not len(end) == 4:
            end = "0000"
    else:
        end = "1031"
    logging.warning(F"end = {end}")

    return team, year, start, end, loglevel


def main_game_summary(args:list):
    lgr = logging.getLogger("PrintGameSummary")

    team, year, start, end, loglevel = process_input_parameters(args)

    lgr.setLevel(loglevel)
    lgr.debug( str(lgr.handlers) )
    lgr.warning(F" team = {team}; year = {year}")

    cwtools = MyChadwickTools(lgr)
    pgs = PrintGameSummary(cwtools, lgr)
    try:
        # get the team files
        team_file_name = REGULAR_SEASON_FOLDER + "TEAM" + year
        lgr.info(F"team file name = {team_file_name}")
        with open(team_file_name, newline = '') as csvfile:
            teamreader = csv.reader(csvfile)
            for row in teamreader:
                rteam = row[0]
                lgr.info(F"Found team {rteam}")
                if rteam == team:
                    lgr.info(F"\t-- league is {row[1]}L; city is {row[2]}; nickname is {row[3]}")
                # create the rosters
                pgs.rosters[rteam] = MyCwlib.roster_create(rteam, int(year), row[1]+"L", row[2], row[3])
                roster_file = ROSTERS_FOLDER + rteam + year + ".ROS"
                lgr.debug(F"roster file name = {roster_file}")
                if not os.path.exists(roster_file):
                    raise FileNotFoundError(F"CANNOT find roster file {roster_file}!")
                roster_fptr = chadwick.fopen( bytes(roster_file, "utf8") )
                # fill the rosters
                roster_read_result = MyCwlib.roster_read(pgs.rosters[rteam], roster_fptr)
                lgr.info("roster read result = " + ("Success." if roster_read_result > 0 else "Failure!"))
                chadwick.fclose(roster_fptr)
                # find and store the event file paths
                event_file = REGULAR_SEASON_FOLDER + year + rteam + ".EV" + row[1]
                if not os.path.exists(event_file):
                    raise FileNotFoundError(F"CANNOT find event file {event_file}!")
                pgs.event_files[rteam] = event_file

        for item in pgs.rosters.values():
            lgr.debug(item)
        for item in pgs.event_files.values():
            lgr.debug(item)

        start_id = year + start
        lgr.info(F"start id = {start_id}")
        end_id = year + end
        lgr.info(F"end id = {end_id}")

        # get all the games for the requested team in the supplied date range
        for evteam in pgs.event_files:
            lgr.info(F"found events for team = {evteam}")
            cwgames = chadwick.games( pgs.event_files[evteam] )
            for game in cwgames:
                # lgr.debug(F"type(game) = {type(game)}")
                # type(game) = <class 'pychadwick.game.LP_CWGame'>
                game_id = game.contents.game_id.decode(encoding='UTF-8')
                game_date = game_id[3:11]
                lgr.debug(F" Found game id = {game_id}; date = {game_date}")

                if end_id >= game_date >= start_id:
                    proc_game = chadwick.process_game(game)
                    g_results = tuple(proc_game)
                    home_team = g_results[0]['HOME_TEAM_ID']
                    away_team = g_results[0]['AWAY_TEAM_ID']
                    if home_team == team or away_team == team:
                        lgr.warning(F" Found game id = {game_id}")
                        pgs.games[game_id[3:]] = game

        # sort the games and print out the information
        for key in sorted( pgs.games.keys() ):
            game = pgs.games[key]
            box = MyCwlib.box_create(game)
            events = chadwick.process_game(game)
            e_results = tuple(events)

            away_team = e_results[0]['AWAY_TEAM_ID']
            visitor = pgs.rosters[away_team]
            home_team = e_results[0]['HOME_TEAM_ID']
            home = pgs.rosters[home_team]

            pgs.print_summary(game, box, visitor, home)

    except Exception as ex:
        lgr.exception(F"Exception: {repr(ex)}")


if __name__ == "__main__":
    run_start_time = dt.now()
    if '-q' not in sys.argv:
        logging.critical(F"Run Start time = {run_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    main_game_summary(sys.argv[1:])
    if '-q' not in sys.argv:
        run_time = (dt.now() - run_start_time).total_seconds()
        logging.critical(F" Running time = {(run_time // 60)} minutes, {(run_time % 60):2.3} seconds")
    exit()
