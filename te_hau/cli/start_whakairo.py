import subprocess


def main():
    subprocess.run([
        "mcp",
        "serve",
        "--manifest",
        "te_hau/whakairo_codex/mcp/manifest.yaml"
    ])


if __name__ == "__main__":
    main()
""""""
