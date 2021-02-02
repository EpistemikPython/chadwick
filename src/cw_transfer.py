# Output the count of double plays by team
# void cwbox_print_double_play(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
def print_double_plays(self, p_game, p_box, p_vis, p_home):
    if (boxscore.dp[0] == 0 and boxscore.dp[1] == 0)
        return

    print("DP -- ")
    if (boxscore.dp[0] > 0 and boxscore.dp[1] == 0) 
        print("%s %d\n", (visitors) ? visitors.city : cw_game_info_lookup(game, "visteam"), boxscore.dp[0])

    elif (boxscore.dp[0] == 0 and boxscore.dp[1] > 0) 
        print("%s %d\n", (home) ? home.city : cw_game_info_lookup(game, "hometeam"), boxscore.dp[1])

    else:
        print("%s %d, %s %d\n", (visitors) ? visitors.city : cw_game_info_lookup(game, "visteam"), boxscore.dp[0],
               (home) ? home.city : cw_game_info_lookup(game, "hometeam"), boxscore.dp[1])

# Output the count of triple plays by team
# void cwbox_print_triple_play(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
def print_triple_plays(self, p_game, p_box, p_vis, p_home)
    if (boxscore.tp[0] == 0 and boxscore.tp[1] == 0) 
        return

    print("TP -- ")
    if (boxscore.tp[0] > 0 and boxscore.tp[1] == 0) 
        print("%s %d\n", (visitors) ? visitors.city : cw_game_info_lookup(game, "visteam"), boxscore.tp[0])
  
    elif (boxscore.tp[0] == 0 and boxscore.tp[1] > 0) 
        print("%s %d\n", (home) ? home.city : cw_game_info_lookup(game, "hometeam"), boxscore.tp[1])
  
    else:
        print("%s %d, %s %d\n", (visitors) ? visitors.city : cw_game_info_lookup(game, "visteam"), boxscore.tp[0], 
              (home) ? home.city : cw_game_info_lookup(game, "hometeam"), boxscore.tp[1])

# Output the number of runners left on base
# void cwbox_print_lob(CWGame *game, CWBoxscore *boxscore, CWRoster *visitors, CWRoster *home)
def print_lob(self, p_game, p_box, p_vis, p_home)
    if (boxscore.lob[0] == 0 and boxscore.lob[1] == 0)
        return

    printf("LOB -- %s %d, %s %d\n", (visitors) ? visitors.city : cw_game_info_lookup(game, "visteam"), boxscore.lob[0],
	         (home) ? home.city : cw_game_info_lookup(game, "hometeam"), boxscore.lob[1])


print(F"04 > 03 = {'04' > '03'}")
print(F"04 == 04 = {'04' == '04'}")
print(F"04 == 05 = {'04' == '05'}")
print(F"04 > 05 = {'04' > '05'}")
print(F"10 > 07 = {'10' > '07'}")
print(F"13 <= 13 = {'13' <= '13'}")
print(F"17 >= 13 = {'17' >= '13'}")
print(F"27 <= 30 = {'27' <= '30'}")


# void cwbox_print_hbp_apparatus(CWGame *game, CWBoxEvent *list,  CWRoster *visitors, CWRoster *home) 
def print_hbp(self, p_game, p_box, p_vis, p_home)
    CWBoxEvent *event = p_box
    comma = 0
    if (p_box == NULL):
        return
    
    print("HBP -- ")
    while event:
        search_event = event
        batter = None
        pitcher = None
        batter_name = ""
        pitcher_name = ""
        count = 0
        if event.mark > 0:
            event = event.next
            continue
        
        while search_event:
            if event.players[0] == search_event.players[0] and event.players[1] == search_event.players[1]:
                count += 1
                search_event.mark = 1
            search_event = search_event.next
        
        if visitors: batter = cw_roster_player_find(visitors, event.players[0])
        
        if not batter and home: batter = cw_roster_player_find(home, event.players[0])
        
        if not batter: batter_name = cwbox_game_find_name(game, event.players[0])

        if visitors: pitcher = cw_roster_player_find(visitors, event.players[1])
        
        if not pitcher and home: pitcher = cw_roster_player_find(home, event.players[1])
        
        if not pitcher: pitcher_name = cwbox_game_find_name(game, event.players[1])

        if comma: print(", ")
        
        if count == 1:
            if pitcher:
                print("by %s %c ", pitcher.last_name, pitcher.first_name[0])
            elif pitcher_name:
                print("by %s ", pitcher_name)
            else:
                print("by %s ", event.players[1])
            
            if batter:
                print("(%s %c)", batter.last_name, batter.first_name[0])
            elif batter_name:
                print("(%s)", batter_name)
            else:
                print("(%s)", event.players[0]);
        else:
            if pitcher:
                print("by %s %c ", pitcher.last_name, pitcher.first_name[0])
            elif pitcher_name:
                print("by %s ", pitcher_name)
            else:
                print("by %s ", event.players[1])
            
            if batter:
                print("(%s %c)", batter.last_name, batter.first_name[0])
            elif batter_name:
                print("(%s)", batter_name)
            else
                print("(%s)", event.players[0])
            
            print(" %d", count)
        
        comma = 1
    
    print("")
    event = p_box
    while event:
        event.mark = 0
        event = event.next


if count == 1:
    if pitcher:
        print(F"by {LP_c_char_to_str(pitcher.contents.last_name)} {pitcher.contents.first_name[0].decode('UTF8')} ")
    else:
        print(F"by {pitcher_name if pitcher_name else LP_c_char_to_str(event.contents.players[1])} ")
    if batter:
        print(F"({batter.contents.last_name} {batter.contents.first_name[0].decode('UTF8')})")
    else:
        print(F"({batter_name if batter_name else LP_c_char_to_str(event.contents.players[0])})")
else:
    if pitcher:
        print(F"by {LP_c_char_to_str(pitcher.contents.last_name)} {pitcher.contents.first_name[0].decode('UTF8')} ")
    else:
        print(F"by {pitcher_name} ") if pitcher_name else print(F"by {event.contents.players[1]} ")
    if batter:
        print(F"({batter.contents.last_name} {batter.contents.first_name[0].decode('UTF8')})")
    else:
        print(F"({batter_name})") if batter_name else print(F"({event.contents.players[0]})")
    print(" %d", count)

