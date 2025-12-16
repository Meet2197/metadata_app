from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
import os

SP_SITE = os.getenv("SP_SITE_URL")
SP_CLIENT_ID = os.getenv("SP_CLIENT_ID")
SP_CLIENT_SECRET = os.getenv("SP_CLIENT_SECRET")
SP_LIST_NAME = "RTG Microscopy Experiments"

def export_to_sharepoint(metadata: dict):
    ctx = ClientContext(SP_SITE).with_credentials(
        ClientCredential(SP_CLIENT_ID, SP_CLIENT_SECRET)
    )

    sp_list = ctx.web.lists.get_by_title(SP_LIST_NAME)

    item = {
        "Title": metadata["filename"],
        "User": metadata["user"],
        "Microscope": metadata["microscope"],
        "Objective": metadata["objective"],
        "RawPath": metadata["path"],
        "OME_TIFF": metadata.get("ome_tiff_path"),
        "OME_ZARR": metadata.get("ome_zarr_path"),
        "ELN_ID": metadata.get("eln_id")
    }

    sp_list.add_item(item)
    ctx.execute_query()
