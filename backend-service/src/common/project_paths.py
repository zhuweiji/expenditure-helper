from pathlib import Path

src_root_dir = Path(__file__).parent.parent
project_root_dir = src_root_dir.parent

local_db_filepath = project_root_dir / "dev.db"

directories = [
    data_dir := project_root_dir / "data",
    cc_statement_dir := data_dir / "statements",
]

for dir in directories:
    dir.mkdir(parents=True, exist_ok=True)
