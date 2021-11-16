DUMMY = True

if DUMMY:
    from dummy import FriendlyHiSeq
else:
    from friendly_hiseq import FriendlyHiSeq  # type: ignore

from ui import init_ui

hs = FriendlyHiSeq()
init_ui(hs.gen_initialize_seq())
