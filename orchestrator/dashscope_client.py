#!/usr/bin/env python3
"""
AETHER MIND — DashScope API Client
===================================
Direct API client for DashScope (Alibaba Cloud)
OpenAI-compatible format

Endpoint: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# DashScope API Configuration
DASHSCOPE_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

# Auto-load from shared config
from config_loader import Config
DASHSCOPE_API_KEY = Config.get_dashscope_key()
DASHSCOPE_BASE_URL = Config.get_dashscope_url()


@dataclass
class Model:
    """Model information"""
    id: str
    name: str
    context_window: Optional[int] = None
    modalities: List[str] = None
    
    def __post_init__(self):
        if self.modalities is None:
            self.modalities = []


class DashScopeClient:
    """DashScope API Client (OpenAI-compatible)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or DASHSCOPE_API_KEY
        self.base_url = DASHSCOPE_BASE_URL
        
        if not self.api_key:
            raise ValueError(
                "DASHSCOPE_API_KEY not set. "
                "Please set environment variable or pass api_key parameter."
            )
    
    def list_models(self) -> List[Model]:
        """
        Get list of available models from DashScope
        
        Returns:
            List of Model objects
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{self.base_url}/models",
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to list models: {response.status_code} - {response.text}")
        
        data = response.json()
        models = []
        
        for model_data in data.get("data", []):
            model = Model(
                id=model_data.get("id"),
                name=model_data.get("name", model_data.get("id")),
                context_window=model_data.get("context_window"),
                modalities=model_data.get("modalities", [])
            )
            models.append(model)
        
        return models
    
    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Chat completion (OpenAI-compatible)
        
        Args:
            model: Model ID (e.g., "qwen-max")
            messages: List of message dicts [{"role": "user", "content": "..."}]
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-2.0)
            stream: Whether to stream response
            
        Returns:
            Response dict with "content" key
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"Chat completion failed: {response.status_code} - {response.text}")
        
        data = response.json()
        
        # Extract content from response
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0].get("message", {}).get("content", "")
        else:
            content = ""
        
        return {
            "content": content,
            "usage": data.get("usage", {}),
            "model": data.get("model", model)
        }
    
    def embeddings(
        self,
        model: str,
        input_text: str
    ) -> List[float]:
        """
        Generate embeddings
        
        Args:
            model: Embedding model ID
            input_text: Text to embed
            
        Returns:
            List of embedding values
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "input": input_text
        }
        
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Embedding failed: {response.status_code} - {response.text}")
        
        data = response.json()
        return data["data"][0]["embedding"]


# Convenience function
def quick_chat(model: str, prompt: str, api_key: Optional[str] = None) -> str:
    """
    Quick chat completion
    
    Args:
        model: Model ID
        prompt: User prompt
        api_key: Optional API key
        
    Returns:
        Response content as string
    """
    client = DashScopeClient(api_key)
    messages = [{"role": "user", "content": prompt}]
    result = client.chat(model, messages, max_tokens=1024)
    return result["content"]


# Test function
def test_connection(api_key: Optional[str] = None) -> bool:
    """
    Test API connection
    
    Returns:
        True if connection successful
    """
    try:
        client = DashScopeClient(api_key)
        models = client.list_models()
        print(f"✅ API Connection successful")
        print(f"📊 Found {len(models)} models")
        return True
    except Exception as e:
        print(f"❌ API Connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test connection
    print("🧪 Testing DashScope API connection...")
    if test_connection():
        print("\n📋 Available Models:")
        client = DashScopeClient()
        models = client.list_models()
        
        for i, model in enumerate(models[:10], 1):
            ctx = f"({model.context_window:,} ctx)" if model.context_window else ""
            mods = ", ".join(model.modalities) if model.modalities else "text"
            print(f"  {i}. {model.name} {ctx} [{mods}]")
        
        if len(models) > 10:
            print(f"  ... and {len(models) - 10} more")
