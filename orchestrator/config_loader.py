#!/usr/bin/env python3
"""
AETHER MIND — Shared Config Loader
===================================
สคริปต์ทั้งหมดอ่านจากไฟล์นี้ — ไม่ต้องตั้งค่าซ้ำ
Minis = Command Center เท่านั้น
"""

import json
from pathlib import Path
from typing import Dict, Any

# Project root (parent of orchestrator/)
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_ROOT / "config" / "api_keys.json"


class Config:
    """Singleton config — โหลดครั้งเดียว ใช้ตลอด session"""
    
    _instance = None
    _data: Dict[str, Any] = {}
    
    @classmethod
    def load(cls) -> Dict[str, Any]:
        """โหลด config จากไฟล์ — auto-load ทุกครั้งที่เรียก"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cls._data = json.load(f)
        return cls._data
    
    @classmethod
    def get_dashscope_key(cls) -> str:
        """ดึง DashScope API key"""
        if not cls._data:
            cls.load()
        return cls._data.get("dashscope", {}).get("api_key", "")
    
    @classmethod
    def get_dashscope_url(cls) -> str:
        """ดึง DashScope base URL"""
        if not cls._data:
            cls.load()
        return cls._data.get("dashscope", {}).get(
            "base_url",
            "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        )
    
    @classmethod
    def is_locked(cls) -> bool:
        """เช็คว่า config ถูกล็อคแล้วหรือยัง"""
        if not cls._data:
            cls.load()
        return cls._data.get("dashscope", {}).get("locked", False)
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """ดึง config ทั้งหมด"""
        if not cls._data:
            cls.load()
        return cls._data


# Auto-load on import
Config.load()
