try:
    from kaitiaki.kitenga_codex.bootstrap import bootstrap as kitenga_bootstrap
except ImportError:  # Template used without kaitiaki module available
    kitenga_bootstrap = None


def bootstrap():
    """Initialize assistant + tool metadata for a mini realm."""
    if kitenga_bootstrap is None:
        print("[mini_te_po] te_po package not found; skipping Kitenga bootstrap.")
        return
    kitenga_bootstrap()


if __name__ == "__main__":
    bootstrap()
