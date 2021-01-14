import sys
from pychadwick.box import CWBoxPlayer, CWBoxPitcher
from pychadwick.chadwick import *
from pychadwick.roster import CWPlayer
from ctypes import c_void_p

chadwick = Chadwick()
cwlib = chadwick.libchadwick

CAL = "CAL"
SEA = "SEA"

positions = ["", "p", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf", "dh", "ph", "pr"]

tor_1996_events = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/event/regular/1996TOR.EVA"
tor_1996_roster = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/TOR1996.ROS"

roster_files = {
    CAL:"/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/CAL1996.ROS",
    SEA:"/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/SEA1996.ROS"
}


class CwHelper:
    @staticmethod
    def bytes_to_str(byt:bytes, maxlen:int=20) -> str:
        """Convert a c-type char array to a python string:
           convert and concatenate the values until hit the null terminator or the char limit"""
        if len(byt) == 1:
            return chr(byt[0])
        result = ""
        if len(byt) == 0:
            return result
        ct = 0
        limit = 1 if maxlen <= 1 else min(maxlen, 1024)
        for b in byt:
            if b == 0:
                return result.strip()
            result += chr(b)
            ct += 1
            if ct == limit:
                return result.strip()

    @staticmethod
    def check_for_file(file_path:str, lgr:logging.Logger):
        if not os.path.exists(file_path):
            lgr.info(F"CANNOT find file {file_path}: try to create.")
            try:
                open(file_path, "w+").close()
            except Exception as cfe:
                raise OSError(F"CANNOT create file {file_path}: {repr(cfe)}")
# END class CwHelper


class MyCwlib:
    # char * cw_game_info_lookup(CWGame * game, char * label)
    @staticmethod
    def cwlib_game_info_lookup(game_ptr:POINTER(CWGame), label:bytes) -> str:
        # lgr.info("\n cwlib_game_info_lookup():\n-------------------------")
        func = cwlib.cw_game_info_lookup
        func.restype = c_char_p
        func.argtypes = (POINTER(CWGame), c_char_p,)
        result = func(game_ptr, label)
        return result.decode(encoding = 'UTF-8')

    # void cw_game_write(CWGame *game, FILE *file)
    @staticmethod
    def cwlib_game_write(game_ptr:POINTER(CWGame), file_ptr:c_void_p):
        # lgr.info("\n cwlib_game_write():\n-------------------------")
        func = cwlib.cw_game_write
        func.restype = None
        func.argtypes = (POINTER(CWGame), c_void_p,)
        return func(game_ptr, file_ptr)

    # CWGameIterator *cw_gameiter_create(CWGame *game)
    @staticmethod
    def cwlib_gameiter_create(game_ptr:POINTER(CWGame)) -> POINTER(CWGameIterator):
        # lgr.info("\n cwlib_gameiter_create():\n-------------------------")
        func = cwlib.cw_gameiter_create
        func.restype = POINTER(CWGameIterator)
        func.argtypes = (POINTER(CWGame),)
        return func(game_ptr)

    # CWBoxscore *cw_box_create(CWGame *game)
    @staticmethod
    def cwlib_box_create(game_ptr:POINTER(CWGame)) -> POINTER(CWBoxscore):
        # lgr.info("\n cwlib_box_create():\n-------------------------")
        func = cwlib.cw_box_create
        func.restype = POINTER(CWBoxscore)
        func.argtypes = (POINTER(CWGame),)
        return func(game_ptr)

    # CWRoster *cw_roster_create(char *team_id, int year, char *league, char *city, char *nickname)
    @staticmethod
    def cwlib_roster_create(team:str, year:int, league:str, city:str, nickname:str) -> POINTER(CWRoster):
        # self.lgr.info("\n cwlib_roster_create():\n-------------------------")
        bteam = bytes(team, "utf8")
        bleague = bytes(league, "utf8")
        bcity = bytes(city, "utf8")
        bnickname = bytes(nickname, "utf8")

        func = cwlib.cw_roster_create
        func.restype = POINTER(CWRoster)
        func.argtypes = (c_char_p, c_int, c_char_p, c_char_p, c_char_p,)
        return func(bteam, year, bleague, bcity, bnickname)

    # int cw_roster_read(CWRoster *roster, FILE *file)
    @staticmethod
    def cwlib_roster_read(roster_ptr:POINTER(CWRoster), file_handle:c_void_p) -> int:
        # lgr.info("\n cwlib_roster_read():\n-------------------------")
        func = cwlib.cw_roster_read
        func.restype = c_int
        func.argtypes = (POINTER(CWRoster), c_void_p,)
        return func(roster_ptr, file_handle)

    # CWPlayer *cw_roster_player_find(CWRoster *roster, char *player_id)
    @staticmethod
    def cwlib_roster_player_find(roster_ptr:POINTER(CWRoster), player_id:bytes) -> POINTER(CWPlayer):
        # lgr.info("\n cwlib_roster_player_find():\n-------------------------")
        func = cwlib.cw_roster_player_find
        func.restype = POINTER(CWPlayer)
        func.argtypes = (POINTER(CWRoster), c_char_p,)
        return func(roster_ptr, player_id)

    # CWBoxPlayer *cw_box_get_starter(CWBoxscore *boxscore, int team, int slot)
    @staticmethod
    def cwlib_box_get_starter(box_ptr:POINTER(CWBoxscore), team:int, slot:int) -> POINTER(CWBoxPlayer):
        logging.info(" cwlib_box_get_starter():\n-------------------------")
        func = cwlib.cw_box_get_starter
        func.restype = POINTER(CWBoxPlayer)
        func.argtypes = (POINTER(CWBoxscore), c_int, c_int,)
        return func(box_ptr, team, slot)

    # CWBoxPitcher *cw_box_get_starting_pitcher(CWBoxscore *boxscore, int team)
    @staticmethod
    def cwlib_box_get_starting_pitcher(box_ptr:POINTER(CWBoxscore), team:int) -> POINTER(CWBoxPitcher):
        logging.info("\n cwlib_box_get_starting_pitcher():\n-------------------------")
        func = cwlib.cw_box_get_starting_pitcher
        func.restype = POINTER(CWBoxPitcher)
        func.argtypes = (POINTER(CWBoxscore), c_int,)
        return func(box_ptr, team)
# END class MyCwlib


class MyChadwickTools:
    def __init__(self):
        self.lgr = logging
        self.lgr.info(F"Start {self.__class__.__name__}")

    # void cwbox_print_timeofgame(CWGame * game)
    def print_time_of_game(self, p_game:pointer):
        # Output the time of game
        self.lgr.info("print_time_of_game():\n----------------------------------")
        tog = int(MyCwlib.cwlib_game_info_lookup(p_game, b'timeofgame'))
        if tog and tog > 0:
            print(F"T -- {tog // 60}:{(tog % 60):2}")

    # void cwbox_print_attendance(CWGame * game)
    def print_attendance(self, p_game):
        # Output the attendance
        self.lgr.info("print_attendance():\n----------------------------------")
        print(F"A -- {MyCwlib.cwlib_game_info_lookup(p_game, b'attendance')}")

    # void cwbox_print_header(CWGame *game, CWRoster *visitors, CWRoster *home)
    def print_header( self, p_game:pointer, p_vis:pointer, p_home:pointer ):
        self.lgr.info("print_header():\n----------------------------------")

        dn_code = "?"
        day_night = MyCwlib.cwlib_game_info_lookup(p_game, b"daynight")
        if day_night:
            dn_code = "D" if day_night == "day" else "N" if day_night == "night" else day_night

        game_date = MyCwlib.cwlib_game_info_lookup(p_game, b"date")
        self.lgr.info(F"game date = {game_date}")
        year, month, day = game_date.split('/')
        game_number = MyCwlib.cwlib_game_info_lookup(p_game, b"number")
        self.lgr.info(F"game_number = {game_number}")
        game_number_str = "" if game_number == "0" else F", game #{game_number}"

        vis_city = p_vis.contents.city
        vis_city_text = CwHelper.bytes_to_str(vis_city[:32])
        self.lgr.info(F"visitor = {vis_city_text}")

        home_city = p_home.contents.city
        home_city_text = CwHelper.bytes_to_str(home_city[:32])
        self.lgr.info(F"home = {home_city_text}")

        print(F"\nGame of {month}/{day}/{year}{game_number_str} -- {vis_city_text} @ {home_city_text} ({dn_code})\n")

    # void cwbox_print_linescore(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_linescore( self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer ):
        self.lgr.info("print_linescore():\n----------------------------------")

        linescore = p_box.contents.linescore
        for t in range(0,2):
            runs = 0
            if t == 0:
                print(F"{CwHelper.bytes_to_str(p_vis.contents.city[:32],16):16}" if p_vis
                      else MyCwlib.cwlib_game_info_lookup(p_game, b"visteam"), end = '')
            else:
                print(F"{CwHelper.bytes_to_str(p_home.contents.city[:32],16):16}" if p_home
                      else MyCwlib.cwlib_game_info_lookup(p_game, b"hometeam"), end = '')

            # TODO: handle extra-innings games
            for ix in range(1,10):
                if linescore[ix][t] >= 10:
                    print(F"({linescore[ix][t]})", end = '')
                    runs += linescore[ix][t]
                elif linescore[ix][t] >= 0:
                    print(F"{linescore[ix][t]}", end = '')
                    runs += linescore[ix][t]
                else:
                    print("x", end = '')

                if ix % 3 == 0:
                    print(" ", end = '')

            print(F" -- {runs:2}")

        outs_at_end = p_box.contents.outs_at_end
        if outs_at_end != 3:
            if not p_box.contents.walk_off:
                print(F"  {outs_at_end} out{'' if outs_at_end == 1 else 's'} when game ended.")
            else:
                print(F"  {outs_at_end} out{'' if outs_at_end == 1 else 's'} when winning run scored.")

    # char * cwbox_game_find_name(CWGame * game, char * player_id)
    def game_find_name(self, p_game:pointer, player_id:bytes) -> str:
        # Derive a player name from an appearance record in a game. Used when roster file is not available.
        self.lgr.info("game_find_name():\n----------------------------------")

        app = p_game.contents.first_starter
        while app:
            if app.player_id == player_id:
                return app.name.decode(encoding = 'UTF-8')
            app = app.next

        event = p_game.contents.first_event
        while event:
            app = event.contents.first_sub
            while app:
                if app.player_id == player_id:
                    return app.name.decode(encoding = 'UTF-8')
                app = app.next
            event = event.next
        return ""

# void cwbox_print_text(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_text( self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer ):
        self.lgr.info("print_text():\n----------------------------------")

        note_count = 0
        slots = [1, 1]
        players = list()
        ab = [0, 0]
        r  = [0, 0]
        h  = [0, 0]
        bi = [0, 0]

        player0 = MyCwlib.cwlib_box_get_starter(p_box, 0, 1)
        self.lgr.info(F"type(player0) = {type(player0)}")
        players.insert(0, player0)
        player1 = MyCwlib.cwlib_box_get_starter(p_box, 1, 1)
        self.lgr.info(F"type(player1) = {type(player1)}")
        players.insert(1, player1)

        self.print_header(p_game, p_vis, p_home)

        vis_city = CwHelper.bytes_to_str(p_vis.contents.city[:32]) if p_vis \
                   else MyCwlib.cwlib_game_info_lookup(p_game, b"visteam")
        home_city = CwHelper.bytes_to_str(p_home.contents.city[:32]) if p_home \
                    else MyCwlib.cwlib_game_info_lookup(p_game, b"hometeam")

        print(F"{vis_city:20} AB  R  H RBI    {home_city:20} AB  R  H RBI    ")

        while slots[0] <= 9 or slots[1] <= 9 :
            for t in range(0,2):
                if slots[t] <= 9:
                    self.print_player(players[t], p_vis if (t == 0) else p_home)
                    batting = players[t].contents.battiing.contents
                    ab[t] += batting.ab
                    r[t]  += batting.r
                    h[t]  += batting.h
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
                                players[t] = cwlib.cw_box_get_starter(p_box, t, slots[t])
                else:
                    print(F"{''.ljust(32)}", end = '')
                print("     ", end = ''),
            print("")

        print(F"{''.ljust(20)} -- -- -- -- {''.ljust(24)} -- -- -- --")

        if bi[0] == -1 or bi[1] == -1:
            print(F"{''.ljust(20)} {ab[0]:2} {r[0]:2} {h[0]:2}    {''.ljust(24)} {ab[1]:2} {r[1]:2} {h[1]:2}")
        else:
            print(F"{''.ljust(20)} {ab[0]:2} {r[0]:2} {h[0]:2} {bi[0]:2} {''.ljust(24)} {ab[1]:2} {r[1]:2} {h[1]:2} {bi[1]:2}")
        print("")

        self.print_linescore(p_game, p_box, p_vis, p_home)
        print("")

        for t in range(0, 2):
            pitcher = MyCwlib.cwlib_box_get_starting_pitcher(p_box, t)
            if t == 0:
                print(F"  {vis_city:18}   IP  H  R ER BB SO")
            else:
                print(F"  {home_city:18}   IP  H  R ER BB SO")
            while pitcher:
                self.print_pitcher(p_game, pitcher, (p_vis if (t == 0) else p_home), note_count)
                pitcher = pitcher.contents.next
            if t == 0:
                print("")

        self.print_pitcher_apparatus(p_box)
        print("")

        self.print_apparatus(p_game, p_box, p_vis, p_home)
        print("")

    # void cwbox_print_player(CWBoxPlayer *player, CWRoster *roster)
    def print_player( self, p_player:POINTER(CWBoxPlayer), p_roster:POINTER(CWRoster) ):
        self.lgr.info("print_player():\n----------------------------------")

        bio = None
        posstr = ""

        player = p_player.contents
        if p_roster:
            bio = MyCwlib.cwlib_roster_player_find(p_roster, player.player_id)

        if bio:
            name = CwHelper.bytes_to_str(bio.contents.last_name[:20]) + " " \
                   + CwHelper.bytes_to_str(bio.contents.first_name[:1],1)
        else:
            name = player.name
        self.lgr.info(F"player name = {name}")

        if player.ph_inn > 0 and player.positions[0] != 11:
            posstr = "ph"
        elif player.pr_inn > 0 and player.positions[0] != 12:
            posstr = "pr"

        for pos in range(0, player.num_positions):
            if len(posstr) > 0:
                posstr += "-"
            posstr += positions[player.positions[pos]]

        if len(posstr) <= 10:
            if len(posstr) + len(name) > 18:
                outstr = name[:(18 - len(posstr))]
                outstr += ", "
            else:
                outstr = name
                outstr += ", "
            outstr += posstr
        else:
            # When there are a lot of positions, can't do much sensibly...
            outstr = name
            outstr += ", "
            outstr += positions[player.positions[0]]
            outstr += ",..."
        self.lgr.info(F"outstr = {outstr}")

        batting = player.battiing.contents
        if batting.bi != -1:
            print(F"{outstr:20} {batting.ab:2} {batting.r:2} {batting.h:2} {batting.bi:2}", end = '')
        else:
            print(F"{outstr:20} {batting.ab:2} {batting.r:2} {batting.h:2}", end = '')

    # void cwbox_print_player_apparatus(CWGame *game, CWBoxEvent *list, int index, char *label, CWRoster *visitors, CWRoster *home)
    def print_player_apparatus(self, p_game, p_events, index, label, p_vis, p_home):
        # Generic output for list of events (2B, 3B, WP, etc.)
        self.lgr.info("print_player_apparatus():\n----------------------------------")
        if not p_events:
            return
        event = p_events.contents # CWBoxEvent*
        comma = 0
        print(F"{label} -- ", end = '')
        while event:
            search_event = event
            bio = None
            name = ""
            count = 0
            # print("flag1")
            if event.mark > 0:
                event = event.next.contents if event.next else None
                # print("flag2")
                continue
            while search_event:
                if event.players[index] == search_event.players[index]:
                    count += 1
                    search_event.mark = 1
                    # print("flag3")
                search_event = search_event.next.contents if search_event.next else None

            # print("flag4")
            if p_vis:
                bio = MyCwlib.cwlib_roster_player_find(p_vis, event.players[index])
            if not bio and p_home:
                bio = MyCwlib.cwlib_roster_player_find(p_home, event.players[index])
            if not bio:
                name = self.game_find_name(p_game, event.players[index])
            # print("flag5")
            if comma:
                print(", ", end = '')
            if count == 1:
                # print("flag6")
                if bio:
                    print(F"{CwHelper.bytes_to_str(bio.contents.last_name[:20])} "
                          F"{CwHelper.bytes_to_str(bio.contents.first_name[0][:1],1)}", end = '')
                elif name:
                    print(F"{name}", end = '')
                else:
                    print(F"{event.players[index]}", end = '')
            else:
                # print("flag7")
                if bio:
                    print(F"{CwHelper.bytes_to_str(bio.contents.last_name[:20])} "
                          F"{CwHelper.bytes_to_str(bio.contents.first_name[0][:1],1)} {count}", end = '')
                elif name:
                    print(F"{name} {count}", end = '')
                else:
                    print(F"{CwHelper.bytes_to_str(event.players[index][:20])} {count}", end = '')
            comma = 1
        print("")
        # NOTE: reset events.mark >> NEEDED in Python?
        event = p_events.contents
        while event:
            event.mark = 0
            event = event.next.contents if event.next else None

    # void cwbox_print_apparatus(CWGame * game, CWBoxscore * boxscore, CWRoster * visitors, CWRoster * home)
    def print_apparatus( self, p_game, p_box, p_vis, p_home ):
        # Output the apparatus (list of events and other miscellaneous game information)
        self.lgr.info("print_apparatus():\n----------------------------------")

        boxscore = p_box.contents
        self.print_player_apparatus(p_game, boxscore.err_list, 0, "E", p_vis, p_home)
        # cwbox_print_double_play(game, boxscore, visitors, home)
        # cwbox_print_triple_play(game, boxscore, visitors, home)
        # cwbox_print_lob(p_game, boxscore, visitors, home)
        self.print_player_apparatus(p_game, boxscore.b2_list, 0, "2B", p_vis, p_home)
        self.print_player_apparatus(p_game, boxscore.b3_list, 0, "3B", p_vis, p_home)
        self.print_player_apparatus(p_game, boxscore.hr_list, 0, "HR", p_vis, p_home)
        self.print_player_apparatus(p_game, boxscore.sb_list, 0, "SB", p_vis, p_home)
        self.print_player_apparatus(p_game, boxscore.cs_list, 0, "CS", p_vis, p_home)
        self.print_player_apparatus(p_game, boxscore.sh_list, 0, "SH", p_vis, p_home)
        self.print_player_apparatus(p_game, boxscore.sf_list, 0, "SF", p_vis, p_home)
        # cwbox_print_hbp_apparatus(p_game, boxscore.hp_list, p_vis, p_home)
        self.print_player_apparatus(p_game, boxscore.wp_list, 0, "WP", p_vis, p_home)
        self.print_player_apparatus(p_game, boxscore.bk_list, 0, "Balk", p_vis, p_home)
        self.print_player_apparatus(p_game, boxscore.pb_list, 1, "PB", p_vis, p_home)
        self.print_time_of_game(p_game)
        self.print_attendance(p_game)

    # void cwbox_print_pitcher(CWGame * game, CWBoxPitcher * pitcher, CWRoster * roster, int * note_count)
    def print_pitcher( self, p_game, p_pitcher, p_roster, note_count ):
        self.lgr.info("self.print_pitcher():\n----------------------------------")
        # Output one pitcher's pitching line. The parameter 'note_count' keeps track of how many apparatus notes
        # have been emitted (for pitchers who do not record an out in an inning)
        markers = ["*", "+", "#"]
        bio = None

        roster = p_roster.contents
        pitcher = p_pitcher.contents
        player_id = pitcher.player_id.decode("UTF8")
        self.lgr.info(F"player id = {player_id}")
        self.lgr.info(F"type(player id) = {type(player_id)}")
        if roster:
            bio = MyCwlib.cwlib_roster_player_find(p_roster, bytes(pitcher.player_id))

        if bio:
            name = CwHelper.bytes_to_str(bio.contents.last_name[:20]) + " " \
                   + CwHelper.bytes_to_str(bio.contents.first_name[:1],1)
        else:
            name = pitcher.name
        self.lgr.info(F"pitcher name = {name}")

        game = p_game.contents
        wp = MyCwlib.cwlib_game_info_lookup(game, b"wp")
        self.lgr.info(F"winning pitcher id = {wp}")
        self.lgr.info(F"type(wp) = {type(wp)}")
        lp = MyCwlib.cwlib_game_info_lookup(game, b"lp")
        self.lgr.info(F"losing pitcher id = {lp}")
        save = MyCwlib.cwlib_game_info_lookup(game, b"save")
        self.lgr.info(F"save pitcher id = {save}")
        if wp and wp == player_id:
            name += " (W)"
        elif lp and lp == player_id:
            name += " (L)"
        elif save and save == player_id:
            name += " (S)"

        pitching = pitcher.pitching.contents
        if pitching.xbinn > 0 and pitching.xb > 0:
            for i in range(0, note_count // 3):
                name += markers[note_count % 3]
            note_count += 1

        print(F"{name:20} {pitching.outs // 3:2}.{pitching.outs % 3} {pitching.h:2} {pitching.r:2}", end = '')

        if pitching.er != -1:
            print(F" {pitching.er:2}", end = '')
        else:
            print("   ")

        if pitching.bb != -1:
            print(F" {pitching.bb:2}", end = '')
        else:
            print("   ")

        if pitching.so != -1:
            print(F" {pitching.so:2}")
        else:
            print("   ")

    # void cwbox_print_pitcher_apparatus(CWBoxscore * boxscore)
    def print_pitcher_apparatus(self, p_box:pointer):
        # Output the pitching apparatus (list of pitchers who did not record an out in an inning)
        self.lgr.info("self.print_pitcher_apparatus():\n----------------------------------")

        markers = ["*", "+", "#"]
        count = t = 0
        pitcher = MyCwlib.cwlib_box_get_starting_pitcher(p_box, t) # CWBoxPitcher *
        while pitcher:
            pitching = pitcher.contents.pitching.contents
            if pitching.xbinn > 0 and pitching.xb > 0:
                print("  ")
                for i in range(0, count // 3):
                    print(F"{markers[count % 3]}")
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

# END class MyChadwickTools


def main_chadwick_py3(limit:int=10):
    lgr = logging
    lgr.info(F"byteorder = {sys.byteorder}\nlimit = {limit}")
    try:
        # create and fill the visitor rosters
        vis_rosters = {}
        cal_roster = MyCwlib.cwlib_roster_create(CAL, 1996, "AL", "California", "Angels")
        vis_rosters[CAL] = cal_roster
        if not os.path.exists(roster_files[CAL]):
            raise FileNotFoundError(F"CANNOT find file {roster_files[CAL]}!")
        cal_fptr = chadwick.fopen( bytes(roster_files[CAL], "utf8") )
        cal_roster_read_result = MyCwlib.cwlib_roster_read(cal_roster, cal_fptr)
        lgr.info("CAL read result = " + ("Success." if cal_roster_read_result > 0 else "Failure!"))
        sea_roster = MyCwlib.cwlib_roster_create("SEA", 1996, "AL", "Seattle", "Mariners")
        vis_rosters[SEA] = sea_roster
        if not os.path.exists(roster_files[SEA]):
            raise FileNotFoundError(F"CANNOT find file {roster_files[SEA]}!")
        sea_fptr = chadwick.fopen( bytes(roster_files[SEA], "utf8") )
        sea_roster_read_result = MyCwlib.cwlib_roster_read(sea_roster, sea_fptr)
        lgr.info("SEA read result = " + ("Success." if sea_roster_read_result > 0 else "Failure!"))

        # create and fill the home roster
        home = MyCwlib.cwlib_roster_create("TOR", 1996, "AL", "Toronto", "Blue Jays")
        if not os.path.exists(tor_1996_roster):
            raise FileNotFoundError(f"cannot find file {tor_1996_roster}")
        home_fptr = chadwick.fopen( bytes(tor_1996_roster, "utf8") )
        home_roster_read_result = MyCwlib.cwlib_roster_read(home, home_fptr)
        lgr.info("HOME read result = " + ("Success." if home_roster_read_result > 0 else "Failure!"))

        cwtools = MyChadwickTools()
        count = 0
        games = chadwick.games(tor_1996_events)
        for game in games:
            if game and count < limit:
                lgr.info("\tFound a game.")
                lgr.info(F"game id = {game.contents.game_id}")

                box = MyCwlib.cwlib_box_create(game)
                events = chadwick.process_game(game)
                results = tuple(events)
                away_team = results[count]['AWAY_TEAM_ID']
                visitor = vis_rosters[away_team]

                cwtools.print_text(game, box, visitor, home)

                count += 1
    except Exception as ex:
        lgr.warning(F"Exception: {repr(ex)}")


if __name__ == "__main__":
    loglevel = sys.argv[1].strip().upper() if len(sys.argv) >= 1 else "INFO"
    logging.basicConfig(level = loglevel)
    logging.critical(F"main_chadwick_py3(): Level = {loglevel}\n--------------------------------------")
    runlimit = int(sys.argv[2]) if len(sys.argv) >= 2 else 6
    main_chadwick_py3(runlimit)
    exit()
