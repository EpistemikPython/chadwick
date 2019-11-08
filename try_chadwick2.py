import sys
from chadwick.libchadwick import *

# void cwbox_print_text(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
def cwbox_print_text(game, boxscore, visitors, home):
    t = note_count = 0 # int
    slots = [1, 1] # array int[2]
    players = [0, 0] # array CWBoxPlayer[2]
    # array int[2]
    ab = [0, 0]
    r  = [0, 0]
    h  = [0, 0]
    bi = [0, 0]

    players[0] = cw_box_get_starter(boxscore, 0, 1);
    players[1] = cw_box_get_starter(boxscore, 1, 1);

    cwbox_print_header(game, visitors, home);

    printf("  %-18s AB  R  H RBI    %-18s AB  R  H RBI\n",
     (visitors) ? visitors->city : cw_game_info_lookup(game, "visteam"),
     (home) ? home->city : cw_game_info_lookup(game, "hometeam"));

    while (slots[0] <= 9 || slots[1] <= 9) {
    for (t = 0; t <= 1; t++) {
      if (slots[t] <= 9) {
    cwbox_print_player(players[t], (t == 0) ? visitors : home);
    ab[t] += players[t]->batting->ab;
    r[t] += players[t]->batting->r;
    h[t] += players[t]->batting->h;
    if (players[t]->batting->bi != -1) {
      bi[t] += players[t]->batting->bi;
    }
    else {
      bi[t] = -1;
    }
    players[t] = players[t]->next;
    if (players[t] == NULL) {
      /* In some National Association games, teams played with 8
       * players.  This generalization allows for printing
       * boxscores when some batting slots are empty.
       */
      while (slots[t] <= 9 && players[t] == NULL) {
        slots[t]++;
        if (slots[t] <= 9) {
          players[t] = cw_box_get_starter(boxscore, t, slots[t]);
        }
      }
    }
      }
      else {
    printf("%-32s", "");
      }

      printf("   ");
    }
    printf("\n");
    }

    printf("%-20s -- -- -- -- %-22s -- -- -- --\n", "", "");

    if (bi[0] == -1 || bi[1] == -1) {
    printf("%-20s %2d %2d %2d    %-22s %2d %2d %2d   \n",
       "", ab[0], r[0], h[0], "", ab[1], r[1], h[1]);
    }
    else {
    printf("%-20s %2d %2d %2d %2d %-22s %2d %2d %2d %2d\n",
       "", ab[0], r[0], h[0], bi[0], "", ab[1], r[1], h[1], bi[1]);
    }
    printf("\n");

    cwbox_print_linescore(game, boxscore, visitors, home);

    printf("\n");

    for (t = 0; t <= 1; t++) {
    CWBoxPitcher *pitcher = cw_box_get_starting_pitcher(boxscore, t);
    if (t == 0) {
      printf("  %-18s   IP  H  R ER BB SO\n",
         (visitors) ? visitors->city : cw_game_info_lookup(game, "visteam"));
    }
    else {
      printf("  %-18s   IP  H  R ER BB SO\n",
         (home) ? home->city : cw_game_info_lookup(game, "hometeam"));
    }
    while (pitcher != NULL) {
      cwbox_print_pitcher(game, pitcher, (t == 0) ? visitors : home,
              &note_count);
      pitcher = pitcher->next;
    }
    if (t == 0) {
      printf("\n");
    }
    }
    cwbox_print_pitcher_apparatus(boxscore);
    printf("\n");

    cwbox_print_apparatus(game, boxscore, visitors, home);

    printf("\f");


# print(sys.path)
tor_1996 = "/home/marksa/dev/git/fork/ChadwickBureau/retrosheet/event/regular/1996TOR.EVA"
try:
    with open(tor_1996, "r") as fp:
        print("type(fp) = %s" % type(fp))
        g1 = read_game(fp)
        if g1:
            print("found a game.")
            print("type(g1) = %s" % type(g1))
            print("g1 = %s" % g1)
            away, home = g1.teams
            print("away = %s, home = %s" % (away,home))
            cw_game_write(g1, sys.stdout)
            print("innings = %s" % g1._get_innings())
            g1_b = cw_box_create(g1)
            print("type(g1_b) = %s" % type(g1_b))
            # print("boxscore = %s" % g1._get_boxscore())
            for event in g1.events:
                pass # print("event = %s" % repr(event))
            g2 = read_game(fp)
            print("g2 = %s" % g2)
        else:
            print("NO game.")
        g_f = cw_file_find_first_game(fp)
        if g_f:
            print("found the first game = %d" % g_f)
            print("type(g_f) = %s" % type(g_f))
        else:
            print("NO first game.")
except Exception as e:
    print("Exception: %s" % str(e))
