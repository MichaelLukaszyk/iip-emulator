import astropy.units as u

class ParamEntry:
    value: u.Quantity
    crit_type: str

    def __init__(self, value, crit_type = ""):
        self.value = value
        self.crit_type = crit_type
    def __str__(self):
        return str(self.value)
    
    def to_dict(self):
        return {
            "value": str(self.value),
            "crit_type": self.crit_type
        }

    @staticmethod
    def from_dict(data):
        return ParamEntry(
            value = u.Quantity(data["value"]),
            crit_type = data["crit_type"]
        )

class RunEntry:
    log_lsun: ParamEntry
    v_start: ParamEntry
    t_inner: ParamEntry

    def __init__(self, log_lsun, v_start, t_inner):
        self.log_lsun = log_lsun
        self.v_start = v_start
        self.t_inner = t_inner
    def __str__(self):
        return str(self.log_lsun) + " log_lsun, " + str(self.v_start) + ", " + str(self.t_inner)
    
    @classmethod
    def new(cls, log_lsun, v_start, t_inner, crit_index = -1, crit_type = None):
        log_lsun = u.Quantity(log_lsun)
        return cls(
            ParamEntry(log_lsun.copy(), crit_index == 0 and crit_type or None),
            ParamEntry(v_start.copy(), crit_index == 1 and crit_type or None),
            ParamEntry(t_inner.copy(), crit_index == 2 and crit_type or None)
        )
    
    def to_dict(self):
        return {
            "log_lsun": self.log_lsun.to_dict(),
            "v_start": self.v_start.to_dict(),
            "t_inner": self.t_inner.to_dict()
        }

    @staticmethod
    def from_dict(data):
        return RunEntry(
            log_lsun = ParamEntry.from_dict(data["log_lsun"]),
            v_start = ParamEntry.from_dict(data["v_start"]),
            t_inner = ParamEntry.from_dict(data["t_inner"])
        )