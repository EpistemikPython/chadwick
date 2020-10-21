
from pychadwick.chadwick import *
# from pychadwick.box import CWBoxscore

chadwick = Chadwick()
cwlib = chadwick.libchadwick

positions = [
  "", "p", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf", "dh", "ph", "pr"
]


# void cwbox_print_header(CWGame *game, CWRoster *visitors, CWRoster *home)
def try_cwbox_print_header(p_game, p_vis, str_vis_city, p_home, str_home_city):
    try:
        # print( "%s %s %s" % (str(p_game),str(p_vis),str(p_home)) )

        # char * cw_game_info_lookup(CWGame * game, char * label);
        my_game_info_lookup = cwlib.cw_game_info_lookup
        my_game_info_lookup.restype = c_char_p
        my_game_info_lookup.argtypes = (POINTER(CWGame), c_char_p,)

        dn_code = "?"
        day_night = my_game_info_lookup(p_game, b"daynight").decode(encoding='UTF-8')
        print(F"day_night = {day_night}")
        if day_night:
            dn_code = "D" if day_night == "day" else "N" if day_night == "night" else day_night
        print(F"dn_code = {dn_code}")

        result = my_game_info_lookup(p_game, b"date").decode(encoding='UTF-8')
        print(F"result = {result}")
        print(F"type(result) = {type(result)}")
        year, month, day = result.split('/')
        print(F"year, month, day = {year}, {month}, {day}")
        game_number = my_game_info_lookup(p_game, b"number").decode(encoding='UTF-8')
        print(F"game_number = {game_number}")
        game_number_str = "" if game_number == "0" else F", game {game_number}"
        print(F"game_number_str = {game_number_str}")
        vis_roster = p_vis.contents
        print(F"type(vis_roster) = {type(vis_roster)}")
        # vis_city = vis_roster.city.contents
        # vis_city = (c_char * 32).from_address(vis_roster.city)
        vis_city = vis_roster.city[:len(str_vis_city)].decode(encoding='UTF-8').strip()
        print(F"type(vis_city) = {type(vis_city)}")
        print(F"vis_city = {vis_city}")
        home_roster = p_home.contents
        print(F"type(home_roster) = {type(home_roster)}")
        home_city = home_roster.city[:len(str_home_city)].decode(encoding='UTF-8').strip()
        print(F"Game of {month}/{day}/{year}{game_number_str} -- {vis_city} @ {home_city} ({dn_code})\n")
                # -- {vis_roster.city if vis_roster else my_game_info_lookup(p_game, b'visteam')} \
                # at {home_roster.city if home_roster else my_game_info_lookup(p_game, b'hometeam')} \
                # ({dn_code})" )
    except Exception as tcph:
        print(F"try_cwbox_print_header() Exception: {repr(tcph)}")
        raise tcph


# void cwbox_print_player(CWBoxPlayer *player, CWRoster *roster)
def try_cwbox_print_player(p_player, p_roster):
    # print( "%s %s" % (str(p_player),str(p_team)) )
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


# void cwbox_print_linescore(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
def try_cwbox_print_linescore(p_game, p_box, p_vis, p_home):
    # print( "%s %s %s %s" % (str(p_game),str(p_box),str(p_vis),str(p_home)) )
    i = 0
    for t in range(0,2):
        runs = 0
        if t == 0:
            print("%-17s" % p_vis.city if p_vis else cwlib.cw_game_info_lookup(p_game, "visteam"))
        else:
            print("%-17s" % p_home.city if p_home else cwlib.cw_game_info_lookup(p_game, "hometeam"))
        for i in range(1,50):
            linescore = p_box.linescore
            print("linescore = {}".format(str(linescore)))

            def swig_to_str(p_base, p_form):
                base = int(p_base)
                ty = ctypes.c_ubyte * 1

                # for x in itertools.count():
                v = ty.from_address(base + i)[0]
                if not v: return
                p_form.append(v)
                return v

            score_list = list()
            swig_to_str(linescore, score_list)
            print("score_list = {}".format(score_list))

            def swig_to_byte(b):
                ty = ctypes.c_ubyte*1
                print("ty = %s" % ty)
                b_int = int(b)
                print("b_int = 0x%x" % b_int)
                v = ty.from_address(b_int)
                print("v = {}".format(v))
                # v2 = ty.from_address(v)
                return v

            byte_score = swig_to_byte(linescore)
            print("byte_score = {}".format(str(byte_score)))
            print("byte_score[0] = {}".format(str(byte_score[0])))
            # print("byte_score[1] = {}".format(str(byte_score[1])))

            score = linescore[i]
            print("score = {}".format(score))
            if score[0] < 0 and p_box.linescore[i][1] < 0:
                break
            if p_box.linescore[i][t] >= 10:
                print("(%d)" % p_box.linescore[i][t])
                runs += p_box.linescore[i][t]
            elif p_box.linescore[i][t] >= 0:
                print("%d" % p_box.linescore[i][t])
                runs += p_box.linescore[i][t]
            else:
                print("x")

            if i % 3 == 0:
                print(" ")

        if (i - 1) % 3 != 0:
            print(" ")

        print("-- %2d\n" % runs)

    if p_box.outs_at_end != 3:
        if not p_box.walk_off:
            print("  %d out%s when game ended.\n" % (p_box.outs_at_end, "" if p_box.outs_at_end == 1 else "s"))
        else:
            print("  %d out%s when winning run was scored.\n" % (p_box.outs_at_end, "" if p_box.outs_at_end == 1 else "s"))


# cwbox_print_pitcher_apparatus(boxscore)
def try_cwbox_print_pitcher_apparatus(p_box):
    print( "%s" % (str(p_box)) )


# cwbox_print_pitcher(game, pitcher, (visitors if (t == 0) else home), note_count)
def try_cwbox_print_pitcher(p_game, p_pitcher, p_team, p_note):
    print( "%s %s %s %s" % (str(p_game),str(p_pitcher),str(p_team),str(p_note)) )


# cwbox_print_apparatus(game, boxscore, visitors, home)
def try_cwbox_print_apparatus(p_game, p_box, p_vis, p_home):
    print( "%s %s %s %s" % (str(p_game),str(p_box),str(p_vis),str(p_home)) )


# void cwbox_print_text(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
def try_cwbox_print_text(p_game, p_box, p_vis, p_home):
    # print( "cwbox_print_text(%s, %s, %s, %s)" % (str(p_game),str(p_box),str(p_vis),str(p_home)) )
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


# CWGameIterator *cw_gameiter_create(CWGame *game);
def try_gameiter_create(game_ptr):
    func = cwlib.cw_gameiter_create
    func.restype = POINTER(CWGameIterator)
    func.argtypes = (POINTER(CWGame),)
    return func(game_ptr)


# CWBoxscore *cw_box_create(CWGame *game);
def try_box_create(game_ptr):
    func = cwlib.cw_box_create
    func.restype = POINTER(CWBoxscore)
    func.argtypes = (POINTER(CWGame),)
    return func(game_ptr)


def try_roster_create(team:str, year:int, league:str, city:str, nickname:str):
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
    func = cwlib.cw_roster_read
    func.restype = c_int
    func.argtypes = (POINTER(CWRoster),ctypes.c_void_p,)
    return func(roster_ptr,file_handle)


# print(sys.path)
tor_1996_events = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/event/regular/1996TOR.EVA"
tor_1996_roster = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/TOR1996.ROS"
cal_1996_roster = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/CAL1996.ROS"


def try_chadwick_py3_main():
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

                box = chadwick.cw_box_create(game)
                print(F"type(box) = {type(box)}")
                print(box)

                events = chadwick.process_game(game)
                for event in events:
                    print(event)

                count += 1

                # away, at_home = g1.teams
                # print("away = %s, home = %s" % (away,at_home))

                visitor = try_roster_create("CAL", 1996, 'AL', 'California', 'Angels')
                print(F"type(visitor) = {type(visitor)}")
                if not os.path.exists(cal_1996_roster):
                    raise FileNotFoundError(f"cannot find file {cal_1996_roster}")
                vis_file_path = bytes(cal_1996_roster, "utf8")
                print(F"type(vis_file_path) = {type(vis_file_path)}")
                vis_fptr = chadwick.fopen(vis_file_path)
                print(F"type(visitor) = {type(visitor)}")
                print(F"type(vis_fptr) = {type(vis_fptr)}")
                result = try_roster_read(visitor, vis_fptr)
                print(f"visitor result = {result}")

                home = try_roster_create('TOR', 1996, 'AL', 'Toronto', 'Blue Jays')
                print(F"type(home) = {type(home)}")
                if not os.path.exists(tor_1996_roster):
                    raise FileNotFoundError(f"cannot find file {tor_1996_roster}")
                home_file_path = bytes(tor_1996_roster, "utf8")
                print(F"type(home_file_path) = {type(home_file_path)}")
                home_fptr = chadwick.fopen(home_file_path)
                result = try_roster_read(home, home_fptr)
                print(f"home result = {result}")

                try_cwbox_print_header(game, visitor, 'California', home, 'Toronto')

                # # cw_game_write(g1, sys.stdout)
                #
                # print(F"innings = {g1.innings}")
                #
                # g1_it = cwlib.cw_gameiter_create(g1)
                # print(F"type(g1_it) = {type(g1_it)}")
                # print(F"g1_it.totals[1].lob = {g1_it.totals[1].lob}")
                #
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


if __name__ == "__main__":
    try_chadwick_py3_main()
    exit()
