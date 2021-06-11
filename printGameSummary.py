##############################################################################################################################
# coding=utf-8
#
# printGameSummary.py -- print a summary of baseball game or games using Retrosheet data
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
__created__ = "2019-11-07"
__updated__ = "2021-06-11"

from mhsUtils import dt, run_ts, now_dt
from mhsLogging import MhsLogger
from cwTools import *


class PrintGameSummary:
    """Print MLB game summaries using Retrosheet data."""
    def __init__(self, logger:lg.Logger):
        self.note_count = 0
        self.lgr = logger
        self.lgr.warning(F" Start {self.__class__.__name__}")

    # void cwbox_print_text(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    # noinspection PyAttributeOutsideInit
    def print_summary( self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer ):
        self.lgr.info("\n----------------------------------")

        self.game = p_game
        self.box  = p_box
        self.vis_rost  = p_vis
        self.home_rost = p_home

        self.vis_city = c_char_p_to_str(p_vis.contents.city, 16) \
                          if p_vis else MyCwlib.game_info_lookup(self.game, b'visteam')
        self.lgr.info(F"visitor = {self.vis_city}")

        self.home_city = c_char_p_to_str(p_home.contents.city, 16) \
                           if p_home else MyCwlib.game_info_lookup(self.game, b'hometeam')
        self.lgr.info(F"home = {self.home_city}")

        self.print_header()
        self.print_linescore()

        self.print_batting()
        self.print_pitching()

        self.print_time_of_game()
        self.print_attendance()

    # void cwbox_print_header(CWGame *game, CWRoster *visitors, CWRoster *home)
    def print_header( self):
        self.lgr.info("\n----------------------------------")
        dn_code = '?'
        day_night = MyCwlib.game_info_lookup(self.game, b'daynight')
        if day_night:
            dn_code = 'D' if day_night == "day" else 'N' if day_night == "night" else day_night

        game_date = MyCwlib.game_info_lookup(self.game, b'date')
        self.lgr.info(F"game date = {game_date}")
        year, month, day = game_date.split('/')
        game_number = MyCwlib.game_info_lookup(self.game, b'number')
        self.lgr.info(F"game number = {game_number}")
        game_number_str = '' if game_number == '0' else F", game #{game_number}"

        print(F"\n\t\tGame of {month}/{day}/{year}{game_number_str} -- {self.vis_city} @ {self.home_city} ({dn_code})\n")

    # void cwbox_print_linescore(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_linescore( self):
        self.lgr.info("\n----------------------------------")
        linescore = self.box.contents.linescore
        for t in range(2):
            runs = 0
            city = self.home_city if t == 1 else self.vis_city
            print(F"{city:16}", end = '')

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

        if self.box.contents.outs_at_end != 3:
            result = "winning run scored" if self.box.contents.walk_off else "game ended"
            print(F"  {self.box.contents.outs_at_end} out when {result}.")
        print('')

    def print_batting(self):
        self.lgr.info("\n----------------------------------")
        slots = [1, 1]
        players = list()
        ab = [0, 0]
        r  = [0, 0]
        h  = [0, 0]
        bi = [0, 0]
        pa = [0, 0]
        bb = [0, 0]
        so = [0, 0]

        # ?? using cwlib.cw_box_get_starter() FAILS here as print_batter() gets players[t] as an int... see below
        player0 = MyCwlib.box_get_starter(self.box, 0, 1)
        self.lgr.debug(F"\ntype(player0) = {type(player0)}")
        players.insert(0, player0)
        player1 = MyCwlib.box_get_starter(self.box, 1, 1)
        self.lgr.debug(F"\ntype(player1) = {type(player1)}")
        players.insert(1, player1)

        print(F"  {self.vis_city:18} PA  AB   H  BB  SO  R RBI      {self.home_city:18} PA  AB   H  BB  SO  R RBI    ")
        while slots[0] <= 9 or slots[1] <= 9:
            for t in range(2):
                if slots[t] <= 9:
                    self.print_batter(players[t], t)  # see note just above
                    batting = players[t].contents.batting.contents
                    ab[t] += batting.ab
                    r[t] += batting.r
                    h[t] += batting.h
                    bb[t] += batting.bb
                    pa[t] += batting.pa
                    so[t] += batting.so
                    if batting.bi != -1:
                        bi[t] += batting.bi
                    else:
                        bi[t] = -1
                    # get any replacement players for this slot
                    players[t] = players[t].contents.next
                    # get the next starter for this team
                    if not players[t]:
                        while slots[t] <= 9 and not players[t]:
                            slots[t] += 1
                            if slots[t] <= 9:
                                # ?? using cwlib.cw_box_get_starter() works fine here
                                players[t] = MyCwlib.box_get_starter(self.box, t, slots[t])
                                self.lgr.debug(F"slots[{t}] = {slots[t]}:{players[t].contents.name}")
                else:
                    print(''.ljust(45), end = '')
                print("     ", end = ''),
            print('')

        # print the totals for both teams
        print(F"{''.ljust(20)} --  --  --  --  -- -- -- {''.ljust(24)} --  --  --  --  -- -- --")
        print(F"{''.ljust(20)}{pa[0]:3}{ab[0]:4}{h[0]:4}{bb[0]:4}{so[0]:4}{r[0]:3}", end = '')
        print(F"{bi[0]:3} " if bi[0] >= 0 else "    ", end = '')
        print(F"{''.ljust(24)}{pa[1]:3}{ab[1]:4}{h[1]:4}{bb[1]:4}{so[1]:4}{r[1]:3}", end = '')
        print(F"{bi[1]:3} " if bi[1] >= 0 else "    ")
        print('')
        self.print_batting_apparatus()
        print('')

    def print_pitching(self):
        self.lgr.info("\n----------------------------------")
        self.note_count = 0
        for t in range(2):
            pitcher = MyCwlib.box_get_starting_pitcher(self.box, t)
            city = self.home_city if t == 1 else self.vis_city
            print(F"  {city:20} IP  H  R ER BB SO  TP TS GB FB")

            while pitcher:
                self.print_pitcher(pitcher, t)
                pitcher = pitcher.contents.next
            if t == 0:
                print('')
        print('')
        if self.print_pitching_apparatus():
            print('')

    # void cwbox_print_timeofgame(CWGame * game)
    def print_time_of_game(self):
        self.lgr.info("\n----------------------------------")
        tog = int(MyCwlib.game_info_lookup(self.game, b'timeofgame'))
        if tog and tog > 0:
            minutes = str(tog % 60)
            if len(minutes) == 1: minutes = '0' + minutes
            print(F"T -- {tog // 60}:{minutes}")

    # void cwbox_print_attendance(CWGame * game)
    def print_attendance(self):
        self.lgr.info("\n----------------------------------")
        print(F"A -- {MyCwlib.game_info_lookup(self.game, b'attendance')}")

    # void cwbox_print_player(CWBoxPlayer *player, CWRoster *roster)
    def print_batter( self, p_player:pointer, side:int ):
        self.lgr.info("\n----------------------------------")
        bio = None
        posstr = ''
        p_roster = self.home_rost if side == 1 else self.vis_rost
        player = p_player.contents
        if p_roster:
            bio = MyCwlib.roster_player_find(p_roster, player.player_id)
        if bio:
            name = c_char_p_to_str(bio.contents.last_name) + ' ' + c_char_p_to_str(bio.contents.first_name, 1)
        else:
            name = player.name
        self.lgr.info(F"player name = {name}")

        if player.ph_inn > 0 and player.positions[0] != 11:
            posstr = "ph"
        elif player.pr_inn > 0 and player.positions[0] != 12:
            posstr = "pr"

        for pos in range( player.num_positions ):
            if len(posstr) > 0:
                posstr += '-'
            posstr += POSITIONS[player.positions[pos]]

        if len(posstr) <= 10:
            if len(posstr) + len(name) > 18:
                outstr = F"{name[:(18 - len(posstr))]}, "
            else:
                outstr = F"{name}, "
            outstr += posstr
        else:
            # When there are a lot of positions, can't do much sensibly...
            outstr = F"{name}, {POSITIONS[player.positions[0]]}..."

        self.lgr.info(F"outstr = {outstr}")

        batting = player.batting.contents
        print(F"{outstr:20}{batting.pa:3}{batting.ab:4}{batting.h:4}{batting.bb:4}{batting.so:4}{batting.r:3}", end = '')
        print(F"{batting.bi:3}" if batting.bi >= 0 else "", end = '')

    # void cwbox_print_apparatus(CWGame * game, CWBoxscore * boxscore, CWRoster * visitors, CWRoster * home)
    def print_batting_apparatus(self):
        """Output the batting apparatus: info on miscellaneous batting events: DP, 2B, SB, CS etc."""
        self.lgr.info("\n----------------------------------")

        boxscore = self.box.contents
        self.print_player_apparatus(boxscore.err_list, 0, 'E')
        self.print_double_plays()
        self.print_triple_plays()
        self.print_lob()
        self.print_player_apparatus(boxscore.b2_list, 0, "2B")
        self.print_player_apparatus(boxscore.b3_list, 0, "3B")
        self.print_player_apparatus(boxscore.hr_list, 0, "HR")
        self.print_player_apparatus(boxscore.sb_list, 0, "SB")
        self.print_player_apparatus(boxscore.cs_list, 0, "CS")
        self.print_player_apparatus(boxscore.sh_list, 0, "SH")
        self.print_player_apparatus(boxscore.sf_list, 0, "SF")

    # void cwbox_print_pitcher(CWGame * game, CWBoxPitcher * pitcher, CWRoster * roster, int * note_count)
    def print_pitcher( self, p_pitcher:pointer, side:int ):
        self.lgr.info("\n----------------------------------")
        # Output one pitcher's pitching line. The parameter 'note_count' keeps track of how many apparatus notes
        # have been emitted (for pitchers who do not record an out in an inning)
        bio = None
        p_roster = self.home_rost
        if side == 0:
            p_roster = self.vis_rost
        roster = p_roster.contents
        pitcher = p_pitcher.contents
        player_id = pitcher.player_id.decode(UTF8_ENCODING)
        self.lgr.info(F"player id = {player_id}")
        self.lgr.debug(F"type(player id) = {type(player_id)}")
        if roster:
            bio = MyCwlib.roster_player_find(p_roster, bytes(pitcher.player_id))
        if bio:
            name = c_char_p_to_str(bio.contents.last_name) + " " + c_char_p_to_str(bio.contents.first_name, 1)
        else:
            name = pitcher.name
        self.lgr.info(F"pitcher name = {name}")

        game = self.game.contents
        wp = MyCwlib.game_info_lookup(game, b'wp')
        self.lgr.info(F"winning pitcher id = {wp}")
        self.lgr.debug(F"type(wp) = {type(wp)}")
        lp = MyCwlib.game_info_lookup(game, b'lp')
        self.lgr.info(F"losing pitcher id = {lp}")
        save = MyCwlib.game_info_lookup(game, b'save')
        self.lgr.info(F"save pitcher id = {save}")
        if wp and wp == player_id:
            name += " (W)"
        elif lp and lp == player_id:
            name += " (L)"
        elif save and save == player_id:
            name += " (S)"

        pitching = pitcher.pitching.contents
        if pitching.xbinn > 0 and pitching.xb > 0:
            for i in range( (self.note_count // 3)+1 ):
                name += MARKERS[self.note_count % 3]
            self.note_count += 1

        print(F"{name:20} {pitching.outs // 3:2}.{pitching.outs % 3} {pitching.h:2} {pitching.r:2}", end = '')
        print(F"{pitching.er:3}" if pitching.er >= 0 else "   ", end = '')
        print(F"{pitching.bb:3}" if pitching.bb >= 0 else "   ", end = '')
        print(F"{pitching.so:3}" if pitching.so >= 0 else "   ", end = '')
        print(F"{pitching.pitches:4}" if pitching.pitches >= 0 else "    ", end = '')
        print(F"{pitching.strikes:3}" if pitching.strikes >= 0 else "   ", end = '')
        print(F"{pitching.gb:3}" if pitching.gb >= 0 else "   ", end = '')
        print(F"{pitching.fb:3}" if pitching.fb >= 0 else "   ")

    # void cwbox_print_pitcher_apparatus(CWBoxscore * boxscore)
    def print_pitching_apparatus(self) -> bool:
        """Output the pitching apparatus as well as info on pitchers who did not record an out in an inning."""
        self.lgr.info("\n----------------------------------")
        boxscore = self.box.contents

        bxp = False
        count = 0
        for t in range(2):
            pitcher = MyCwlib.box_get_starting_pitcher(self.box, t)
            while pitcher:
                pitching = pitcher.contents.pitching.contents
                if pitching.xbinn > 0 and pitching.xb > 0:
                    bxp = True
                    print("  ", end = '')
                    for i in range( (count // 3)+1 ):
                        print(F"{MARKERS[count % 3]}", end = '')
                    print(F" Pitched to {pitching.xb} batter{'' if pitching.xb == 1 else 's'} in {pitching.xbinn}", end = '')
                    if pitching.xbinn % 10 == 1 and pitching.xbinn != 11:
                        print("st")
                    elif pitching.xbinn % 10 == 2 and pitching.xbinn != 12:
                        print("nd")
                    elif pitching.xbinn % 10 == 3 and pitching.xbinn != 13:
                        print("rd")
                    else:
                        print("th")
                    count += 1
                pitcher = pitcher.contents.next

        bhbp = self.print_hbp(boxscore.hp_list)
        bwp = self.print_player_apparatus(boxscore.wp_list, 0, "WP")
        bpb = self.print_player_apparatus(boxscore.pb_list, 1, "PB")
        balk = self.print_player_apparatus(boxscore.bk_list, 0, "Balk")

        return bhbp or bwp or bpb or balk or bxp

    # void
    # cwbox_print_player_apparatus(CWGame *game, CWBoxEvent *list, int index, char *label, CWRoster *visitors, CWRoster *home)
    def print_player_apparatus(self, p_events:pointer, index:int, label:str) -> bool:
        """Output for various events: 2B, 3B, WP, Balk etc."""
        self.lgr.info("\n----------------------------------")
        if not p_events:
            return False
        event = p_events.contents
        comma = False
        print(F"{label} -- ", end = '')
        while event:
            search_event = event
            bio = None
            name = ''
            count = 0
            if event.mark > 0:
                event = event.next.contents if event.next else None
                continue
            # find any multiple events by the same player and keep count
            while search_event:
                if event.players[index] == search_event.players[index]:
                    count += 1
                    search_event.mark = 1
                search_event = search_event.next.contents if search_event.next else None

            if self.vis_rost:
                bio = MyCwlib.roster_player_find(self.vis_rost, event.players[index])
            if not bio and self.home_rost:
                bio = MyCwlib.roster_player_find(self.home_rost, event.players[index])
            if not bio:
                name = event.players[index].decode(UTF8_ENCODING)
                self.lgr.warning("bio NOT available!")
            if comma:
                print(", ", end = '')

            if count == 1:
                if bio:
                    print( c_char_p_to_str(bio.contents.last_name) + " "
                           + c_char_p_to_str(bio.contents.first_name[0],1), end = '' )
                elif name:
                    print(name, end = '')
                else:
                    print(event.players[index].decode(UTF8_ENCODING), end = '')
            else:
                if bio:
                    print(F"{c_char_p_to_str(bio.contents.last_name)} "
                          F"{c_char_p_to_str(bio.contents.first_name[0],1)} {count}", end = '')
                elif name:
                    print(F"{name} {count}", end = '')
                else:
                    print(F"{event.players[index].decode(UTF8_ENCODING)} {count}", end = '')
            comma = True
        print('')
        return True

    # void cwbox_print_double_play(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_double_plays(self):
        self.lgr.info("\n----------------------------------")
        dp = self.box.contents.dp
        if dp[0] == 0 and dp[1] == 0:
            return
        print("DP -- ", end = '')

        if dp[0] > 0 and dp[1] == 0:
            print(F"{self.vis_city} {dp[0]}")
        elif dp[0] == 0 and dp[1] > 0:
            print(F"{self.home_city} {dp[1]}")
        else:
            print(F"{self.vis_city} {dp[0]}, {self.home_city} {dp[1]}")

    # void cwbox_print_triple_play(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_triple_plays(self):
        self.lgr.info("\n----------------------------------")
        tp = self.box.contents.tp
        if tp[0] == 0 and tp[1] == 0:
            return
        print("TP -- ", end = '')

        if tp[0] > 0 and tp[1] == 0:
            print(F"{self.vis_city} {tp[0]}")
        elif tp[0] == 0 and tp[1] > 0:
            print(F"{self.home_city} {tp[1]}")
        else:
            print(F"{self.vis_city} {tp[0]}, {self.home_city} {tp[1]}")

    # void cwbox_print_hbp_apparatus(CWGame *game, CWBoxEvent *list,  CWRoster *visitors, CWRoster *home)
    def print_hbp(self, p_event:pointer) -> bool:
        self.lgr.info("\n----------------------------------")
        if not p_event:
            return False
        event = p_event
        comma = False
        print("HBP -- ", end = '')
        while event:
            search_event = event
            batter = pitcher = None
            batter_name = pitcher_name = ''
            count = 0
            if event.contents.mark > 0:
                event = event.contents.next
                continue

            while search_event:
                if event.contents.players[0] == search_event.contents.players[0] \
                        and event.contents.players[1] == search_event.contents.players[1]:
                    count += 1
                    search_event.contents.mark = 1
                search_event = search_event.contents.next

            if self.vis_rost:
                batter = MyCwlib.roster_player_find(self.vis_rost, event.contents.players[0])
                pitcher = MyCwlib.roster_player_find(self.vis_rost, event.contents.players[1])
            if self.home_rost:
                if not batter: batter = MyCwlib.roster_player_find(self.home_rost, event.contents.players[0])
                if not pitcher: pitcher = MyCwlib.roster_player_find(self.home_rost, event.contents.players[1])
            if not batter:
                batter_name = event.contents.players[0].decode(UTF8_ENCODING)
                self.lgr.warning("roster NOT available for batter!")
            if not pitcher:
                pitcher_name = event.contents.players[1].decode(UTF8_ENCODING)
                self.lgr.warning("roster NOT available for pitcher!")
            if comma:
                print(", ", end = '')

            if pitcher:
                print(F"by {c_char_p_to_str(pitcher.contents.last_name)} "
                      F"{pitcher.contents.first_name[0].decode(UTF8_ENCODING)} ", end = '')
            else:
                print(F"by {pitcher_name if pitcher_name else c_char_p_to_str(event.contents.players[1])} ", end = '')
            if batter:
                print(F"({c_char_p_to_str(batter.contents.last_name)} "
                      F"{batter.contents.first_name[0].decode(UTF8_ENCODING)})", end = '')
            else:
                print(F"({batter_name if batter_name else c_char_p_to_str(event.contents.players[0])})", end = '')
            if count != 1:
                print(F" {count}")
            comma = True
        print('')
        return True

    # void cwbox_print_lob(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_lob(self):
        self.lgr.info("\n----------------------------------")
        lob = self.box.contents.lob
        if lob[0] == 0 and lob[1] == 0:
            return
        print(F"LOB -- {self.vis_city} {lob[0]}, {self.home_city} {lob[1]}")

# END class PrintGameSummary


def process_args():
    arg_parser = ArgumentParser(description="Print boxscore(s) from retrosheet data for the specified team and date range",
                                prog='main_game_summary.py')
    # required arguments
    required = arg_parser.add_argument_group('REQUIRED')
    required.add_argument('-t', '--team', required=True, help="Retrosheet 3-character id for a team, e.g. TOR, LAN")
    required.add_argument('-y', '--year', type=int, required=True, help="year to find games to print out (yyyy)")
    # optional arguments
    arg_parser.add_argument('-s', '--start', help="start date to print out games (mmdd)")
    arg_parser.add_argument('-e', '--end', help="end date to print out games (mmdd)")
    arg_parser.add_argument('-p', '--post', action="store_true", help=F"find {POST_SEASON} games instead of {REG_SEASON}")
    arg_parser.add_argument('-q', '--quiet', action="store_true", help="NO logging")
    arg_parser.add_argument('-l', '--level', default=lg.getLevelName(DEFAULT_CONSOLE_LEVEL), help="set LEVEL of logging output")

    return arg_parser


def process_input_parameters(argl:list):
    argp = process_args().parse_args(argl)
    loglevel = lg.getLevelName(QUIET_LOG_LEVEL) if argp.quiet else argp.level.strip().upper()
    try:
        getattr( lg, loglevel )
    except AttributeError as ae:
        print(F"Problem with log level: {repr(ae)}")
        loglevel = DEFAULT_CONSOLE_LEVEL

    if argp.team.isalnum() and len(argp.team.strip()) >= 3:
        team = argp.team.strip().upper()
    else:
        print(F">>> IMPROPER team name '{argp.team}'! Using default value = TOR.\n")
        team = "TOR"
    if len(team) > 3:
        team = team[:3]

    if RETROSHEET_START_YEAR <= argp.year <= RETROSHEET_END_YEAR:
        year = str(argp.year)
    else:
        print(F">>> INVALID year '{argp.year}'! Using default year = 1993.\n")
        year = "1993"

    if argp.start:
        start = argp.start.strip() if argp.start.isdecimal() and len(argp.start) == 4 else "0701"
        end = argp.end.strip() if argp.end and argp.end.isdecimal() and len(argp.end) == 4 else start
        if end < start: end = start
    else: # the entire year
        start = "0901" if argp.post else "0301"
        end = "1231" if argp.post else "1031"

    return team, year, start, end, argp.post, loglevel


def main_game_summary(args:list):
    team, year, start, end, post, loglevel = process_input_parameters(args)

    lg_ctrl = MhsLogger(__file__, con_level = loglevel, folder = "logs/games")
    lgr = lg_ctrl.get_logger()
    lgr.debug(F"loglevel = {repr(loglevel)}")
    lgr.warning(F" team = {team}; year = {year}; start = {start}; end = {end}")

    games = {}
    rosters = {}
    event_files = {}
    season = POST_SEASON if post else REG_SEASON
    try:
        # get the team files
        team_file_name = REGULAR_SEASON_FOLDER + "TEAM" + year
        lgr.info(F"team file name = {team_file_name}")
        with open(team_file_name, newline = '') as csvfile:
            teamreader = csv.reader(csvfile)
            for row in teamreader:
                rteam = row[0]
                lgr.debug(F"Found team {rteam}")
                if rteam == team:
                    lgr.info(F"\t-- league is {row[1]}L; city is {row[2]}; nickname is {row[3]}")
                # create the rosters
                rosters[rteam] = MyCwlib.roster_create(rteam, int(year), row[1]+"L", row[2], row[3])
                roster_file = ROSTERS_FOLDER + rteam + year + ".ROS"
                lgr.debug(F"roster file name = {roster_file}")
                if not osp.exists(roster_file):
                    raise FileNotFoundError(F"CANNOT find roster file {roster_file}!")
                roster_fptr = chadwick.fopen( bytes(roster_file, UTF8_ENCODING) )
                # fill the rosters
                roster_read_result = MyCwlib.roster_read(rosters[rteam], roster_fptr)
                lgr.debug("roster read result = " + ("Failure!" if roster_read_result == 0 else "Success."))
                chadwick.fclose(roster_fptr)
                if not post:
                    # find and store the event file paths
                    rfile = REGULAR_SEASON_FOLDER + year + rteam + ".EV" + row[1]
                    if not osp.exists(rfile):
                        raise FileNotFoundError(F"CANNOT find {season} event file {rfile}!")
                    event_files[rteam] = rfile

        if post:
            # find and store the event file paths for the requested years
            post_files = POST_SEASON_FOLDER + str(year) + "*"
            for pfile in glob.glob(post_files):
                basename = get_base_filename(pfile)
                lgr.debug(F"{season} base file name = {basename}")
                if not osp.exists(pfile):
                    raise FileNotFoundError(F"CANNOT find {season} event file {pfile}!")
                event_files[basename] = pfile

        start_date = year + start
        end_date = year + end
        lgr.info(F"start date = {start_date}; end date = {end_date}")

        # get all the games for the requested team in the supplied date range
        for evteam in event_files:
            lgr.debug(F"found event file for {('file' if post else 'team')} = {evteam}")
            cwgames = chadwick.games( event_files[evteam] )
            for game in cwgames:
                game_id = game.contents.game_id.decode(encoding = UTF8_ENCODING)
                game_date = game_id[3:11]
                lgr.debug(F" Found game id = {game_id}; date = {game_date}")

                if end_date >= game_date >= start_date:
                    proc_game = chadwick.process_game(game)
                    g_results = tuple(proc_game)
                    if team == g_results[0]["HOME_TEAM_ID"] or team == g_results[0]["AWAY_TEAM_ID"]:
                        lgr.info(F" Found game id = {game_id}")
                        games[game_id[3:]] = game

        lgr.warning(F" Found {len(games)} {season} games")
        pgs = PrintGameSummary(lgr)
        # sort the games and print out the information
        for key in sorted( games.keys() ):
            kgame = games[key]
            kbox = MyCwlib.box_create(kgame)
            kevents = chadwick.process_game(kgame)
            ev_results = tuple(kevents)
            visitor = rosters[ ev_results[0]["AWAY_TEAM_ID"] ]
            home = rosters[ ev_results[0]["HOME_TEAM_ID"] ]

            pgs.print_summary(kgame, kbox, visitor, home)

    except Exception as ex:
        lgr.exception(F"Exception: {repr(ex)}")


if __name__ == "__main__":
    if '-q' not in sys.argv:
        print(F"\n\tStart time = {run_ts}\n")
    main_game_summary(sys.argv[1:])
    if '-q' not in sys.argv:
        run_time = (dt.now() - now_dt).total_seconds()
        print(F"\n\tRunning time = {(run_time // 60)} minutes, {(run_time % 60):2.3} seconds\n")
    exit()
