#!/usr/bin/env python3
"""
Mynah Voice Assistant - Main process thread loop.
"""

import asyncio
import sys

async def main():
    print("Initializing Mynah Voice Assistant...")
    # TODO: Implement main process loop
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMynah stopped by user.")
        sys.exit(0)
