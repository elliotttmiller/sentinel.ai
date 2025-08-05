"""
Emergency patch for ChatGoogleGenerativeAI to fix model name format issues with litellm.
This module applies runtime patches to ensure compatibility between langchain-google-genai and CrewAI/litellm.
"""

import os
from loguru import logger

def apply_llm_patches():
    """Apply runtime patches to fix LLM model name formatting issues"""
    try:
        # Patch ChatGoogleGenerativeAI to fix model name issues
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Store the original methods
        original_init = ChatGoogleGenerativeAI.__init__
        original_llm_type = ChatGoogleGenerativeAI._llm_type if hasattr(ChatGoogleGenerativeAI, '_llm_type') else None
        
        def patched_init(self, *args, **kwargs):
            """Patched init that ensures correct model name format"""
            # Extract and clean the model name
            model_name = kwargs.get('model', 'gemini-1.5-pro')
            
            # Clean any problematic prefixes
            if model_name.startswith('models/'):
                clean_model = model_name.replace('models/', '')
                kwargs['model'] = clean_model
                logger.debug(f"Patched ChatGoogleGenerativeAI model name: {model_name} -> {clean_model}")
            
            # Call original init
            original_init(self, *args, **kwargs)
            
            # Store the litellm-compatible model name
            if '/' in self.model:
                self._litellm_model = self.model.split('/')[-1]
            else:
                self._litellm_model = self.model
                
            # Ensure it has the gemini/ prefix for litellm
            if not self._litellm_model.startswith('gemini/'):
                self._litellm_model = f"gemini/{self._litellm_model}"
        
        def patched_llm_type(self):
            """Return the litellm-compatible model name"""
            if hasattr(self, '_litellm_model'):
                return self._litellm_model
            elif hasattr(self, 'model'):
                # Fallback logic
                model = self.model
                if model.startswith('models/'):
                    model = model.replace('models/', '')
                if not model.startswith('gemini/'):
                    model = f"gemini/{model}"
                return model
            else:
                return "gemini/gemini-1.5-pro"
        
        # Apply the patches
        ChatGoogleGenerativeAI.__init__ = patched_init
        ChatGoogleGenerativeAI._llm_type = property(patched_llm_type)
        
        logger.success("✅ Applied runtime patches to ChatGoogleGenerativeAI for litellm compatibility")
        return True
        
    except ImportError:
        logger.warning("⚠️  langchain-google-genai not available, skipping patches")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to apply LLM patches: {e}")
        return False

def patch_litellm_completion():
    """Patch litellm completion to handle model name mapping"""
    try:
        import litellm
        
        # Store original completion function
        original_completion = litellm.completion
        
        def patched_completion(*args, **kwargs):
            """Patched completion that fixes model names"""
            if 'model' in kwargs:
                model = kwargs['model']
                
                # Fix the model name format
                if model.startswith('models/gemini'):
                    # Extract the actual model name
                    clean_model = model.split('/')[-1]
                    fixed_model = f"gemini/{clean_model}"
                    kwargs['model'] = fixed_model
                    logger.debug(f"Patched litellm model name: {model} -> {fixed_model}")
                elif model.startswith('models/'):
                    # Remove models/ prefix and add gemini/
                    clean_model = model.replace('models/', '')
                    fixed_model = f"gemini/{clean_model}"
                    kwargs['model'] = fixed_model
                    logger.debug(f"Patched litellm model name: {model} -> {fixed_model}")
            
            # Call original function
            return original_completion(*args, **kwargs)
        
        # Apply the patch
        litellm.completion = patched_completion
        
        logger.success("✅ Applied runtime patches to litellm.completion")
        return True
        
    except ImportError:
        logger.warning("⚠️  litellm not available, skipping completion patches")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to apply litellm patches: {e}")
        return False

# Apply all patches on import
def apply_all_patches():
    """Apply all necessary patches for LLM compatibility"""
    logger.info("🔧 Applying LLM compatibility patches...")
    
    patch_results = []
    patch_results.append(apply_llm_patches())
    patch_results.append(patch_litellm_completion())
    
    if any(patch_results):
        logger.success("✅ LLM compatibility patches applied successfully")
    else:
        logger.warning("⚠️  No patches could be applied - dependencies may not be available")
    
    return any(patch_results)

# Auto-apply patches when module is imported
apply_all_patches()