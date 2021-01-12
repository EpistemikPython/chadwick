from pychadwick.box import CWBoxPlayer
from pychadwick.chadwick import *
from pychadwick.roster import CWPlayer

chadwick = Chadwick()
cwlib = chadwick.libchadwick

positions = [
  "", "p", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf", "dh", "ph", "pr"
]

#  2021-01-08: runs with Python3.8.5
######################################


def my_check_for_file(file_path:str):
    if not os.path.exists(file_path):
        print(F"CANNOT find file {file_path}: try to create.")
        try:
            open(file_path, "w+").close()
        except Exception as cfe:
            raise OSError(F"CANNOT create file {file_path}: {repr(cfe)}")


# char * cw_game_info_lookup(CWGame * game, char * label)
def my_game_info_lookup(game_ptr, label):
    # print("\n my_game_info_lookup():\n-------------------------")
    func = cwlib.cw_game_info_lookup
    func.restype = c_char_p
    func.argtypes = ( POINTER(CWGame), c_char_p, )
    result = func(game_ptr, label)
    return result.decode(encoding='UTF-8')


# void cw_game_write(CWGame *game, FILE *file)
def my_game_write(game_ptr, file_ptr):
    print("\n my_game_write():\n-------------------------")
    func = cwlib.cw_game_write
    func.restype = None
    func.argtypes = ( POINTER(CWGame), ctypes.c_void_p, )
    return func(game_ptr, file_ptr)


# CWGameIterator *cw_gameiter_create(CWGame *game)
def my_gameiter_create(game_ptr):
    print("\n my_gameiter_create():\n-------------------------")
    func = cwlib.cw_gameiter_create
    func.restype = POINTER(CWGameIterator)
    func.argtypes = ( POINTER(CWGame), )
    return func(game_ptr)


# CWBoxscore *cw_box_create(CWGame *game)
def my_box_create(game_ptr):
    print("\n my_box_create():\n-------------------------")
    func = cwlib.cw_box_create
    func.restype = POINTER(CWBoxscore)
    func.argtypes = ( POINTER(CWGame), )
    return func(game_ptr)


# int cw_roster_read(CWRoster *roster, FILE *file)
def my_roster_read(roster_ptr, file_handle):
    # print("\n my_roster_read():\n-------------------------")
    func = cwlib.cw_roster_read
    func.restype = c_int
    func.argtypes = ( POINTER(CWRoster), ctypes.c_void_p, )
    return func(roster_ptr, file_handle)


# CWPlayer *cw_roster_player_find(CWRoster *roster, char *player_id);
def my_roster_player_find(roster_ptr, player_id):
    # print("\n my_roster_player_find():\n-------------------------")
    func = cwlib.cw_roster_player_find
    func.restype = POINTER(CWPlayer)
    func.argtypes = ( POINTER(CWRoster), c_char_p, )
    return func(roster_ptr, player_id)


# CWBoxPlayer *cw_box_get_starter(CWBoxscore *boxscore, int team, int slot)
def my_get_starter(box_ptr, team, slot):
    # print("\n my_get_starter():\n-------------------------")
    func = cwlib.cw_box_get_starter
    func.restype = POINTER(CWBoxPlayer)
    func.argtypes = ( POINTER(CWBoxscore), c_int, c_int, )
    return func(box_ptr, team, slot)


def try_game_write(game):
    print("\n try_game_write():\n-------------------------")
    cal_at_tor = "cal_at_tor_1996-001.txt"
    if not os.path.exists(cal_at_tor):
        raise FileNotFoundError(F"CANNOT find file {cal_at_tor}!")
    caltor_file_path = bytes(cal_at_tor, "utf8")
    print(F"type(caltor_file_path) = {type(caltor_file_path)}")
    caltor_fptr = chadwick.fopen(caltor_file_path)
    print(F"type(caltor_fptr) = {type(caltor_fptr)}")
    my_game_write(game, caltor_fptr) # NO output: and seems to be writing to inappropriate locations...


# void cwbox_print_header(CWGame *game, CWRoster *visitors, CWRoster *home)
def try_cwbox_print_header(p_game:pointer, p_vis:pointer, p_home:pointer):
    try:
        print("\n try_cwbox_print_header():\n-------------------------")

        dn_code = "?"
        day_night = my_game_info_lookup(p_game, b"daynight")
        # print(F"day_night = {day_night}")
        if day_night:
            dn_code = "D" if day_night == "day" else "N" if day_night == "night" else day_night
        # print(F"dn_code = {dn_code}")

        game_date = my_game_info_lookup(p_game, b"date")
        print(F"game date = {game_date}")
        year, month, day = game_date.split('/')
        # print(F"year, month, day = {year}, {month}, {day}")
        game_number = my_game_info_lookup(p_game, b"number")
        print(F"game_number = {game_number}")
        game_number_str = "" if game_number == "0" else F", game #{game_number}"

        vis_city = p_vis.contents.city
        vis_city_text = bytes_to_str(vis_city[:32])
        print(F"visitor = {vis_city_text}")

        home_city = p_home.contents.city
        home_city_text = bytes_to_str(home_city[:32])
        print(F"home = {home_city_text}")

        print(F"\nGame of {month}/{day}/{year}{game_number_str} -- {vis_city_text} @ {home_city_text} ({dn_code})")

    except Exception as tcph:
        print(F"try_cwbox_print_header() Exception: {repr(tcph)}")
        raise tcph


# void cwbox_print_linescore(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
def try_cwbox_print_linescore(p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer):
    print("\n try_cwbox_print_linescore():\n----------------------------")

    linescore = p_box.contents.linescore
    # print(F"linescore = {linescore}")
    # print(F"len linescore = {len(linescore)}")

    for t in range(0,2):
        # print(F"\nt = {t}")
        runs = 0
        if t == 0:
            print(F"{bytes_to_str(p_vis.contents.city[:32]):13}" if p_vis
                  else my_game_info_lookup(p_game, "visteam"), end = '')
        else:
            print(F"{bytes_to_str(p_home.contents.city[:32]):13}" if p_home
                  else my_game_info_lookup(p_game, "hometeam"), end = '')

        for ix in range(1,10):
            # print(F"\nix = {ix}")
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
def try_cwbox_print_text(p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer):
    print("\n try_cwbox_print_text():\n----------------------------")

    note_count = 0 # int
    slots = [1, 1] # array int[2]
    players = list() # array CWBoxPlayer[2]
    # array int[2]
    ab = [0, 0]
    r  = [0, 0]
    h  = [0, 0]
    bi = [0, 0]

    player = my_get_starter(p_box, 0, 1)
    print(F"type(player) = {type(player)}")
    players.insert(0, player)
    print(F"players[0] = {players[0]}")
    players.insert(1, cwlib.cw_box_get_starter(p_box, 1, 1))
    print(F"players[1] = {players[1]}")

    try_cwbox_print_header(p_game, p_vis, p_home)

    print(F"type(p_vis.contents.city) = {type(p_vis.contents.city)}")
    vis_city = bytes_to_str(p_vis.contents.city[:32]) if p_vis else my_game_info_lookup(p_game, "visteam")
    home_city = bytes_to_str(p_home.contents.city[:32]) if p_home else my_game_info_lookup(p_game, "hometeam")

    print(F"{vis_city} AB  R  H RBI    {home_city} AB  R  H RBI    ")

    while slots[0] <= 9 or slots[1] <= 9 :
        for t in range(0,2):
            if slots[t] <= 9:
                try_cwbox_print_player(players[t], p_vis if (t == 0) else p_home)
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
                print("%-32s" % ""),
            print(" "),
        print("")

    print( "%-20s -- -- -- -- %-22s -- -- -- --\n" % ("","") )

    if bi[0] == -1 or bi[1] == -1:
        print( "%-20s %2d %2d %2d    %-22s %2d %2d %2d   \n" % ("",ab[0],r[0],h[0],"",ab[1],r[1],h[1]) )
    else:
        print( "%-20s %2d %2d %2d %2d %-22s %2d %2d %2d %2d\n" % ("",ab[0],r[0],h[0],bi[0],"",ab[1],r[1],h[1],bi[1]) )
    print("\n")

    try_cwbox_print_linescore(p_game, p_box, p_vis, p_home)
    print("")

    for t in range(0, 2):
        pitcher = cwlib.cw_box_get_starting_pitcher(p_box, t) # CWBoxPitcher
        if t == 0:
            print("  %-18s   IP  H  R ER BB SO" % vis_city if p_vis else cwlib.cw_game_info_lookup(p_game, "visteam"))
        else:
            print("  %-18s   IP  H  R ER BB SO" % home_city if p_home else cwlib.cw_game_info_lookup(p_game, "hometeam"))
        while pitcher:
            try_cwbox_print_pitcher(p_game, pitcher, (p_vis if (t == 0) else p_home), note_count)
            pitcher = pitcher.next
        if t == 0:
            print("")

    try_cwbox_print_pitcher_apparatus(p_box)
    print("")

    try_cwbox_print_apparatus(p_game, p_box, p_vis, p_home)
    print("\f")


# void cwbox_print_player(CWBoxPlayer *player, CWRoster *roster)
def try_cwbox_print_player( p_player:pointer, p_roster:pointer ):
    # print( "%s %s" % (str(p_player),str(p_team)) )
    print("\n try_cwbox_print_player():\n----------------------------")

    bio = None # CWPlayer * bio = NULL;
    # char name[256], posstr[256], outstr[256];
    posstr = ""

    print(F"type(p_roster) = {type(p_roster)}")
    player = p_player.contents
    print(F"type(player) = {type(player)}")
    if p_roster:
        bio = my_roster_player_find(p_roster, bytes(player.player_id)).contents

    print(F"type(bio) = {type(bio)}")
    print(F"type(bio.last_name) = {type(bio.last_name)}")
    print(F"type(bio.first_name) = {type(bio.first_name)}")
    print(F"type(bio.last_name[:20]) = {type(bio.last_name[:20])}")
    print(F"type(bio.first_name[:1]) = {type(bio.first_name[:1])}")
    if bio:
        name = bytes_to_str(bio.last_name[:20]) + " " + bytes_to_str(bio.first_name[:1])
    else:
        name = player.name
    print(F"name = {name}")

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
    print(F"outstr = {outstr}")

    batting = player.battiing.contents
    print(F"type(batting) = {type(batting)}")
    if batting.bi != -1:
        print(F"{outstr:20} {batting.ab:2} {batting.r:2} {batting.h:2} {batting.bi:2}")
    else:
        print(F"{outstr:20} {batting.ab:2} {batting.r:2} {batting.h:2}")


# CWRoster *cw_roster_create(char *team_id, int year, char *league, char *city, char *nickname)
def try_roster_create(team:str, year:int, league:str, city:str, nickname:str):
    # print("\n try_roster_create():\n-------------------------")
    team = bytes(team, "utf8")
    league = bytes(league, "utf8")
    city = bytes(city, "utf8")
    nickname = bytes(nickname, "utf8")

    my_roster_create = cwlib.cw_roster_create
    my_roster_create.restype = POINTER(CWRoster)
    my_roster_create.argtypes = (c_char_p, c_int, c_char_p, c_char_p, c_char_p,)

    return my_roster_create(team, year, league, city, nickname)


# cwbox_print_pitcher_apparatus(boxscore)
def try_cwbox_print_pitcher_apparatus(p_box):
    print("\n try_cwbox_print_pitcher_apparatus():\n-------------------------")


# cwbox_print_pitcher(game, pitcher, (visitors if (t == 0) else home), note_count)
def try_cwbox_print_pitcher(p_game, p_pitcher, p_team, p_note):
    print("\n try_cwbox_print_pitcher():\n-------------------------")


# cwbox_print_apparatus(game, boxscore, visitors, home)
def try_cwbox_print_apparatus(p_game, p_box, p_vis, p_home):
    print("\n try_cwbox_print_apparatus():\n-------------------------")


tor_1996_events = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/event/regular/1996TOR.EVA"
tor_1996_roster = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/TOR1996.ROS"

CAL = "CAL"
SEA = "SEA"
roster_files = {
    CAL : "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/CAL1996.ROS" ,
    SEA : "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/SEA1996.ROS"
}


def main_chadwick_py3():
    print("\n main_chadwick_py3():\n-------------------------")
    # print(F"byteorder = {sys.byteorder}")
    try:
        # create and fill the visitor rosters
        vis_rosters = {}
        cal_roster = try_roster_create(CAL, 1996, "AL", "California", "Angels")
        vis_rosters[CAL] = cal_roster
        if not os.path.exists(roster_files[CAL]):
            raise FileNotFoundError(F"CANNOT find file {roster_files[CAL]}!")
        cal_fptr = chadwick.fopen( bytes(roster_files[CAL], "utf8") )
        cal_roster_read_result = my_roster_read(cal_roster, cal_fptr)
        print("CAL read result = " + ("Success." if cal_roster_read_result > 0 else "Failure!"))
        sea_roster = try_roster_create("SEA", 1996, "AL", "Seattle", "Mariners")
        vis_rosters[SEA] = sea_roster
        if not os.path.exists(roster_files[SEA]):
            raise FileNotFoundError(F"CANNOT find file {roster_files[SEA]}!")
        sea_fptr = chadwick.fopen( bytes(roster_files[SEA], "utf8") )
        sea_roster_read_result = my_roster_read(sea_roster, sea_fptr)
        print("SEA read result = " + ("Success." if sea_roster_read_result > 0 else "Failure!"))

        # create and fill the home roster
        home = try_roster_create("TOR", 1996, "AL", "Toronto", "Blue Jays")
        if not os.path.exists(tor_1996_roster):
            raise FileNotFoundError(f"cannot find file {tor_1996_roster}")
        home_fptr = chadwick.fopen( bytes(tor_1996_roster, "utf8") )
        home_roster_read_result = my_roster_read(home, home_fptr)
        print("HOME read result = " + ("Success." if home_roster_read_result > 0 else "Failure!"))

        count = 0
        limit = 6
        games = chadwick.games(tor_1996_events)
        for game in games:
            if game and count < limit:
                print("\n\nFound a game.")
                # print(F"game = {game}")
                print(F"game id = {game.contents.game_id}")

                box = my_box_create(game)
                # print(F"box = {box}")

                events = chadwick.process_game(game)
                results = tuple(events)
                # for event in results[:5]:
                #     print(F"event: GAME ID = {event['GAME_ID']}; AWAY TEAM = {event['AWAY_TEAM_ID']}")
                away_team = results[count]['AWAY_TEAM_ID']
                print(F"away team == {away_team}")
                visitor = vis_rosters[away_team]

                try_cwbox_print_header(game, visitor, home)

                try_cwbox_print_linescore(game, box, visitor, home)

                # try_game_write(game)

                # game_itr = cwlib.cw_gameiter_create(game)
                # print(F"type(game_itr) = {type(game_itr)}")
                # game_state = game_itr.contents.state
                # print(F"type(game_state) = {type(game_state)}")

                try_cwbox_print_text(game, box, visitor, home)

                count += 1
            # else:
            #     print("NO game.")
            # g_first = cwlib.cw_file_find_first_game(gfp)
            # if g_first:
            #     print("found the first game = %d" % g_first)
            #     print("type(g_first) = %s" % type(g_first))
            # else:
            #     print("NO first game.")
    except Exception as ex:
        print(F"Exception: {repr(ex)}")


def bytes_to_str(byt:bytes) -> str:
    """Convert a c-type char array to a python string:
        convert and concatenate the values until hit the null terminator"""
    print("\n bytes_to_str():\n----------------------")
    print(F"byt = {byt}")
    print(F"type(byt) = {type(byt)}")
    result = ""
    if len(byt) == 1:
        return chr(byt[0])
    for b in byt:
        # print(F"b = {b}")
        # print(F"type(b) = {type(b)}")
        if b == 0:
            value = result.strip()
            print(F"bytes_to_str():value = {value}")
            return value
        result += chr(b)


if __name__ == "__main__":
    main_chadwick_py3()
    exit()
