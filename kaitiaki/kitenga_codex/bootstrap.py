import yaml
from mauri.te_kete.load_manifest import load_manifest


def bootstrap():
    manifest = load_manifest()
    print(
        f"🪶 Bootstrapping Assistant: {manifest['name']} ({manifest['assistant_id']})")

    # Example: validate tools or print config
    for tool in manifest["tools"]:
        print(f"🔧 Tool loaded: {tool}")

    # (Optional) Setup logic to init assistant with OpenAI API, Supabase, etc


if __name__ == "__main__":
    bootstrap()
