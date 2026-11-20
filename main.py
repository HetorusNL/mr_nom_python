# entrypoint for the browser build (pygbag requires a main.py)
import asyncio

# pygbag decides which packages to load by scanning the imports in main.py,
# so pygame must be imported here explicitly
import pygame  # noqa: F401

from mr_nom import MrNom

asyncio.run(MrNom().run())
