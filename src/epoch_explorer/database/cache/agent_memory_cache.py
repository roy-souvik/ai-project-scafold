"""
In-memory cache for agent memories with LRU eviction and TTL support.

This cache sits in front of the SQLite database:
- Cache hits return instantly (no DB hit)
- Cache misses fetch from SQLite and populate cache
- TTL-based expiration automatically cleans old entries
- LRU eviction keeps memory usage bounded

USAGE:
    cache = AgentMemoryCache(max_size=1000, ttl_seconds=3600)
    
    # Write (updates both cache and DB)
    cache.put("langgraph_agent", "decision", "healing_strategy", json_content, db_model)
    
    # Read (tries cache first, then DB)
    memory = cache.get("langgraph_agent", "decision", "healing_strategy", db_model)
"""

from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
import json
import threading


class CacheEntry:
    """Single cache entry with TTL tracking"""
    def __init__(self, data: Dict[str, Any], ttl_seconds: int = 3600):
        self.data = data
        self.created_at = datetime.now()
        self.ttl_seconds = ttl_seconds
        self.access_count = 0
    
    def is_expired(self) -> bool:
        """Check if this entry has expired"""
        if self.ttl_seconds is None:
            return False
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def touch(self) -> None:
        """Update access time"""
        self.access_count += 1


class AgentMemoryCache:
    """
    LRU Cache with TTL for agent memories.
    Thread-safe for concurrent access from multiple agents.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl_seconds: int = 3600):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of entries before LRU eviction
            default_ttl_seconds: Default TTL for entries (None = no expiration)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl_seconds
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0
    
    def _make_key(self, agent_id: str, memory_type: str, memory_key: str) -> str:
        """Create cache key from components"""
        return f"{agent_id}:{memory_type}:{memory_key}"
    
    def put(self, agent_id: str, memory_type: str, memory_key: str, 
            data: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        """
        Put an entry in the cache.
        
        Args:
            agent_id: Agent ID
            memory_type: Memory type
            memory_key: Memory key
            data: Data to cache (dict)
            ttl_seconds: TTL override (None uses default)
        """
        with self.lock:
            key = self._make_key(agent_id, memory_type, memory_key)
            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
            
            # Remove old entry if exists (for LRU ordering)
            if key in self.cache:
                del self.cache[key]
            
            # Add new entry (moves to end = most recent)
            self.cache[key] = CacheEntry(data, ttl)
            
            # Evict oldest if over capacity
            if len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
    
    def get(self, agent_id: str, memory_type: str, memory_key: str) -> Optional[Dict[str, Any]]:
        """
        Get an entry from the cache.
        Returns None if not found or expired.
        
        Args:
            agent_id: Agent ID
            memory_type: Memory type
            memory_key: Memory key
        
        Returns:
            Cached data (dict) or None
        """
        with self.lock:
            key = self._make_key(agent_id, memory_type, memory_key)
            
            if key not in self.cache:
                self.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                return None
            
            # Update LRU (move to end)
            del self.cache[key]
            self.cache[key] = entry
            entry.touch()
            
            self.hits += 1
            return entry.data
    
    def remove(self, agent_id: str, memory_type: str, memory_key: str) -> bool:
        """Remove an entry from the cache"""
        with self.lock:
            key = self._make_key(agent_id, memory_type, memory_key)
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear_agent(self, agent_id: str) -> int:
        """Clear all entries for an agent and return count"""
        with self.lock:
            prefix = f"{agent_id}:"
            to_delete = [k for k in self.cache.keys() if k.startswith(prefix)]
            for key in to_delete:
                del self.cache[key]
            return len(to_delete)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        with self.lock:
            to_delete = [k for k, v in self.cache.items() if v.is_expired()]
            for key in to_delete:
                del self.cache[key]
            return len(to_delete)
    
    def clear_all(self) -> None:
        """Clear entire cache"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate_percent": round(hit_rate, 2),
                "total_requests": total_requests
            }
    
    def get_all_entries(self, agent_id: str = None) -> Dict[str, Dict[str, Any]]:
        """Get all entries (optionally filtered by agent)"""
        with self.lock:
            result = {}
            for key, entry in self.cache.items():
                if agent_id and not key.startswith(f"{agent_id}:"):
                    continue
                if not entry.is_expired():
                    result[key] = entry.data
            return result


# Global cache instance (shared across app)
_global_memory_cache: Optional[AgentMemoryCache] = None


def get_agent_memory_cache(max_size: int = 1000, ttl_seconds: int = 3600) -> AgentMemoryCache:
    """Get or create global agent memory cache (singleton pattern)"""
    global _global_memory_cache
    if _global_memory_cache is None:
        _global_memory_cache = AgentMemoryCache(max_size=max_size, default_ttl_seconds=ttl_seconds)
    return _global_memory_cache
