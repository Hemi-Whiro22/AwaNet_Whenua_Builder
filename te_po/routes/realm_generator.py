"""
Realm Generator Routes

API endpoints for spawning and managing realms
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import os

from te_po.services.realm_generator import (
    get_generator,
    generate_realm,
    list_realms,
    get_realm
)

router = APIRouter(prefix="/realms", tags=["realms"])


class RealmCreateRequest(BaseModel):
    """Request to create a new realm"""
    realm_name: str = Field(..., description="Name of the realm (e.g., Te Wai)")
    kaitiaki_name: str = Field(..., description="Name of the guardian")
    description: Optional[str] = Field(None, description="Description of the realm and its purpose")
    cloudflare_hostname: Optional[str] = Field(None, description="Custom Cloudflare hostname")
    pages_project: Optional[str] = Field(None, description="Cloudflare Pages project name")
    backend_url: Optional[str] = Field(None, description="Custom backend URL")


class RealmResponse(BaseModel):
    """Response for realm operations"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.post("/create", response_model=RealmResponse)
async def create_realm(request: RealmCreateRequest):
    """
    Create a new realm from template
    
    This will:
    1. Create an OpenAI assistant for the realm's kaitiaki
    2. Create a vector store for the realm's knowledge
    3. Copy the project template to /realms/{realm_slug}/
    4. Replace all placeholders with realm-specific values
    5. Generate realm config and README
    """
    try:
        result = generate_realm(
            realm_name=request.realm_name,
            kaitiaki_name=request.kaitiaki_name,
            description=request.description or "",
            cloudflare_hostname=request.cloudflare_hostname,
            pages_project=request.pages_project,
            backend_url=request.backend_url
        )
        
        if result.get("success"):
            return RealmResponse(
                success=True,
                message=f"Realm '{request.realm_name}' created successfully",
                data=result
            )
        else:
            return RealmResponse(
                success=False,
                message=result.get("error", "Unknown error"),
                data=result
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=RealmResponse)
async def list_all_realms():
    """
    List all spawned realms
    
    Returns all realms in the /realms/ directory with their configs
    """
    try:
        realms = list_realms()
        return RealmResponse(
            success=True,
            message=f"Found {len(realms)} realm(s)",
            data={"realms": realms, "count": len(realms)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{realm_slug}", response_model=RealmResponse)
async def get_realm_info(realm_slug: str):
    """
    Get information about a specific realm
    
    Args:
        realm_slug: The slug identifier for the realm (e.g., te_wai)
    """
    try:
        realm = get_realm(realm_slug)
        if realm is None:
            return RealmResponse(
                success=False,
                message=f"Realm '{realm_slug}' not found",
                data=None
            )
        
        return RealmResponse(
            success=True,
            message=f"Found realm '{realm_slug}'",
            data=realm
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/template/info")
async def get_template_info():
    """
    Get information about the realm template
    
    Returns the template config showing what placeholders and secrets are needed
    """
    generator = get_generator()
    template_config_path = generator.template_path / "template.config.json"
    
    if not template_config_path.exists():
        return {
            "success": False,
            "message": "Template config not found",
            "template_path": str(generator.template_path)
        }
    
    import json
    with open(template_config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return {
        "success": True,
        "template_path": str(generator.template_path),
        "realms_path": str(generator.realms_path),
        "config": config
    }


@router.delete("/{realm_slug}", response_model=RealmResponse)
async def delete_realm(realm_slug: str, confirm: bool = False):
    """
    Delete a realm
    
    WARNING: This permanently deletes the realm folder.
    Does NOT delete OpenAI resources (assistant, vector store).
    
    Args:
        realm_slug: The slug identifier for the realm
        confirm: Must be True to actually delete
    """
    if not confirm:
        return RealmResponse(
            success=False,
            message="Deletion not confirmed. Set confirm=true to delete.",
            data=None
        )
    
    import shutil
    generator = get_generator()
    realm_path = generator.realms_path / realm_slug
    
    if not realm_path.exists():
        return RealmResponse(
            success=False,
            message=f"Realm '{realm_slug}' not found",
            data=None
        )
    
    try:
        # Get config before deletion for reference
        config = get_realm(realm_slug)
        
        shutil.rmtree(realm_path)
        
        return RealmResponse(
            success=True,
            message=f"Realm '{realm_slug}' deleted. Note: OpenAI resources were NOT deleted.",
            data={
                "deleted_path": str(realm_path),
                "openai_resources": config.get("openai") if config else None,
                "note": "Manually delete OpenAI assistant and vector store if needed"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
