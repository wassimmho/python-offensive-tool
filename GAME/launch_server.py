#!/usr/bin/env python3
"""
Launch script for the 3D Space Combat Game Server
"""

import sys
import os
import argparse

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_server import GameServer

def main():
    print("🚀 3D Space Combat Game Server Launcher")
    print("=" * 50)
    
    parser = argparse.ArgumentParser(description='Launch 3D Space Combat Game Server')
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Host to bind to (default: 0.0.0.0 for all interfaces)')
    parser.add_argument('--port', type=int, default=5555, 
                       help='Port to bind to (default: 5555)')
    
    args = parser.parse_args()
    
    print(f"🌐 Server will be accessible at:")
    print(f"   - Local: localhost:{args.port}")
    print(f"   - Network: {args.host}:{args.port}")
    print(f"   - Public IP: [Your public IP]:{args.port}")
    print()
    print("⚠️  Make sure to:")
    print("   1. Open port {args.port} in your firewall")
    print("   2. Forward port {args.port} on your router if needed")
    print("   3. Share your public IP with other players")
    print()
    
    input("Press Enter to start the server...")
    
    try:
        server = GameServer(args.host, args.port)
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()
