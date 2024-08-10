from mage_ai.settings.repo import get_repo_path
from mage_ai.io.bigquery import BigQuery
from mage_ai.io.config import ConfigFileLoader
from os import path
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def define_query(year):
    query = f'''WITH previous_games as 
(SELECT 
  team_id, 
  gametime, 
  game_id,
  LAG(three_points_pct) OVER team AS three_points_pct,
  LAG(three_points_att) OVER team AS three_points_att,
  LAG(two_points_pct) OVER team AS two_points_pct,
  LAG(two_points_att) OVER team AS two_points_att,
  LAG(offensive_rebounds) OVER team AS offensive_rebounds,
  LAG(defensive_rebounds) OVER team AS defensive_rebounds,
  LAG(turnovers) OVER team AS turnovers,
  LAG(steals) OVER team AS steals,
  LAG(blocks) OVER team AS blocks,
  LAG(personal_fouls) OVER team AS personal_fouls,
  LAG(points) OVER team AS points,
  LAG(gametime) OVER team AS gametime_lag,
  LAG(game_id) OVER team AS game_id_lag
  FROM bigquery-public-data.ncaa_basketball.mbb_teams_games_sr
  WHERE EXTRACT(year FROM gametime)={year} AND coverage='full'
  WINDOW team AS (PARTITION BY team_id ORDER BY gametime ASC))

SELECT
  games.game_id,
  pg_h.three_points_pct AS h_three_points_pct,
  pg_h.three_points_att AS h_three_points_att,
  pg_h.two_points_pct as h_two_points_pct,
  pg_h.two_points_att as h_two_points_att,
  pg_h.offensive_rebounds as h_offensive_rebounds,
  pg_h.defensive_rebounds as h_defensive_rebounds,
  pg_h.turnovers as h_turnovers,
  pg_h.steals as h_steals,
  pg_h.blocks as h_blocks,
  pg_h.personal_fouls as h_personal_fouls ,
  games.h_points as h_points,
  pg_a.three_points_pct as a_three_points_pct,
  pg_a.three_points_att as a_three_points_att,
  pg_a.two_points_pct as a_two_points_pct,
  pg_a.two_points_att as a_two_points_att,
  pg_a.offensive_rebounds as a_offensive_rebounds,
  pg_a.defensive_rebounds as a_defensive_rebounds,
  pg_a.turnovers as a_turnovers,
  pg_a.steals as a_steals,
  pg_a.blocks as a_blocks,
  pg_a.personal_fouls as a_personal_fouls,
  games.a_points as a_points
 
FROM
  bigquery-public-data.ncaa_basketball.mbb_games_sr games
  JOIN previous_games pg_h ON games.h_id=pg_h.team_id AND games.game_id=pg_h.game_id
  JOIN previous_games pg_a ON games.a_id=pg_a.team_id AND games.game_id=pg_a.game_id

WHERE
  EXTRACT(year
  FROM games.gametime)={year}
  AND pg_h.game_id_lag IS NOT NULL
  AND pg_a.game_id_lag IS NOT NULL'''
    return query
@data_loader
def load_data_from_big_query(*args, **kwargs):
    print('start')
    """
    Template for loading data from a BigQuery warehouse.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#bigquery
    """
    train_year = kwargs.get('train_year')
    if train_year is None:
        train_year = 2013
    val_year = kwargs.get('val_year')
    if val_year is None:
        val_year = 2014
    use_dv = kwargs.get('use_dv')
    if use_dv is None:
        use_dv = 0

    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    query=define_query(train_year)
    train_data=BigQuery.with_config(ConfigFileLoader(config_path, config_profile)).load(query)
    query=define_query(val_year)
    val_data=BigQuery.with_config(ConfigFileLoader(config_path, config_profile)).load(query)
    return [train_data, val_data, train_year, val_year, use_dv]


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
