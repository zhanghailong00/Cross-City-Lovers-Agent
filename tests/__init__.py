"""测试包。"""

import warnings


# 统一忽略测试环境中第三方库发出的已知弃用告警，避免影响阅读。
warnings.filterwarnings("ignore", category=DeprecationWarning)
