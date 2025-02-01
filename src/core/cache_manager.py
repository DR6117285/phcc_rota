from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import threading
import logging

logger = logging.getLogger(__name__)

class CacheEntry:
    def __init__(self, value: Any, ttl: int = 3600):
        self.value = value
        self.expiry = datetime.now() + timedelta(seconds=ttl)
        self.last_accessed = datetime.now()
        self.access_count = 0

    def is_expired(self) -> bool:
        return datetime.now() > self.expiry

    def access(self) -> None:
        self.last_accessed = datetime.now()
        self.access_count += 1

class CacheManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CacheManager, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the cache manager"""
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = 1000  # Maximum number of cached items
        self._cleanup_threshold = 0.8  # Cleanup when 80% full
        self._metrics: Dict[str, int] = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        entry = self._cache.get(key)
        
        if entry is None:
            self._metrics['misses'] += 1
            return None
            
        if entry.is_expired():
            self._remove(key)
            self._metrics['misses'] += 1
            return None
            
        entry.access()
        self._metrics['hits'] += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set a value in cache with TTL in seconds"""
        if len(self._cache) >= self._max_size * self._cleanup_threshold:
            self._cleanup()
            
        self._cache[key] = CacheEntry(value, ttl)

    def _remove(self, key: str) -> None:
        """Remove an item from cache"""
        if key in self._cache:
            del self._cache[key]
            self._metrics['evictions'] += 1

    def _cleanup(self) -> None:
        """Clean up expired and least recently used items"""
        # Remove expired entries
        expired_keys = [
            key for key, entry in self._cache.items() 
            if entry.is_expired()
        ]
        for key in expired_keys:
            self._remove(key)
            
        # If still too many items, remove least accessed
        if len(self._cache) >= self._max_size:
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: (x[1].access_count, x[1].last_accessed)
            )
            entries_to_remove = sorted_entries[:int(self._max_size * 0.2)]
            for key, _ in entries_to_remove:
                self._remove(key)

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._metrics = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        total_requests = self._metrics['hits'] + self._metrics['misses']
        hit_rate = (self._metrics['hits'] / total_requests * 100 
                   if total_requests > 0 else 0)
        
        return {
            **self._metrics,
            'total_entries': len(self._cache),
            'hit_rate': hit_rate,
            'memory_usage': sum(
                len(str(entry.value)) for entry in self._cache.values()
            ) / 1024  # KB
        }

    def get_keys(self) -> List[str]:
        """Get all active cache keys"""
        return list(self._cache.keys())

    def touch(self, key: str) -> bool:
        """Update last access time of a cache entry"""
        entry = self._cache.get(key)
        if entry and not entry.is_expired():
            entry.access()
            return True
        return False

    def extend_ttl(self, key: str, additional_seconds: int) -> bool:
        """Extend TTL of a cache entry"""
        entry = self._cache.get(key)
        if entry and not entry.is_expired():
            entry.expiry += timedelta(seconds=additional_seconds)
            return True
        return False 