import sys
# from pychadwick.box import CWBoxscore
from pychadwick.chadwick import *

chadwick = Chadwick()
cwlib = chadwick.libchadwick

positions = [
  "", "p", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf", "dh", "ph", "pr"
]

#  2021-01-08: runs with Python3.8.5
######################################


# char * cw_game_info_lookup(CWGame * game, char * label);
def my_game_info_lookup(game_ptr, label):
    print("\n my_game_info_lookup():\n-------------------------")
    func = cwlib.cw_game_info_lookup
    func.restype = c_char_p
    func.argtypes = (POINTER(CWGame), c_char_p,)
    result = func(game_ptr, label)
    return result.decode(encoding='UTF-8')


# void cwbox_print_header(CWGame *game, CWRoster *visitors, CWRoster *home)
def try_cwbox_print_header(p_game:pointer, p_vis:pointer, p_home:pointer):
    try:
        # print( "%s %s %s" % (str(p_game),str(p_vis),str(p_home)) )
        print("\n try_cwbox_print_header():\n-------------------------")

        dn_code = "?"
        day_night = my_game_info_lookup(p_game, b"daynight")
        print(F"\nday_night = {day_night}")
        if day_night:
            dn_code = "D" if day_night == "day" else "N" if day_night == "night" else day_night
        print(F"dn_code = {dn_code}")

        result = my_game_info_lookup(p_game, b"date")
        print(F"result = {result}")
        print(F"type(result) = {type(result)}")
        year, month, day = result.split('/')
        print(F"year, month, day = {year}, {month}, {day}")
        game_number = my_game_info_lookup(p_game, b"number")
        print(F"game_number = {game_number}")
        game_number_str = "" if game_number == "0" else F", game {game_number}"
        print(F"game_number_str = {game_number_str}")

        vis_roster = p_vis.contents
        print(F"\ntype(vis_roster) = {type(vis_roster)}")
        vis_city = vis_roster.city
        print(F"type(vis_city) = {type(vis_city)}")
        print(F"vis_city = {vis_city}")
        vis_city_contents = vis_city.contents
        print(F"type(vis_city_contents) = {type(vis_city_contents)}")
        print(F"vis_city_contents = {vis_city_contents}")

        vis_city_32 = vis_city[:32]
        print(F"type(vis_city_32) = {type(vis_city_32)}")
        print(F"vis_city_32 = {vis_city_32}")
        vis_city_text = bytes_to_str(vis_city_32)
        print(F"type(vis_city_text) = {type(vis_city_text)}")
        print(F"vis_city_text = {vis_city_text}")

        # vis_city_decoded = vis_city_32.decode(encoding='UTF-8').strip()
        # print(F"type(vis_city_decoded) = {type(vis_city_decoded)}")
        # print(F"vis_city_decoded = {vis_city_decoded}")

        home_roster = p_home.contents
        print(F"\ntype(home_roster) = {type(home_roster)}")
        home_city = home_roster.city
        home_city_32 = home_city[:32]
        home_city_text = bytes_to_str(home_city_32)

        print(F"Game of {month}/{day}/{year}{game_number_str} -- {vis_city_text} @ {home_city_text} ({dn_code})\n")

    except Exception as tcph:
        print(F"try_cwbox_print_header() Exception: {repr(tcph)}")
        raise tcph


# void cwbox_print_linescore(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
def try_cwbox_print_linescore(p_game:pointer, p_box:pointer, p_vis:pointer, p_home:pointer):
    # print( "%s %s %s %s" % (str(p_game),str(p_box),str(p_vis),str(p_home)) )
    print("\n try_cwbox_print_linescore():\n----------------------------")

    linescore = p_box.contents.linescore
    print(F"linescore = {linescore}")
    # linescore = < pychadwick.box.c_int_Array_2_Array_50 object at 0x7fde1fa69840 >
    print(F"len linescore = {len(linescore)}")
    # len linescore = 50

    tuple_ls = tuple(linescore)
    print(F"tuple linescore = {tuple_ls}")
    itx = tuple_ls[0]
    print(F"type(itx) = {type(itx)}")
    print(F"len itx = {len(itx)}")
    print(F"itx = {itx}")
    print(F"itx[0] = {itx[0]}")
    print(F"itx[1] = {itx[1]}")
    for item in tuple_ls:
        print(F"{item[0]}, {item[1]}")

    for t in range(0,2):
        print(F"\nt = {t}")
        runs = 0
        if t == 0:
            print("%-17s" % bytes_to_str(p_vis.contents.city[:32]) if p_vis else my_game_info_lookup(p_game, "visteam"))
        else:
            print("%-17s" % bytes_to_str(p_home.contents.city[:32]) if p_home else my_game_info_lookup(p_game, "hometeam"))

        for ix in range(0,12):
            print(F"\ni = {ix}")
            score = linescore[ix]
            print(F"linescore[{ix},{t}] = {linescore[ix][t]}")
            # print(F"score = {score}")
            print(F"score[{t}] = {score[t]}")
            # print(F"score[1] = {score[1]}")
            # if score[0] < 0:
            #     continue
            if linescore[ix][t] >= 10:
                print(F"({linescore[ix][t]})")
                runs += linescore[ix][t]
            elif linescore[ix][t] >= 0:
                print(F"{linescore[ix][t]}")
                runs += linescore[ix][t]
            else:
                print("x")

            if ix % 3 == 0:
                print(" ")

            if (ix - 1) % 3 != 0:
                print(" ")

            print("-- %2d\n" % runs)

    outs_at_end = p_box.contents.outs_at_end
    if outs_at_end != 3:
        if not p_box.contents.walk_off:
            print("  %d out%s when game ended.\n" % (outs_at_end, "" if outs_at_end == 1 else "s"))
        else:
            print("  %d out%s when winning run was scored.\n" % (outs_at_end, "" if outs_at_end == 1 else "s"))


# void cwbox_print_text(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
def try_cwbox_print_text(p_game, p_box, p_vis, p_home):
    # print( "cwbox_print_text(%s, %s, %s, %s)" % (str(p_game),str(p_box),str(p_vis),str(p_home)) )
    print("\n try_cwbox_print_text():\n----------------------------")

    note_count = 0 # int
    slots = [1, 1] # array int[2]
    players = list() # array CWBoxPlayer[2]
    # array int[2]
    ab = [0, 0]
    r  = [0, 0]
    h  = [0, 0]
    bi = [0, 0]

    players.insert(0, cwlib.cw_box_get_starter(p_box, 0, 1))
    players.insert(1, cwlib.cw_box_get_starter(p_box, 1, 1))

    try_cwbox_print_header(p_game, p_vis, p_home)

    print("  %-18s AB  R  H RBI    %-18s AB  R  H RBI" %
          (p_vis.city if p_vis else cwlib.cw_game_info_lookup(p_game, "visteam"),
           p_home.city if p_home else cwlib.cw_game_info_lookup(p_game, "hometeam")) )

    while slots[0] <= 9 or slots[1] <= 9 :
        for t in range(0,2):
            if slots[t] <= 9:
                try_cwbox_print_player(players[t], p_vis if (t == 0) else p_home)
                ab[t] += players[t].batting.ab
                r[t]  += players[t].batting.r
                h[t]  += players[t].batting.h
                if players[t].batting.bi != -1:
                    bi[t] += players[t].batting.bi
                else:
                    bi[t] = -1
                players[t] = players[t].next
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
            print("  %-18s   IP  H  R ER BB SO" % p_vis.city if p_vis else cwlib.cw_game_info_lookup(p_game, "visteam"))
        else:
            print("  %-18s   IP  H  R ER BB SO" % p_home.city if p_home else cwlib.cw_game_info_lookup(p_game, "hometeam"))
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
def try_cwbox_print_player(p_player, p_roster):
    # print( "%s %s" % (str(p_player),str(p_team)) )
    print("\n try_cwbox_print_player():\n----------------------------")

    bio = None # CWPlayer *
    name = p_player.name
    if p_roster:
        bio = cwlib.cw_roster_player_find(p_roster, p_player.player_id)
    if bio:
        name = bio.last_name + bio.first_name[0]

    posn_str = ""
    if p_player.ph_inn > 0 and p_player._get_position(0) != 11:
        posn_str = "ph"
    elif p_player.pr_inn > 0 and p_player._get_position(0) != 12:
        posn_str = "pr"

    for pos in range(0, p_player.num_positions):
        if len(posn_str) > 0:
            posn_str += "-"
        posn_str += positions[p_player._get_position(pos)]

    posn_str_len = len(posn_str)
    if len(posn_str) <= 10:
        if len(posn_str) + len(name) > 18:
            out_str = name[0:(18 - posn_str_len)] + ", "
        else:
            out_str = name + ", "
        out_str += posn_str
    else:
        # When there are a lot of positions, can't do much sensibly...
        out_str = name + ", " + positions[p_player._get_position(0)] + ",..."

    if p_player.batting.bi != -1:
        print("%-20s %2d %2d %2d %2d" % (out_str, p_player.batting.ab, p_player.batting.r, p_player.batting.h, p_player.batting.bi)),
    else:
        print("%-20s %2d %2d %2d   " % (out_str, p_player.batting.ab, p_player.batting.r, p_player.batting.h)),


# cwbox_print_pitcher_apparatus(boxscore)
def try_cwbox_print_pitcher_apparatus(p_box):
    print( "%s" % (str(p_box)) )
    print("\n try_cwbox_print_pitcher_apparatus():\n-------------------------")


# cwbox_print_pitcher(game, pitcher, (visitors if (t == 0) else home), note_count)
def try_cwbox_print_pitcher(p_game, p_pitcher, p_team, p_note):
    print( "%s %s %s %s" % (str(p_game),str(p_pitcher),str(p_team),str(p_note)) )
    print("\n try_cwbox_print_pitcher():\n-------------------------")


# cwbox_print_apparatus(game, boxscore, visitors, home)
def try_cwbox_print_apparatus(p_game, p_box, p_vis, p_home):
    print( "%s %s %s %s" % (str(p_game),str(p_box),str(p_vis),str(p_home)) )
    print("\n try_cwbox_print_apparatus():\n-------------------------")


# CWGameIterator *cw_gameiter_create(CWGame *game);
def try_gameiter_create(game_ptr):
    print("\n try_gameiter_create():\n-------------------------")
    func = cwlib.cw_gameiter_create
    func.restype = POINTER(CWGameIterator)
    func.argtypes = (POINTER(CWGame),)
    return func(game_ptr)


# CWBoxscore *cw_box_create(CWGame *game);
def try_box_create(game_ptr):
    print("\n try_box_create():\n-------------------------")
    func = cwlib.cw_box_create
    func.restype = POINTER(CWBoxscore)
    func.argtypes = (POINTER(CWGame),)
    return func(game_ptr)


def try_roster_create(team:str, year:int, league:str, city:str, nickname:str):
    print("\n try_roster_create():\n-------------------------")
    team = bytes(team, "utf8")
    league = bytes(league, "utf8")
    city = bytes(city, "utf8")
    nickname = bytes(nickname, "utf8")

    # CWRoster *cw_roster_create(char *team_id, int year, char *league, char *city, char *nickname);
    my_roster_create = cwlib.cw_roster_create
    my_roster_create.restype = POINTER(CWRoster)
    my_roster_create.argtypes = (c_char_p, c_int, c_char_p, c_char_p, c_char_p,)

    return my_roster_create(team, year, league, city, nickname)


# int cw_roster_read(CWRoster *roster, FILE *file);
def try_roster_read(roster_ptr, file_handle):
    print("\n try_roster_read():\n-------------------------")
    func = cwlib.cw_roster_read
    func.restype = c_int
    func.argtypes = (POINTER(CWRoster),ctypes.c_void_p,)
    return func(roster_ptr,file_handle)


tor_1996_events = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/event/regular/1996TOR.EVA"
tor_1996_roster = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/TOR1996.ROS"
cal_1996_roster = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/CAL1996.ROS"


def try_chadwick_py3_main():
    print("\n try_chadwick_py3_main():\n-------------------------")
    print(F"byteorder = {sys.byteorder}")
    try:
        count = 0
        limit = 1
        games = chadwick.games(tor_1996_events)
        for game in games:
            if game and count < limit:
                print("found a game.")
                print(F"type(game) = {type(game)}")
                print(F"game = {game}")

                df = chadwick.game_to_dataframe(game)
                print(F"type(df) = {type(df)}")
                print(df)

                box = try_box_create(game)
                print(F"type(box) = {type(box)}")
                print(box)

                events = chadwick.process_game(game)
                results = tuple(events)
                for event in results[:5]:
                    print(event)

                count += 1

                # away, at_home = g1.teams
                # print("away = %s, home = %s" % (away,at_home))

                visitor = try_roster_create("CAL", 1996, 'AL', 'California', 'Angels')
                print(F"\ntype(visitor) = {type(visitor)}")
                if not os.path.exists(cal_1996_roster):
                    raise FileNotFoundError(f"cannot find file {cal_1996_roster}")
                vis_file_path = bytes(cal_1996_roster, "utf8")
                print(F"type(vis_file_path) = {type(vis_file_path)}")
                vis_fptr = chadwick.fopen(vis_file_path)
                print(F"type(vis_fptr) = {type(vis_fptr)}")
                result = try_roster_read(visitor, vis_fptr)
                print(f"visitor result = {result}")

                home = try_roster_create('TOR', 1996, 'AL', 'Toronto', 'Blue Jays')
                print(F"\ntype(home) = {type(home)}")
                if not os.path.exists(tor_1996_roster):
                    raise FileNotFoundError(f"cannot find file {tor_1996_roster}")
                home_file_path = bytes(tor_1996_roster, "utf8")
                print(F"type(home_file_path) = {type(home_file_path)}")
                home_fptr = chadwick.fopen(home_file_path)
                result = try_roster_read(home, home_fptr)
                print(f"home result = {result}")

                try_cwbox_print_header(game, visitor, home)

                try_cwbox_print_linescore(game, box, visitor, home)

                # cw_game_write(g1, sys.stdout)

                # print(F"innings = {g1.innings}")

                # g1_it = cwlib.cw_gameiter_create(g1)
                # print(F"type(g1_it) = {type(g1_it)}")
                # print(F"g1_it.totals[1].lob = {g1_it.totals[1].lob}")

                # g1_b = cwlib.cw_box_create(g1)
                # print(F"type(g1_b) = {type(g1_b)}")
                # # print("boxscore = %s" % g1._get_boxscore())
                # cwbox_print_text(g1, g1_b, visitor, home)

                # for event in game.events:
                #     pass # print("event = %s" % repr(event))

                # g2 = cwlib.read_game(gfp)
                # print("g2 = %s" % g2)
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


def bytes_to_str(byt:bytes):
    """Convert a c-type char array to a python string:
        convert and concatenate the values until hit the null terminator"""
    # print("\n bytes_to_str():\n----------------------")
    # print(F"byt = {byt}")
    # print(F"type(byt) = {type(byt)}")
    result = ""
    for b in byt:
        # print(F"b = {b}")
        # print(F"type(b) = {type(b)}")
        if b == 0:
            value = result.strip()
            print(F"bytes_to_str():value = {value}")
            return value
        result += chr(b)


if __name__ == "__main__":
    try_chadwick_py3_main()
    exit()
