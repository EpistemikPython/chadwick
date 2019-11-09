import sys
from chadwick.libchadwick import *


positions = [
  "", "p", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf", "dh", "ph", "pr"
]


# void cwbox_print_header(CWGame *game, CWRoster *visitors, CWRoster *home)
def cwbox_print_header(p_game, p_vis, p_home):
    # print( "%s %s %s" % (str(p_game),str(p_vis),str(p_home)) )
    dn_code = "?"
    day_night = cw_game_info_lookup(p_game, "daynight")
    if day_night:
        dn_code = "D" if day_night == "day" else "N" if day_night == "night" else day_night

    year, month, day = cw_game_info_lookup(p_game, "date").split('/')
    game_number = cw_game_info_lookup(p_game, "number")
    game_number_str = "" if game_number == "0" else ", game %s".format(game_number)
    print("     Game of %s/%s/%s%s -- %s at %s (%s)\n" % ( month, day, year, game_number_str,
                p_vis.city if p_vis else cw_game_info_lookup(p_game, "visteam"),
                p_home.city if p_home else cw_game_info_lookup(p_game, "hometeam"),
                dn_code ))
    print("\n")


# void cwbox_print_player(CWBoxPlayer *player, CWRoster *roster)
def cwbox_print_player(p_player, p_roster):
    # print("type(p_player) = {}".format(type(p_player)))
    # print("type(p_roster) = {}".format(type(p_roster)))
    # print( "%s %s" % (str(p_player),str(p_team)) )
    bio = None # CWPlayer *
    name = p_player.name
    if p_roster:
        bio = cw_roster_player_find(p_roster, p_player.player_id)
        # print("found roster")
    if bio:
        name = bio.last_name + bio.first_name[0]
        # print("found bio")
    # print("name = {}".format(name))

    posn_str = ""
    # print("p_player.positions = {}".format(repr(p_player.positions)))
    # print("type(p_player.positions) = {}".format(type(p_player.positions)))
    # print("p_player._get_position(0) = {}".format(p_player._get_position(0)))
    # print("p_player.positions[0] = {}".format(p_player.positions[0]))
    if p_player.ph_inn > 0 and p_player._get_position(0) != 11:
        posn_str = "ph"
    elif p_player.pr_inn > 0 and p_player._get_position(0) != 12:
        posn_str = "pr"
    # print("posn_str = {}".format(posn_str))

    # print("positions = {}".format(positions))
    # print("positions[5] = {}".format(positions[5]))
    # print("p_player.num_positions = {}".format(p_player.num_positions))
    for pos in range(0, p_player.num_positions):
        # print("pos = {}".format(str(pos)))
        if len(posn_str) > 0:
            posn_str += "-"
            # print("new posn_str = {}".format(posn_str))
        posn_str += positions[p_player._get_position(pos)]
    # print("new posn_str = {}".format(posn_str))

    posn_str_len = len(posn_str)
    # print("posn_str_len = {}".format(posn_str_len))
    if len(posn_str) <= 10:
        if len(posn_str) + len(name) > 18:
            out_str = name[0:(18 - posn_str_len)] + ", "
        else:
            out_str = name + ", "
        out_str += posn_str
    else:
        # When there are a lot of positions, can't do much sensibly...
        out_str = name + ", " + positions[p_player._get_position(0)] + ",..."
    # print("out_str = {}".format(out_str))

    if p_player.batting.bi != -1:
        print("%-20s %2d %2d %2d %2d" % (out_str, p_player.batting.ab, p_player.batting.r, p_player.batting.h, p_player.batting.bi)),
    else:
        print("%-20s %2d %2d %2d   " % (out_str, p_player.batting.ab, p_player.batting.r, p_player.batting.h)),


# cwbox_print_linescore(game, boxscore, visitors, home)
def cwbox_print_linescore(p_game, p_box, p_vis, p_home):
    print( "%s %s %s %s" % (str(p_game),str(p_box),str(p_vis),str(p_home)) )


# cwbox_print_pitcher_apparatus(boxscore)
def cwbox_print_pitcher_apparatus(p_box):
    print( "%s" % (str(p_box)) )


# cwbox_print_pitcher(game, pitcher, (visitors if (t == 0) else home), note_count)
def cwbox_print_pitcher(p_game, p_pitcher, p_team, p_note):
    print( "%s %s %s %s" % (str(p_game),str(p_pitcher),str(p_team),str(p_note)) )


# cwbox_print_apparatus(game, boxscore, visitors, home)
def cwbox_print_apparatus(p_game, p_box, p_vis, p_home):
    print( "%s %s %s %s" % (str(p_game),str(p_box),str(p_vis),str(p_home)) )


# void cwbox_print_text(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
def cwbox_print_text(p_game, p_box, p_vis, p_home):
    print( "cwbox_print_text(%s, %s, %s, %s)" % (str(p_game),str(p_box),str(p_vis),str(p_home)) )
    note_count = 0 # int
    slots = [1, 1] # array int[2]
    players = list() # array CWBoxPlayer[2]
    # array int[2]
    ab = [0, 0]
    r  = [0, 0]
    h  = [0, 0]
    bi = [0, 0]

    players.insert(0, cw_box_get_starter(p_box, 0, 1))
    players.insert(1, cw_box_get_starter(p_box, 1, 1))

    cwbox_print_header(p_game, p_vis, p_home)

    print("  %-18s AB  R  H RBI    %-18s AB  R  H RBI\n" %
          (p_vis.city if p_vis else cw_game_info_lookup(p_game, "visteam"),
           p_home.city if p_home else cw_game_info_lookup(p_game, "hometeam")) )

    while slots[0] <= 9 or slots[1] <= 9 :
        for t in range(0,2):
            if slots[t] <= 9:
                cwbox_print_player(players[t], p_vis if (t == 0) else p_home)
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
                            players[t] = cw_box_get_starter(p_box, t, slots[t])
            else:
                print("%-32s" % ""),
            print(" "),
        print("\n")

    print( "%-20s -- -- -- -- %-22s -- -- -- --\n" % ("","") )

    if bi[0] == -1 or bi[1] == -1:
        print( "%-20s %2d %2d %2d    %-22s %2d %2d %2d   \n" % ("",ab[0],r[0],h[0],"",ab[1],r[1],h[1]) )
    else:
        print( "%-20s %2d %2d %2d %2d %-22s %2d %2d %2d %2d\n" % ("",ab[0],r[0],h[0],bi[0],"",ab[1],r[1],h[1],bi[1]) )
    print("\n")

    cwbox_print_linescore(p_game, p_box, p_vis, p_home)

    print("\n")

    for t in range(0, 2):
        pitcher = cw_box_get_starting_pitcher(p_box, t) # CWBoxPitcher
        if t == 0:
            print("  %-18s   IP  H  R ER BB SO\n" % p_vis.city if p_vis else cw_game_info_lookup(p_game, "visteam"))
        else:
            print("  %-18s   IP  H  R ER BB SO\n" % p_home.city if p_home else cw_game_info_lookup(p_game, "hometeam"))
        while pitcher:
            cwbox_print_pitcher(p_game, pitcher, (p_vis if (t == 0) else p_home), note_count)
            pitcher = pitcher.next
        if t == 0:
            print("\n")

    cwbox_print_pitcher_apparatus(p_box)
    print("\n")

    cwbox_print_apparatus(p_game, p_box, p_vis, p_home)
    print("\f")


# print(sys.path)
tor_1996_events = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/event/regular/1996TOR.EVA"
tor_1996_roster = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/TOR1996.ROS"
cal_1996_roster = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/rosters/CAL1996.ROS"
try:
    with open(tor_1996_events, "r") as gfp:
        print("type(gfp) = %s" % type(gfp))
        g1 = read_game(gfp)
        if g1:
            print("found a game.")
            print("type(g1) = %s" % type(g1))
            print("g1 = %s" % g1)
            away, at_home = g1.teams
            print("away = %s, home = %s" % (away,at_home))
            visitor = cw_roster_create('CAL', 1996, 'AL', 'California', 'Angels')
            with open(cal_1996_roster, "r") as rcfp:
                cw_roster_read(visitor, rcfp)
            print("type(visitor) = %s" % type(visitor))
            home = cw_roster_create('TOR', 1996, 'AL', 'Toronto', 'Blue Jays')
            with open(tor_1996_roster, "r") as rtfp:
                cw_roster_read(home, rtfp)
            print("type(home) = %s" % type(home))
            # cw_game_write(g1, sys.stdout)
            print("innings = %s" % g1.innings)
            g1_b = cw_box_create(g1)
            print("type(g1_b) = %s" % type(g1_b))
            # print("boxscore = %s" % g1._get_boxscore())
            cwbox_print_text(g1, g1_b, visitor, home)
            for event in g1.events:
                pass # print("event = %s" % repr(event))
            g2 = read_game(gfp)
            print("g2 = %s" % g2)
        else:
            print("NO game.")
        g_first = cw_file_find_first_game(gfp)
        if g_first:
            print("found the first game = %d" % g_first)
            print("type(g_first) = %s" % type(g_first))
        else:
            print("NO first game.")
except Exception as e:
    print("Exception: %s" % str(e))

exit()
