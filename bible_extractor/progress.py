import logging
import typing as T

class ProgressIndicator:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.num_chapters: T.Optional[int] = None
    
    def report_progress(self, done: bool,
            chap_num: int,
            msg: str = ""):
        prog_percent = (f"[{chap_num*100 // self.num_chapters:3}%] " 
                if self.num_chapters is not None else "")
        progress_msg = "[done] " if done else "[starting] "
        self.logger.info(f"{prog_percent}{progress_msg} {msg}")
            
        
    def starting(self, chap_num: int, msg: str = ""):
        self.report_progress(False, chap_num, msg)
    
    def finishing(self, chap_num: int, msg: str = ""):
        self.report_progress(True, chap_num, msg)
    
    def info(self, *args, **kwargs):
        return self.logger.info(*args, **kwargs)
