class Proton:
    base_dir: str
    dist_dir: str
    bin_dir: str
    lib_dir: str
    lib64_dir: str
    fonts_dir: str
    version_file: str
    default_pfx_dir: str
    user_settings_file: str
    wine_bin: str
    wineserver_bin: str
    def __init__(self, base_dir: str) -> None: ...
    def need_tarball_extraction(self) -> bool: ...
    def extract_tarball(self) -> None: ...
    def missing_default_prefix(self) -> bool: ...
    def make_default_prefix(self) -> None: ...

class CompatData:
    base_dir: str
    prefix_dir: str
    version_file: str
    config_info_file: str
    tracked_files_file: str
    def __init__(self, base_dir: str) -> None: ...

class Session:
    env: dict
    def init_wine(self) -> None: ...
    def init_session(self) -> None:
        """
        Initializes proton session.

        Environment variables:

        PROTON_LOG    Enables logging
        """

g_proton: Proton
g_compatdata: CompatData
g_session: Session
