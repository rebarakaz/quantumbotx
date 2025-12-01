# pandas_ta stub for Docker compatibility
# This package provides minimal pandas_ta compatibility using finta

import warnings

# Issue a warning when pandas_ta stub is loaded
warnings.warn(
    "Using pandas_ta stub. Full pandas_ta is not available in Docker. "
    "Strategy calculations may differ.",
    ImportWarning
)

# Re-export finta as fallback
try:
    from finta import TA
    
    # Create minimal compatibility layer
    def rsi(close, length=14, **kwargs):
        """RSI using finta"""
        import pandas as pd
        df = pd.DataFrame({'close': close})
        return TA.RSI(df, length)
    
    def sma(close, length=10, **kwargs):
        """SMA using finta"""
        import pandas as pd
        df = pd.DataFrame({'close': close})
        return TA.SMA(df, length)
    
    def ema(close, length=10, **kwargs):
        """EMA using finta"""
        import pandas as pd
        df = pd.DataFrame({'close': close})
        return TA.EMA(df, length)
    
    def macd(close, fast=12, slow=26, signal=9, **kwargs):
        """MACD using finta"""
        import pandas as pd
        df = pd.DataFrame({'close': close})
        return TA.MACD(df, fast, slow, signal)
    
    def bbands(close, length=20, std=2, **kwargs):
        """Bollinger Bands using finta"""
        import pandas as pd
        df = pd.DataFrame({'close': close})
        return TA.BBANDS(df, length, std)
    
    # Make functions available at module level
    __all__ = ['rsi', 'sma', 'ema', 'macd', 'bbands', 'TA']
    
except ImportError:
    warnings.warn("finta is also not available. Strategies will fail.", ImportWarning)
    
    class DummyTA:
        def __getattr__(self, name):
            raise ImportError(f"Neither pandas_ta nor finta available. Cannot use: {name}")
    
    TA = DummyTA()
