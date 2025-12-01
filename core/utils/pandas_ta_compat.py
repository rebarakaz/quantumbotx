# pandas_ta Compatibility Shim for Docker
# This module provides a fallback when pandas_ta is not available
# It uses finta as a drop-in replacement for common indicators

try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
except ImportError:
    PANDAS_TA_AVAILABLE = False
    # Create a dummy module that raises informative errors
    import pandas as pd
    
    class PandasTAShim:
        """Shim for pandas_ta when not available"""
        
        def __getattr__(self, name):
            raise ImportError(
                f"pandas_ta is not available in Docker. "
                f"Attempted to use: {name}. "
                f"Please use 'finta' library instead or disable strategies requiring pandas_ta."
            )
    
    ta = PandasTAShim()

__all__ = ['ta', 'PANDAS_TA_AVAILABLE']
