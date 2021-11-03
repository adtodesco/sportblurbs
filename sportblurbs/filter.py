def filter_nfl_at_least_one_att(boxscore, player, player_boxscore):
    return (
        player_boxscore.attempted_passes
        or player_boxscore.rush_attempts
        or player_boxscore.receptions
        or player_boxscore.field_goals_attempted
    )
