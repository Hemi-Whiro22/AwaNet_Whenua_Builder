"""
Te Hau Pipeline Executor

Real execution engine for AwaOS pipelines.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from te_hau.core.fs import get_projects_path


class PipelineExecutor:
    """Executes pipeline stages with real AI integrations."""
    
    def __init__(self, realm_name: str, verbose: bool = False):
        self.realm_name = realm_name
        self.realm_path = get_projects_path() / realm_name
        self.namespace = f"realm::{realm_name}"
        self.verbose = verbose
        self.results = {}
    
    def load_pipeline(self, pipeline_name: str) -> Dict:
        """Load pipeline configuration."""
        # Check custom pipelines
        yaml_path = self.realm_path / "pipelines" / f"{pipeline_name}.yaml"
        if yaml_path.exists():
            with open(yaml_path) as f:
                return yaml.safe_load(f)
        
        json_path = self.realm_path / "pipelines" / f"{pipeline_name}.json"
        if json_path.exists():
            with open(json_path) as f:
                return json.load(f)
        
        # Builtin pipelines
        return self.get_builtin_pipeline(pipeline_name)
    
    def get_builtin_pipeline(self, name: str) -> Optional[Dict]:
        """Get built-in pipeline definition."""
        builtins = {
            'embed': {
                'name': 'Embedding Pipeline',
                'stages': [
                    {'name': 'chunk', 'type': 'chunker', 'size': 1000, 'overlap': 100},
                    {'name': 'embed', 'type': 'embedder', 'model': 'text-embedding-3-small'},
                    {'name': 'store', 'type': 'vector_store'}
                ]
            },
            'summarise': {
                'name': 'Summarisation Pipeline',
                'stages': [
                    {'name': 'summarise', 'type': 'llm', 'action': 'summarize', 'model': 'gpt-4o-mini'}
                ]
            },
            'translate': {
                'name': 'Translation Pipeline',
                'stages': [
                    {'name': 'translate', 'type': 'llm', 'action': 'translate_to_maori', 'model': 'gpt-4o'}
                ]
            },
            'taonga': {
                'name': 'Taonga Pipeline',
                'stages': [
                    {'name': 'summarise', 'type': 'llm', 'action': 'summarize', 'model': 'gpt-4o-mini'},
                    {'name': 'translate', 'type': 'llm', 'action': 'translate_to_maori', 'model': 'gpt-4o'},
                    {'name': 'chunk', 'type': 'chunker', 'size': 1000},
                    {'name': 'embed', 'type': 'embedder'},
                    {'name': 'store', 'type': 'vector_store'}
                ]
            }
        }
        return builtins.get(name)
    
    def execute(self, pipeline_name: str, input_data: Any) -> Dict:
        """Execute a complete pipeline."""
        config = self.load_pipeline(pipeline_name)
        if not config:
            raise ValueError(f"Pipeline '{pipeline_name}' not found")
        
        data = input_data
        results = {
            'pipeline': pipeline_name,
            'realm': self.realm_name,
            'started_at': datetime.utcnow().isoformat(),
            'stages': []
        }
        
        for stage in config.get('stages', []):
            stage_name = stage['name']
            stage_type = stage['type']
            
            if self.verbose:
                print(f"  → {stage_name} ({stage_type})")
            
            try:
                data = self.execute_stage(stage, data)
                results['stages'].append({
                    'name': stage_name,
                    'status': 'success',
                    'output_type': type(data).__name__
                })
            except Exception as e:
                results['stages'].append({
                    'name': stage_name,
                    'status': 'error',
                    'error': str(e)
                })
                results['error'] = str(e)
                break
        
        results['completed_at'] = datetime.utcnow().isoformat()
        results['output'] = data
        
        return results
    
    def execute_stage(self, stage: Dict, data: Any) -> Any:
        """Execute a single pipeline stage."""
        stage_type = stage['type']
        
        if stage_type == 'chunker':
            return self._execute_chunker(stage, data)
        elif stage_type == 'embedder':
            return self._execute_embedder(stage, data)
        elif stage_type == 'vector_store':
            return self._execute_vector_store(stage, data)
        elif stage_type == 'llm':
            return self._execute_llm(stage, data)
        elif stage_type == 'text_clean':
            return self._execute_text_clean(stage, data)
        elif stage_type == 'ocr':
            return self._execute_ocr(stage, data)
        elif stage_type == 'file_read':
            return self._execute_file_read(stage, data)
        else:
            # Pass through unknown types
            return data
    
    def _execute_ocr(self, stage: Dict, data: Any) -> str:
        """Execute OCR on image/PDF files."""
        engine = stage.get('engine', 'tesseract')
        
        # If data is a file path
        if isinstance(data, str) and Path(data).exists():
            file_path = Path(data)
        elif isinstance(data, Path):
            file_path = data
        else:
            raise ValueError("OCR stage requires file path input")
        
        suffix = file_path.suffix.lower()
        
        if engine == 'tesseract':
            try:
                import pytesseract
                from PIL import Image
                
                if suffix in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
                    image = Image.open(file_path)
                    text = pytesseract.image_to_string(image)
                    return text
                elif suffix == '.pdf':
                    # Try pdf2image for PDF
                    try:
                        from pdf2image import convert_from_path
                        images = convert_from_path(file_path)
                        texts = []
                        for img in images:
                            texts.append(pytesseract.image_to_string(img))
                        return "\n\n".join(texts)
                    except ImportError:
                        raise ImportError(
                            "pdf2image required for PDF OCR. "
                            "Install with: pip install pdf2image"
                        )
                else:
                    raise ValueError(f"Unsupported file type for OCR: {suffix}")
                    
            except ImportError:
                raise ImportError(
                    "pytesseract and Pillow required for OCR. "
                    "Install with: pip install pytesseract Pillow\n"
                    "Also install Tesseract: sudo apt install tesseract-ocr"
                )
        else:
            raise ValueError(f"Unknown OCR engine: {engine}")
    
    def _execute_file_read(self, stage: Dict, data: Any) -> str:
        """Read content from a file."""
        if isinstance(data, str) and Path(data).exists():
            file_path = Path(data)
        elif isinstance(data, Path):
            file_path = data
        else:
            # Data might already be text content
            return str(data)
        
        encoding = stage.get('encoding', 'utf-8')
        return file_path.read_text(encoding=encoding)
    
    def _execute_chunker(self, stage: Dict, data: Any) -> List[str]:
        """Chunk text into smaller pieces."""
        from te_hau.core.ai import chunk_text
        
        if isinstance(data, str):
            text = data
        elif isinstance(data, list):
            text = "\n\n".join(str(item) for item in data)
        else:
            text = str(data)
        
        return chunk_text(
            text,
            chunk_size=stage.get('size', 1000),
            overlap=stage.get('overlap', 100),
            preserve_paragraphs=stage.get('preserve_paragraphs', True)
        )
    
    def _execute_embedder(self, stage: Dict, data: Any) -> List[Dict]:
        """Generate embeddings for text chunks."""
        from te_hau.core.ai import embed_texts
        
        if isinstance(data, str):
            chunks = [data]
        elif isinstance(data, list):
            chunks = data
        else:
            chunks = [str(data)]
        
        model = stage.get('model', 'text-embedding-3-small')
        embeddings = embed_texts(chunks, model=model)
        
        return [
            {'content': chunk, 'embedding': emb}
            for chunk, emb in zip(chunks, embeddings)
        ]
    
    def _execute_vector_store(self, stage: Dict, data: Any) -> Dict:
        """Store embeddings in vector database."""
        from te_hau.core.supabase import store_embeddings
        
        if not isinstance(data, list):
            raise ValueError("Vector store expects list of {content, embedding} dicts")
        
        doc_ids = store_embeddings(self.namespace, data)
        
        return {
            'stored': len(doc_ids),
            'namespace': self.namespace,
            'doc_ids': doc_ids
        }
    
    def _execute_llm(self, stage: Dict, data: Any) -> str:
        """Execute LLM stage (summarize, translate, etc.)."""
        from te_hau.core import ai
        
        action = stage.get('action', 'complete')
        model = stage.get('model', 'gpt-4o-mini')
        
        if isinstance(data, list):
            text = "\n\n".join(str(item) for item in data)
        else:
            text = str(data)
        
        if action == 'summarize':
            return ai.summarize(text, model=model)
        elif action == 'translate_to_maori':
            return ai.translate_to_maori(text, model=model)
        elif action == 'translate_to_english':
            return ai.translate_to_english(text, model=model)
        else:
            system = stage.get('system_prompt', 'You are a helpful assistant.')
            return ai.complete(text, system=system, model=model)
    
    def _execute_text_clean(self, stage: Dict, data: Any) -> str:
        """Clean and normalize text."""
        import re
        
        text = str(data) if not isinstance(data, str) else data
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove extra newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()


def run_pipeline(
    realm_name: str,
    pipeline_name: str,
    input_data: Any,
    verbose: bool = False
) -> Dict:
    """
    Convenience function to run a pipeline.
    
    Args:
        realm_name: Name of the realm
        pipeline_name: Name of the pipeline
        input_data: Input data (text, file path, etc.)
        verbose: Show progress
        
    Returns:
        Pipeline results dict
    """
    executor = PipelineExecutor(realm_name, verbose=verbose)
    return executor.execute(pipeline_name, input_data)
