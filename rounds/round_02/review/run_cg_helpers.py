"""Referee launcher: run ChatGPT round 2 helper scripts unchanged, with their code folder on sys.path."""
import os, runpy, sys, traceback

CODE = r"F:\masters\ai_benchmark_results\rounds\round_02\chatgpt\code"
OUT = r"C:\Users\HP\AppData\Local\Temp\claude\cde6940f32f894ca\0e465b7c-021e-4af2-b911-e3c8cd6a0ac8\scratchpad\cg2_rerun"
TRAIN = r"F:\masters\ai_benchmark\data\train"
sys.path.insert(0, CODE)
os.environ["OPENBLAS_NUM_THREADS"] = "1"; os.environ["OMP_NUM_THREADS"] = "1"
for name, extra in (("controls", ["--permutations", "200"]), ("stress", []), ("domain_shift", []), ("postprocess", [])):
    path = os.path.join(CODE, name + ".py")
    sys.argv = [path, "--train-dir", TRAIN, "--out-dir", OUT] + extra
    try:
        runpy.run_path(path, run_name="__main__")
        print("OK", name, flush=True)
    except SystemExit as e:
        print("EXIT", name, e.code, flush=True)
    except Exception:
        print("FAIL", name, flush=True); traceback.print_exc()
