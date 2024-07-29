import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from dotabet import utils, filter, features, fetch, make_csv, cleanup, groupby, league, cumsum, transform, plot, checkout, vizual, train
from dotabet.consistency import main

input_files = [r"D:\WORKSPACE\dotabet\data" + fp for fp in [r"\1pro_games_2.json", r"\1pro_games_1.json"]]  
pro_games_json_path = r"D:\WORKSPACE\dotabet\data\top_teams\1pro_games.json"
all_player_csv_path = r"D:\WORKSPACE\dotabet\data\top_teams\all_players.csv"
all_player_clean_csv_path = r"D:\WORKSPACE\dotabet\data\top_teams\all_players_clean.csv"
features_csv_path = r"D:\WORKSPACE\dotabet\data\top_teams\features.csv"
teams_csv_path = r"D:\WORKSPACE\dotabet\constants\teams.csv"

train_path = r"D:\WORKSPACE\dotabet\data\train\matches.csv"