# SC4052 - Assignment 1

## Run for Quick start (for personal use)
python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

python src/run.py --config configs/steady.json

# Instructions to fully run the code:
## Run all scenarios (per-scenario plots + metrics)
python src/run_all.py

## Find latest run folder
ls -t runs | head -n 1

## Then generate summary plots
python src/plot_summary.py --run runs/<LATEST_TIMESTAMP> --all

