import logging
import time

from sqlalchemy.exc import OperationalError,TimeoutError as PoolTimeout

logger=logging.getLogger(__name__)

RETRYABLE_CODES={2003,2006,2013}

def is_retryable(exc):
    if isinstance(exc,PoolTimeout):
        return True
    if isinstance(exc,OperationalError) and exc.orig is not None:
        return exc.orig.args[0] in RETRYABLE_CODES
    return False

def retry_call(fn,max_retries=2,delay=0.5):
    for attempt in range(max_retries+1):
        try:
            return fn()
        except Exception as exc:
            if not is_retryable(exc):
                logger.error("不是可重试异常，立刻上抛：%s",exc)
                raise
            if attempt==max_retries:
                logger.error ("最终失败：已重试%d次，放弃",max_retries)
                raise
            logger.warning("第%d次重试（原因：%s），%.1f秒以后再试",attempt+1,exc,delay)
            time.sleep(delay)

