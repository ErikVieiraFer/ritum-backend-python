"""
Endpoints do gerador de documentos.
"""

from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status

from app import models, schemas
from app.dependencies import get_current_user
from app.services import document_generator

router = APIRouter(prefix="/api/v1", tags=["Gerador de Documentos"])


@router.get("/document-templates")
def list_templates(current_user: models.User = Depends(get_current_user)):
    """
    Lista todos os templates de documentos disponíveis.
    """
    return document_generator.get_available_templates()


@router.post("/documents/generate", response_model=schemas.GenerateDocumentResponse)
def generate_document(
    request: schemas.GenerateDocumentRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    Gera um documento a partir de um template.
    """
    try:
        # Converter dados do usuário atual para dict
        lawyer_data = schemas.User.model_validate(current_user).model_dump(by_alias=True)
        client_data = request.clientData.model_dump(by_alias=True)
        case_details = request.caseDetails.model_dump(by_alias=True) if request.caseDetails else {}

        output_path_str = document_generator.generate_document(
            template_id=request.templateId,
            client_data=client_data,
            lawyer_data=lawyer_data,
            case_details=case_details
        )
        
        output_path = Path(output_path_str)
        file_name = output_path.name
        document_url = f"/static/generated_documents/{file_name}"

        return {
            "documentUrl": document_url,
            "fileName": file_name
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar documento: {str(e)}"
        )