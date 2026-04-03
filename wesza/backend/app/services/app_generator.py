"""
App Generator service for converting templates to React code.

This module provides functionality to transform JSON configuration
templates into complete React/PWA applications with offline support.
"""

import structlog
from typing import Any, Dict, Optional

logger = structlog.get_logger()


class AppGenerator:
    """
    App Generator for converting templates to React code.
    
    This class takes a JSON configuration and generates a complete
    React PWA application with proper file structure, components,
    and service worker for offline support.
    """
    
    def __init__(self):
        """Initialize App Generator."""
        logger.debug("App Generator initialized")
    
    def template_to_react(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Convert template configuration to React application files.
        
        Args:
            config: Template configuration with name, modules, components, etc.
            
        Returns:
            Dict[str, str]: Dictionary of filename to file content.
        """
        app_name = config.get("name", "Wesza App")
        modules = config.get("modules", [])
        components = config.get("components", [])
        data_models = config.get("data_models", {})
        
        files = {}
        
        # Generate index.html
        files["index.html"] = self._generate_index_html(app_name)
        
        # Generate main.tsx
        files["main.tsx"] = self._generate_main_tsx()
        
        # Generate App.tsx
        files["App.tsx"] = self._generate_app_tsx(config)
        
        # Generate component files
        for component in components:
            files[f"{component}.tsx"] = self._generate_component(component, config)
        
        # Generate types file
        files["types.ts"] = self._generate_types(data_models)
        
        # Generate service worker
        files["service-worker.js"] = self._generate_service_worker(app_name)
        
        logger.info(
            "React files generated",
            app_name=app_name,
            file_count=len(files),
        )
        
        return files
    
    def _generate_index_html(self, app_name: str) -> str:
        """Generate index.html with React root and Tailwind CSS."""
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{app_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <meta name="theme-color" content="#3b82f6" />
    <link rel="manifest" href="/manifest.json" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""
    
    def _generate_main_tsx(self) -> str:
        """Generate main.tsx entry point."""
        return """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/globals.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
    
    def _generate_app_tsx(self, config: Dict[str, Any]) -> str:
        """Generate App.tsx with components based on config."""
        app_name = config.get("name", "Wesza App")
        modules = config.get("modules", [])
        
        modules_imports = "\n".join([
            f"import {module.capitalize()} from './components/{module.capitalize()}'"
            for module in modules[:5]  # Limit to 5 modules
        ])
        
        modules_render = "\n          ".join([
            f"<{module.capitalize()} />"
            for module in modules[:5]
        ])
        
        return f"""import React, {{ useState, useEffect }} from 'react'
import OfflineBadge from './components/OfflineBadge'
{modules_imports}

interface AppState {{
  isOnline: boolean
  lastSync: Date | null
}}

function App() {{
  const [state, setState] = useState<AppState>({{
    isOnline: navigator.onLine,
    lastSync: null,
  }})

  useEffect(() => {{
    const handleOnline = () => setState(prev => ({{ ...prev, isOnline: true }}))
    const handleOffline = () => setState(prev => ({{ ...prev, isOnline: false }}))

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {{
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }}
  }}, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-blue-600 text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">{app_name}</h1>
          <OfflineBadge isOnline={{state.isOnline}} />
        </div>
      </header>

      <main className="container mx-auto p-4">
        <div className="space-y-4">
          {modules_render}
        </div>
      </main>

      <footer className="bg-gray-800 text-white p-4 mt-8">
        <div className="container mx-auto text-center text-sm">
          <p>Powered by Wesza • Generated PWA</p>
        </div>
      </footer>
    </div>
  )
}}

export default App
"""
    
    def _generate_component(self, name: str, config: Dict[str, Any]) -> str:
        """Generate a React component file."""
        return f"""import React from 'react'

interface {name}Props {{
  // Add props as needed
}}

const {name}: React.FC<{name}Props> = ({{}}) => {{
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold mb-2">{name}</h2>
      <p className="text-gray-600">Component placeholder - customize as needed</p>
    </div>
  )
}}

export default {name}
"""
    
    def _generate_types(self, data_models: Dict[str, Any]) -> str:
        """Generate TypeScript types from data models."""
        type_definitions = []
        
        for model_name, fields in data_models.items():
            type_def = f"export interface {model_name} {{\n"
            for field_name, field_type in fields.items():
                ts_type = self._convert_to_ts_type(field_type)
                type_def += f"  {field_name}: {ts_type}\n"
            type_def += "}\n"
            type_definitions.append(type_def)
        
        return "\n".join(type_definitions) if type_definitions else "// No data models defined\n"
    
    def _convert_to_ts_type(self, field_type: str) -> str:
        """Convert generic type to TypeScript type."""
        type_mapping = {
            "string": "string",
            "number": "number",
            "boolean": "boolean",
            "date": "Date",
            "array": "any[]",
            "object": "Record<string, any>",
        }
        return type_mapping.get(field_type.lower(), "any")
    
    def _generate_service_worker(self, app_name: str) -> str:
        """Generate service worker for offline caching."""
        return f"""// Service Worker for {app_name}
// Generated by Wesza

const CACHE_NAME = '{app_name.replace(/\s+/g, '-')}-v1'
const OFFLINE_URL = '/offline.html'

const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  OFFLINE_URL,
]

// Install event - cache static assets
self.addEventListener('install', (event) => {{
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {{
      console.log('[Service Worker] Caching static assets')
      return cache.addAll(STATIC_ASSETS)
    }})
  )
  self.skipWaiting()
}})

// Activate event - clean old caches
self.addEventListener('activate', (event) => {{
  event.waitUntil(
    caches.keys().then((cacheNames) => {{
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    }})
  )
  self.clients.claim()
}})

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {{
  // Skip non-GET requests
  if (event.request.method !== 'GET') return

  event.respondWith(
    fetch(event.request)
      .then((response) => {{
        // Clone response for caching
        const responseClone = response.clone()
        caches.open(CACHE_NAME).then((cache) => {{
          cache.put(event.request, responseClone)
        }})
        return response
      }})
      .catch(() => {{
        console.log('[Service Worker] Fetch failed, serving from cache')
        return caches.match(event.request).then((cachedResponse) => {{
          if (cachedResponse) {{
            return cachedResponse
          }}
          // Fallback to offline page for navigation requests
          if (event.request.mode === 'navigate') {{
            return caches.match(OFFLINE_URL)
          }}
        }})
      }})
  )
}})

// Background sync for offline data
self.addEventListener('sync', (event) => {{
  if (event.tag === 'sync-data') {{
    event.waitUntil(syncData())
  }}
}})

async function syncData() {{
  // Implement data sync logic here
  console.log('[Service Worker] Syncing offline data')
}}
"""
    
    def validate_generated_code(self, code: str) -> bool:
        """
        Basic validation of generated code.
        
        Args:
            code: Generated code string.
            
        Returns:
            bool: True if code appears valid, False otherwise.
        """
        # Basic checks
        if not code or len(code) < 10:
            return False
        
        # Check for common syntax issues
        if code.count("{") != code.count("}"):
            logger.warning("Unbalanced braces in generated code")
            return False
        
        if code.count("(") != code.count(")"):
            logger.warning("Unbalanced parentheses in generated code")
            return False
        
        return True
