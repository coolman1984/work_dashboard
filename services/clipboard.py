class InternalClipboard:
    file_path = None; operation = None; source_panel = None
    @classmethod
    def set(cls, path, op, panel): cls.file_path = path; cls.operation = op; cls.source_panel = panel
    @classmethod
    def get(cls): return cls.file_path, cls.operation
    @classmethod
    def clear(cls): 
        if cls.source_panel: cls.source_panel.clear_clipboard_indicator()
        cls.file_path = None; cls.operation = None; cls.source_panel = None
    @classmethod
    def has_data(cls): return cls.file_path is not None
