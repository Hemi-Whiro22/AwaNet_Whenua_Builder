import subprocess
import sys


def main():
    subprocess.run([
        sys.executable,
        "-m",
        "te_hau.kitenga_whakairo.start_codex"
    ])


if __name__ == "__main__":
    main()
