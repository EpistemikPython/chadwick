import sys
from pychadwick.box import CWBoxPlayer, CWBoxPitcher
from pychadwick.chadwick import *
from pychadwick.roster import CWPlayer

chadwick = Chadwick()
cwlib = chadwick.libchadwick

CAL = "CAL"
SEA = "SEA"

positions = [
    "", "p", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf", "dh", "ph", "pr"
]

tor_1996_events = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/event/regular/1996TOR.EVA"
tor_1996_roster = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/TOR1996.ROS"

roster_files = {
    CAL:"/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/CAL1996.ROS",
    SEA:"/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/SEA1996.ROS"
}


class CwHelper:
    @staticmethod
    def bytes_to_str(byt:bytes, maxlen:int) -> str:
        """Convert a c-type char array to a python string: convert and concatenate the values until hit the null terminator"""
        result = ""
        if len(byt) == 1:
            return chr(byt[0])
        ct = 0
        limit = 1 if maxlen <= 0 else maxlen
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
    def cw_game_info_lookup(game_ptr, label):
        # lgr.info("\n cw_game_info_lookup():\n-------------------------")
        func = cwlib.cw_game_info_lookup
        func.restype = c_char_p
        func.argtypes = (POINTER(CWGame), c_char_p,)
        result = func(game_ptr, label)
        return result.decode(encoding = 'UTF-8')

    # void cw_game_write(CWGame *game, FILE *file)
    @staticmethod
    def cw_game_write(game_ptr, file_ptr):
        # lgr.info("\n cw_game_write():\n-------------------------")
        func = cwlib.cw_game_write
        func.restype = None
        func.argtypes = (POINTER(CWGame), ctypes.c_void_p,)
        return func(game_ptr, file_ptr)

    # CWGameIterator *cw_gameiter_create(CWGame *game)
    @staticmethod
    def cw_gameiter_create(game_ptr):
        # lgr.info("\n cw_gameiter_create():\n-------------------------")
        func = cwlib.cw_gameiter_create
        func.restype = POINTER(CWGameIterator)
        func.argtypes = (POINTER(CWGame),)
        return func(game_ptr)

    # CWBoxscore *cw_box_create(CWGame *game)
    @staticmethod
    def cw_box_create(game_ptr):
        # lgr.info("\n cw_box_create():\n-------------------------")
        func = cwlib.cw_box_create
        func.restype = POINTER(CWBoxscore)
        func.argtypes = (POINTER(CWGame),)
        return func(game_ptr)

    # CWRoster *cw_roster_create(char *team_id, int year, char *league, char *city, char *nickname)
    @staticmethod
    def cw_roster_create( team:str, year:int, league:str, city:str, nickname:str ):
        # self.lgr.info("\n try_roster_create():\n-------------------------")
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
    def cw_roster_read(roster_ptr, file_handle):
        # lgr.info("\n cw_roster_read():\n-------------------------")
        func = cwlib.cw_roster_read
        func.restype = c_int
        func.argtypes = (POINTER(CWRoster), ctypes.c_void_p,)
        return func(roster_ptr, file_handle)

    # CWPlayer *cw_roster_player_find(CWRoster *roster, char *player_id);
    @staticmethod
    def cw_roster_player_find(roster_ptr, player_id):
        # lgr.info("\n cw_roster_player_find():\n-------------------------")
        func = cwlib.cw_roster_player_find
        func.restype = POINTER(CWPlayer)
        func.argtypes = (POINTER(CWRoster), c_char_p,)
        return func(roster_ptr, player_id)

    # CWBoxPlayer *cw_box_get_starter(CWBoxscore *boxscore, int team, int slot)
    @staticmethod
    def cw_box_get_starter(box_ptr, team, slot):
        # lgr.info("\n cw_box_get_starter():\n-------------------------")
        func = cwlib.cw_box_get_starter
        func.restype = POINTER(CWBoxPlayer)
        func.argtypes = (POINTER(CWBoxscore), c_int, c_int,)
        return func(box_ptr, team, slot)

    # CWBoxPitcher *cw_box_get_starting_pitcher(CWBoxscore *boxscore, int team)
    @staticmethod
    def cw_box_get_starting_pitcher(box_ptr, team):
        # lgr.info("\n cw_box_get_starting_pitcher():\n-------------------------")
        func = cwlib.cw_box_get_starting_pitcher
        func.restype = POINTER(CWBoxPitcher)
        func.argtypes = (POINTER(CWBoxscore), c_int,)
        return func(box_ptr, team)
# END class MyCwlib


class MyChadwickTools:
    def __init__(self):
        self.lgr = logging
        self.lgr.info(F"Start {self.__class__.__name__}")

    # void cwbox_print_header(CWGame *game, CWRoster *visitors, CWRoster *home)
    def print_header( self, p_game:pointer, p_vis:pointer, p_home:pointer ):
        try:
            self.lgr.info("self.print_header():\n----------------------------------")

            dn_code = "?"
            day_night = MyCwlib.cw_game_info_lookup(p_game, b"daynight")
            if day_night:
                dn_code = "D" if day_night == "day" else "N" if day_night == "night" else day_night

            game_date = MyCwlib.cw_game_info_lookup(p_game, b"date")
            self.lgr.info(F"game date = {game_date}")
            year, month, day = game_date.split('/')
            # self.lgr.info(F"year, month, day = {year}, {month}, {day}")
            game_number = MyCwlib.cw_game_info_lookup(p_game, b"number")
            self.lgr.info(F"game_number = {game_number}")
            game_number_str = "" if game_number == "0" else F", game #{game_number}"

            vis_city = p_vis.contents.city
            vis_city_text = CwHelper.bytes_to_str(vis_city[:32],32)
            self.lgr.info(F"visitor = {vis_city_text}")

            home_city = p_home.contents.city
            home_city_text = CwHelper.bytes_to_str(home_city[:32],32)
            self.lgr.info(F"home = {home_city_text}")

            print(F"\nGame of {month}/{day}/{year}{game_number_str} -- {vis_city_text} @ {home_city_text} ({dn_code})")

        except Exception as tcph:
            self.lgr.info(F"self.print_header() Exception: {repr(tcph)}")
            raise tcph

    # void cwbox_print_linescore(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_linescore( self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer ):
        self.lgr.info("self.print_linescore():\n----------------------------------")

        linescore = p_box.contents.linescore
        # self.lgr.info(F"linescore = {linescore}")
        # self.lgr.info(F"len linescore = {len(linescore)}")

        for t in range(0,2):
            # self.lgr.info(F"\nt = {t}")
            runs = 0
            if t == 0:
                print(F"{CwHelper.bytes_to_str(p_vis.contents.city[:32],32):13}" if p_vis
                      else MyCwlib.cw_game_info_lookup(p_game, b"visteam"), end = '')
            else:
                print(F"{CwHelper.bytes_to_str(p_home.contents.city[:32],32):13}" if p_home
                      else MyCwlib.cw_game_info_lookup(p_game, b"hometeam"), end = '')

            for ix in range(1,10):
                # self.lgr.info(F"\nix = {ix}")
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
                print("  %d out%s when game ended.\n" % (outs_at_end, "" if outs_at_end == 1 else "s"))
            else:
                print("  %d out%s when winning run was scored.\n" % (outs_at_end, "" if outs_at_end == 1 else "s"))

    # void cwbox_print_text(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
    def print_text( self, p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer ):
        self.lgr.info("self.print_text():\n----------------------------------")

        note_count = 0 # int
        slots = [1, 1] # array int[2]
        players = list() # array CWBoxPlayer[2]
        # array int[2]
        ab = [0, 0]
        r  = [0, 0]
        h  = [0, 0]
        bi = [0, 0]

        player = MyCwlib.cw_box_get_starter(p_box, 0, 1)
        players.insert(0, player)
        players.insert(1, cwlib.cw_box_get_starter(p_box, 1, 1))

        self.print_header(p_game, p_vis, p_home)

        # self.lgr.info(F"type(p_vis.contents.city) = {type(p_vis.contents.city)}")
        vis_city = CwHelper.bytes_to_str(p_vis.contents.city[:32],32) if p_vis \
                   else MyCwlib.cw_game_info_lookup(p_game, b"visteam")
        home_city = CwHelper.bytes_to_str(p_home.contents.city[:32],32) if p_home \
                    else MyCwlib.cw_game_info_lookup(p_game, b"hometeam")

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
                    print("%-32s" % "", end = ''),
                print("     ", end = ''),
            print("")

        print( "%-20s -- -- -- -- %-24s -- -- -- --" % ("","") )

        if bi[0] == -1 or bi[1] == -1:
            print( "%-20s %2d %2d %2d    %-24s %2d %2d %2d   \n" % ("",ab[0],r[0],h[0],"",ab[1],r[1],h[1]) )
        else:
            print( "%-20s %2d %2d %2d %2d %-24s %2d %2d %2d %2d\n" % ("",ab[0],r[0],h[0],bi[0],"",ab[1],r[1],h[1],bi[1]) )
        print("\n")

        self.print_linescore(p_game, p_box, p_vis, p_home)
        print("")

        for t in range(0, 2):
            pitcher = MyCwlib.cw_box_get_starting_pitcher(p_box, t)
            # self.lgr.info(F"type(pitcher) = {type(pitcher)}")
            if t == 0:
                print("  %-18s   IP  H  R ER BB SO" % vis_city if p_vis else MyCwlib.cw_game_info_lookup(p_game, "visteam"))
            else:
                print("  %-18s   IP  H  R ER BB SO" % home_city if p_home else MyCwlib.cw_game_info_lookup(p_game, "hometeam"))
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
    def print_player( self, p_player:pointer, p_roster:pointer ):
        # self.lgr.info( "%s %s" % (str(p_player),str(p_team)) )
        self.lgr.info("self.print_player():\n----------------------------------")

        bio = None # CWPlayer * bio = NULL;
        # char name[256], posstr[256], outstr[256];
        posstr = ""

        # self.lgr.info(F"type(p_roster) = {type(p_roster)}")
        player = p_player.contents
        # self.lgr.info(F"type(player) = {type(player)}")
        if p_roster:
            bio = MyCwlib.cw_roster_player_find(p_roster, bytes(player.player_id)).contents

        # self.lgr.info(F"type(bio) = {type(bio)}")
        # self.lgr.info(F"type(bio.last_name) = {type(bio.last_name)}")
        # self.lgr.info(F"type(bio.first_name) = {type(bio.first_name)}")
        # self.lgr.info(F"type(bio.last_name[:20]) = {type(bio.last_name[:20])}")
        # self.lgr.info(F"type(bio.first_name[:1]) = {type(bio.first_name[:1])}")
        if bio:
            name = CwHelper.bytes_to_str(bio.last_name[:20],20) + " " + CwHelper.bytes_to_str(bio.first_name[:1],1)
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
        # self.lgr.info(F"type(batting) = {type(batting)}")
        if batting.bi != -1:
            print(F"{outstr:20} {batting.ab:2} {batting.r:2} {batting.h:2} {batting.bi:2}", end = '')
        else:
            print(F"{outstr:20} {batting.ab:2} {batting.r:2} {batting.h:2}", end = '')

    # cwbox_print_pitcher_apparatus(boxscore)
    def print_pitcher_apparatus( self, p_box ):
        self.lgr.info("self.print_pitcher_apparatus():\n----------------------------------")

    # void cwbox_print_pitcher(CWGame * game, CWBoxPitcher * pitcher, CWRoster * roster, int * note_count)
    def print_pitcher( self, p_game, p_pitcher, p_roster, note_count ):
        self.lgr.info("self.print_pitcher():\n----------------------------------")
        # Output one pitcher's pitching line. The parameter 'note_count' keeps track of how many apparatus notes
        # have been emitted (for pitchers who do not record an out in an inning)
        markers = ["*", "+", "#"]
        bio = None # CWPlayer *

        roster = p_roster.contents
        pitcher = p_pitcher.contents
        if roster:
            bio = MyCwlib.cw_roster_player_find(p_roster, bytes(pitcher.player_id)).contents

        if bio:
            name = CwHelper.bytes_to_str(bio.last_name[:20],20) + " " + CwHelper.bytes_to_str(bio.first_name[:1],1)
        else:
            name = pitcher.name
        self.lgr.info(F"pitcher name = {name}")

        game = p_game.contents
        # self.lgr.info(F"type(game) = {type(game)}")
        wp = MyCwlib.cw_game_info_lookup(game, b"wp")
        lp = MyCwlib.cw_game_info_lookup(game, b"lp")
        save = MyCwlib.cw_game_info_lookup(game, b"save")
        if wp and wp != pitcher.player_id:
            name += " (W)"
        elif lp and lp != pitcher.player_id:
            name += " (L)"
        elif save and save != pitcher.player_id:
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
            print(F" {pitching.h:2}", end = '')
        else:
            print("   ")

        if pitching.so != -1:
            print(F" {pitching.so:2}")
        else:
            print("   ")

    # cwbox_print_apparatus(game, boxscore, visitors, home)
    def print_apparatus( self, p_game, p_box, p_vis, p_home ):
        self.lgr.info("self.print_apparatus():\n----------------------------------")

# END class MyChadwickTools


def main_chadwick_py3():
    lgr = logging
    lgr.info(F"byteorder = {sys.byteorder}")
    try:
        # create and fill the visitor rosters
        vis_rosters = {}
        cal_roster = MyCwlib.cw_roster_create(CAL, 1996, "AL", "California", "Angels")
        vis_rosters[CAL] = cal_roster
        if not os.path.exists(roster_files[CAL]):
            raise FileNotFoundError(F"CANNOT find file {roster_files[CAL]}!")
        cal_fptr = chadwick.fopen( bytes(roster_files[CAL], "utf8") )
        cal_roster_read_result = MyCwlib.cw_roster_read(cal_roster, cal_fptr)
        lgr.info("CAL read result = " + ("Success." if cal_roster_read_result > 0 else "Failure!"))
        sea_roster = MyCwlib.cw_roster_create("SEA", 1996, "AL", "Seattle", "Mariners")
        vis_rosters[SEA] = sea_roster
        if not os.path.exists(roster_files[SEA]):
            raise FileNotFoundError(F"CANNOT find file {roster_files[SEA]}!")
        sea_fptr = chadwick.fopen( bytes(roster_files[SEA], "utf8") )
        sea_roster_read_result = MyCwlib.cw_roster_read(sea_roster, sea_fptr)
        lgr.info("SEA read result = " + ("Success." if sea_roster_read_result > 0 else "Failure!"))

        # create and fill the home roster
        home = MyCwlib.cw_roster_create("TOR", 1996, "AL", "Toronto", "Blue Jays")
        if not os.path.exists(tor_1996_roster):
            raise FileNotFoundError(f"cannot find file {tor_1996_roster}")
        home_fptr = chadwick.fopen( bytes(tor_1996_roster, "utf8") )
        home_roster_read_result = MyCwlib.cw_roster_read(home, home_fptr)
        lgr.info("HOME read result = " + ("Success." if home_roster_read_result > 0 else "Failure!"))

        cwtools = MyChadwickTools()
        count = 0
        limit = 6
        games = chadwick.games(tor_1996_events)
        for game in games:
            if game and count < limit:
                lgr.info("\tFound a game.")
                # self.lgr.info(F"game = {game}")
                lgr.info(F"game id = {game.contents.game_id}")

                box = MyCwlib.cw_box_create(game)
                # lgr.info(F"box = {box}")

                events = chadwick.process_game(game)
                results = tuple(events)
                away_team = results[count]['AWAY_TEAM_ID']
                # lgr.info(F"away team == {away_team}")
                visitor = vis_rosters[away_team]

                # cwtools.print_header(game, visitor, home)

                # cwtools.print_linescore(game, box, visitor, home)

                # try_game_write(game)

                # game_itr = cwlib.cw_gameiter_create(game)
                # self.lgr.info(F"type(game_itr) = {type(game_itr)}")
                # game_state = game_itr.contents.state
                # self.lgr.info(F"type(game_state) = {type(game_state)}")

                cwtools.print_text(game, box, visitor, home)

                count += 1
            # else:
            #     self.lgr.info("NO game.")
            # g_first = cwlib.cw_file_find_first_game(gfp)
            # if g_first:
            #     self.lgr.info("found the first game = %d" % g_first)
            #     self.lgr.info("type(g_first) = %s" % type(g_first))
            # else:
            #     self.lgr.info("NO first game.")
    except Exception as ex:
        lgr.warning(F"Exception: {repr(ex)}")


if __name__ == "__main__":
    logging.basicConfig(level = logging.CRITICAL)
    logging.info("main_chadwick_py3():\n----------------------------------")
    main_chadwick_py3()
    exit()
