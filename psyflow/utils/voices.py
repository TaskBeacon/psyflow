"""Voice/TTS helper utilities."""

import asyncio
from typing import Optional

from edge_tts import VoicesManager


async def _list_supported_voices_async(filter_lang: Optional[str] = None):
    vm = await VoicesManager.create()
    voices = vm.voices
    if filter_lang:
        voices = [v for v in voices if v["Locale"].startswith(filter_lang)]
    return voices


def list_supported_voices(
    filter_lang: Optional[str] = None,
    human_readable: bool = False,
):
    """Query available edge-tts voices."""
    voices = asyncio.run(_list_supported_voices_async(filter_lang))
    if not human_readable:
        return voices

    header = (
        f"{'ShortName':25} {'Locale':10} {'Gender':8} "
        f"{'Personalities':30} {'FriendlyName'}"
    )
    separator = "-" * len(header)
    print(header)
    print(separator)

    for v in voices:
        short = v.get("ShortName", "")[:25]
        loc = v.get("Locale", "")[:10]
        gen = v.get("Gender", "")[:8]
        pers_list = v.get("VoiceTag", {}).get("VoicePersonalities", [])
        pers = ", ".join(pers_list)[:30]
        disp = v.get("FriendlyName", v.get("Name", ""))

        print(f"{short:25} {loc:10} {gen:8} {pers:30} {disp}")

