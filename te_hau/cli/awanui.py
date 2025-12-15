#!/usr/bin/env python3
"""
Te Hau — Realm & Project Generator for AwaOS

The command-line brain of AwaOS. Orchestrates realm creation, deployment,
pipeline management, and kaitiaki tooling.

Usage:
    tehau new <realm_name>           Create a new realm
    tehau deploy <realm_name>        Deploy realm to cloud
    tehau seal <realm_name>          Seal realm mauri
    tehau evolve <realm> <stage>     Evolve kaitiaki stage
    tehau pipeline run <realm> <p>   Run pipeline
    tehau context switch <realm>     Switch active context
    tehau kaitiaki chat <name>       Chat with a kaitiaki
    tehau infra plan <realm>         Plan infrastructure
    tehau heal diagnose <realm>      Diagnose realm health
    tehau cluster status             Show cluster status
"""

import click
from pathlib import Path

from te_hau.verbs.new import cmd_new
from te_hau.verbs.deploy import cmd_deploy
from te_hau.verbs.seal import cmd_seal, cmd_unseal
from te_hau.verbs.evolve import cmd_evolve
from te_hau.verbs.pipeline import cmd_pipeline, cmd_pipelines_list
from te_hau.verbs.context import cmd_context
from te_hau.verbs.glyph import cmd_glyph, cmd_glyph_inherit
from te_hau.verbs.init import cmd_init
from te_hau.verbs.kaitiaki import cmd_kaitiaki, cmd_kaitiaki_list
from te_hau.verbs.translate import cmd_translate
from te_hau.verbs.security import cmd_security
from te_hau.verbs.branch import cmd_branch
from te_hau.verbs.awa import cmd_awa
from te_hau.verbs.infra import cmd_infra
from te_hau.verbs.heal import cmd_heal
from te_hau.verbs.cluster import cmd_cluster


@click.group()
@click.version_option(version="0.1.0", prog_name="Te Hau")
def cli():
    """Te Hau – Realm & Project Generator for AwaOS.
    
    A sovereign developer operating system for cultural compute.
    """
    pass


# Register all command groups
cli.add_command(cmd_init, "init")
cli.add_command(cmd_new, "new")
cli.add_command(cmd_deploy, "deploy")
cli.add_command(cmd_seal, "seal")
cli.add_command(cmd_unseal, "unseal")
cli.add_command(cmd_evolve, "evolve")
cli.add_command(cmd_pipeline, "pipeline")
cli.add_command(cmd_pipelines_list, "pipelines")
cli.add_command(cmd_context, "context")
cli.add_command(cmd_glyph, "glyph")
cli.add_command(cmd_glyph_inherit, "glyph-inherit")
cli.add_command(cmd_kaitiaki, "kaitiaki")
cli.add_command(cmd_kaitiaki_list, "kaitiaki-list")
cli.add_command(cmd_translate, "translate")
cli.add_command(cmd_security, "security")
cli.add_command(cmd_branch, "branch")
cli.add_command(cmd_awa, "awa")
cli.add_command(cmd_infra, "infra")
cli.add_command(cmd_heal, "heal")
cli.add_command(cmd_cluster, "cluster")


def main():
    """Entry point for Te Hau CLI."""
    cli()


if __name__ == "__main__":
    main()
