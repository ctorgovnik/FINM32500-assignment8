import json
import os
from typing import Dict, Any


class Config:
    """Singleton class for managing application configuration"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: str = 'config.json'):
        if not self._initialized:            
            with open(config_path, 'r') as f:
                self._raw_config = json.load(f)
            
            # Process Gateway config: convert delimiter string to bytes
            gateway_config = self._raw_config["Gateway"].copy()
            gateway_config["delimiter"] = gateway_config["delimiter"].encode('utf-8')
            self._gateway_config = gateway_config
            
            Config._initialized = True

            # Process OrderBook config
            orderbook_config = self._raw_config["OrderBook"].copy()
            self._orderbook_config = orderbook_config

            # Process Strategy config
            strategy_config = self._raw_config["Strategy"].copy()
            self._strategy_config = strategy_config

            # Process OrderManager config
            ordermanager_config = self._raw_config["OrderManager"].copy()
            self._ordermanager_config = ordermanager_config
    
    @property
    def gateway(self) -> Dict[str, Any]:
        """Get Gateway configuration"""
        return self._gateway_config
    
    @property
    def orderbook(self) -> Dict[str, Any]:
        """Get OrderBook configuration"""
        return self._orderbook_config
    
    @property
    def strategy(self) -> Dict[str, Any]:
        """Get Strategy configuration"""
        return self._strategy_config
    
    @property
    def ordermanager(self) -> Dict[str, Any]:
        """Get OrderManager configuration"""
        return self._ordermanager_config
    
    def get(self, section: str) -> Dict[str, Any]:
        """Get a configuration section"""
        return self._raw_config.get(section, {})

