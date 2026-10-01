"""Score peak windows for every candidate span; output data/work/windows.parquet."""
import glob
from concurrent.futures import ProcessPoolExecutor
import polars as pl
import detect
from peaks import peak_windows

def init():
    global RARE
    RARE = detect.load_rare()

def work(path):
    c = pl.read_parquet("data/work/candidates.parquet")
    df = pl.read_parquet(path, columns=["tcp_id", "text"])
    c = c.filter(pl.col("tcp_id").is_in(df["tcp_id"].implode()))
    texts = dict(df.iter_rows())
    out = []
    for r in c.iter_rows(named=True):
        t = texts[r["tcp_id"]]
        for ws, cnt in peak_windows(t, RARE, r["char_start"], r["char_end"]):
            out.append(dict(tcp_id=r["tcp_id"], span_start=r["char_start"], win_start=ws, events=cnt,
                            span_score=r["score"], n_cue=r["n_cue"]))
    return out

if __name__ == "__main__":
    rows = []
    with ProcessPoolExecutor(12, initializer=init) as ex:
        for r in ex.map(work, sorted(glob.glob("data/raw/eebo/data/*.parquet"))):
            rows.extend(r)
    w = pl.DataFrame(rows).unique(["tcp_id", "win_start"])
    w.write_parquet("data/work/windows.parquet")
    print(w.height, "windows")
