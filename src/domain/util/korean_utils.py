def add_subject_particle(name: str) -> str:
    """Add Korean subject particle (이/가) based on final consonant"""
    if not name:
        return name
    last_char = name[-1]
    if not ('가' <= last_char <= '힣'):
        return name
    code = ord(last_char) - 0xAC00
    jongseong = code % 28
    return name if jongseong == 0 else name + "이"
