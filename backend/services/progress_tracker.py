"""
분석 진행률 추적 서비스
"""
import asyncio
from typing import Dict, Optional, Callable
from datetime import datetime
import uuid

class ProgressTracker:
    """분석 진행률 추적 클래스"""
    
    def __init__(self, task_id: Optional[str] = None):
        self.task_id = task_id or str(uuid.uuid4())
        self.progress = 0
        self.current_step = ""
        self.steps = []
        self.start_time = datetime.now()
        self.callbacks: list[Callable] = []
    
    def add_callback(self, callback: Callable[[int, str], None]):
        """진행률 업데이트 콜백 추가"""
        self.callbacks.append(callback)
    
    async def update(self, progress: int, step: str):
        """진행률 업데이트"""
        self.progress = min(100, max(0, progress))
        self.current_step = step
        self.steps.append({
            "progress": self.progress,
            "step": step,
            "timestamp": datetime.now().isoformat()
        })
        
        # 콜백 호출
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.progress, step)
                else:
                    callback(self.progress, step)
            except Exception as e:
                print(f"콜백 실행 오류: {e}")
    
    def get_status(self) -> Dict:
        """현재 상태 반환"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return {
            "task_id": self.task_id,
            "progress": self.progress,
            "current_step": self.current_step,
            "elapsed_seconds": elapsed,
            "steps": self.steps
        }


# 전역 진행률 저장소 (실제로는 Redis나 DB 사용 권장)
_progress_store: Dict[str, ProgressTracker] = {}


def get_progress_tracker(task_id: str) -> Optional[ProgressTracker]:
    """진행률 추적기 가져오기"""
    return _progress_store.get(task_id)


def create_progress_tracker(task_id: Optional[str] = None) -> ProgressTracker:
    """새로운 진행률 추적기 생성"""
    tracker = ProgressTracker(task_id)
    _progress_store[tracker.task_id] = tracker
    return tracker


def remove_progress_tracker(task_id: str):
    """진행률 추적기 제거"""
    if task_id in _progress_store:
        del _progress_store[task_id]
