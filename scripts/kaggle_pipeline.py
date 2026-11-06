"""Chạy tuần tự các task GPU trên Kaggle với giới hạn 2 phiên GPU: đợi, tải output, đẩy task kế tiếp (thử lại khi đầy).

  python scripts/kaggle_pipeline.py medcpt_feat bilstm      # đợi medcpt_feat (nếu đang chạy) rồi chạy bilstm
  python scripts/kaggle_pipeline.py --push crossenc         # đẩy mới rồi đợi
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kaggle_job as k  # noqa: E402


def push_retry(task, smoke=False, every=300, tries=48):
    for i in range(tries):
        try:
            k.push(task, smoke)
            return True
        except SystemExit as e:
            print(f"  đẩy {task} chưa được ({str(e)[-120:]}); thử lại sau {every}s", flush=True)
            time.sleep(every)
    return False


def run_task(task, push):
    if push and not push_retry(task):
        return "push_failed"
    time.sleep(60)
    s = k.wait(task, every=120)
    k.pull(task)
    print(f"== {task}: {s}", flush=True)
    return s


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("tasks", nargs="+")
    ap.add_argument("--push", action="store_true", help="đẩy cả task đầu tiên (mặc định: task đầu đang chạy sẵn)")
    a = ap.parse_args()
    for i, t in enumerate(a.tasks):
        s = run_task(t, push=a.push or i > 0)
        if s != "complete":
            print(f"Dừng: {t} kết thúc với trạng thái {s}", flush=True)
            sys.exit(1)
