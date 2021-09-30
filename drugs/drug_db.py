from .estradiol_valerate import EstradiolValerate
from .estradiol_cypionate import EstradiolCypionate
from .metylphenidate import Methylphenidate
from .lisdex import Lisdexamphetamine, Dexamphetamine
from .drug import Drug
from typing import Type, Optional


def drug_db(drug_string: str) -> Optional[type]:
  if drug_string.lower() in ["estradiolvalerate", "estradiol ealerate", "ev"]:
    return EstradiolValerate
  if drug_string.lower() in ["estradiolcypionate", "estradiol cypionate", "ecyp", "ecy", "ec"]:
    return EstradiolCypionate
  if drug_string.lower() in ["methylphenidate", "ritalin", "MPH"]:
    return Methylphenidate
  if drug_string.lower() in ["lisdexamphetamine", "elvanse", "lisdex", "LDX"]:
    return Lisdexamphetamine
  if drug_string.lower() in ["amphetamine", "dexamphetamine"]:
    return Dexamphetamine
