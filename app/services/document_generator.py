"""
Serviço de geração de documentos a partir de templates DOCX.
"""

import tempfile
from pathlib import Path
from docxtpl import DocxTemplate

# Caminhos
BASE_DIR = Path(__file__).parent.parent.parent
TEMPLATE_ROOT = BASE_DIR / "document_templates"
GENERATED_DOCS_ROOT = BASE_DIR / "static" / "generated_documents"

# Cria o diretório de documentos gerados se não existir
GENERATED_DOCS_ROOT.mkdir(parents=True, exist_ok=True)

# Metadados dos templates
DOCUMENT_TEMPLATES = {
    "PROCURACAO_AD_JUDICIA": {
        "name": "Procuração Ad Judicia",
        "filename": "procuracao_ad_judicia.docx"
    },
    "CONTRATO_HONORARIOS": {
        "name": "Contrato de Honorários",
        "filename": "contrato_honorarios.docx"
    },
    "DECLARACAO_HIPOSSUFICIENCIA": {
        "name": "Declaração de Hipossuficiência",
        "filename": "declaracao_hipossuficiencia.docx"
    }
}


def get_available_templates():
    """Retorna a lista de templates disponíveis."""
    return [
        {"templateId": key, "name": value["name"]}
        for key, value in DOCUMENT_TEMPLATES.items()
    ]


def generate_document(template_id: str, client_data: dict, lawyer_data: dict, case_details: dict) -> str:
    """
    Gera um documento .docx a partir de um template.

    Args:
        template_id: O ID do template.
        client_data: Dicionário com os dados do cliente.
        lawyer_data: Dicionário com os dados do advogado.
        case_details: Dicionário com detalhes extras do caso.

    Returns:
        O caminho para o arquivo .docx gerado.
    """
    if template_id not in DOCUMENT_TEMPLATES:
        raise FileNotFoundError(f"O template com ID '{template_id}' não foi encontrado.")

    template_info = DOCUMENT_TEMPLATES[template_id]
    template_path = TEMPLATE_ROOT / template_info["filename"]

    if not template_path.is_file():
        raise FileNotFoundError(f"O arquivo de template '{template_info['filename']}' não foi encontrado.")

    doc = DocxTemplate(template_path)

    # Prepara o contexto
    context = {
        **{f'client_{k}': v for k, v in client_data.items()},
        **{f'lawyer_{k}': v for k, v in lawyer_data.items()},
        **{f'case_{k}': v for k, v in case_details.items()}
    }
    
    # Dados formatados
    context['lawyer_oab'] = f"{lawyer_data.get('oab_number', '')}/{lawyer_data.get('oab_state', '')}"

    doc.render(context)

    # Gera nome de arquivo único
    output_filename = f"{template_id}_{client_data.get('fullName', 'cliente').replace(' ', '_')}_{tempfile.mktemp('','','')[1:]}.docx"
    output_path = GENERATED_DOCS_ROOT / output_filename
    
    doc.save(output_path)
    return str(output_path)