import asyncio

from pyseq2.com.async_com import COM, CmdParse
from pyseq2.fakes.fake_serial import FakeOptions, open_fake
from pyseq2.utils.utils import ok_if_match


async def test_openfake():
    reader, writer = await open_fake("COMX", "fpga", 9600, FakeOptions())
    writer.write(b"RESET")
    assert await reader.readline() == b"@LOG The FPGA is now online.  Enjoy!\r\n"
    assert await reader.readline() == b"RESET\r\n"


async def test_drop():
    # Test that missing commands do not freeze the program.
    com = await COM.ainit("fpga", "COMX", min_spacing=0.0, test_params=FakeOptions(drop=True))
    cmd = CmdParse(
        "RESET", ok_if_match("@LOG The FPGA is now online.  Enjoy!\nRESET"), n_lines=2, timeout=0.5
    )
    try:
        await asyncio.gather(*[com.send(cmd) for _ in range(5)], return_exceptions=False)
    except asyncio.TimeoutError:
        ...

    com.test_params.drop = False
    assert await com.send(CmdParse("EM2I", ok_if_match("EM2I"), timeout=0.5))
