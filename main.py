from voice_utils import stream, p

FAST_MODE = True

if FAST_MODE:
    print("FAST MODE")
    import main_fast
    main_fast.main()
else:
    print("FULL MODE")
    import main_full
    main_full.main()

stream.stop_stream()
stream.close()
p.terminate()