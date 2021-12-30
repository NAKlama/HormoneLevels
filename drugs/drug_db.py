from .estradiol import Estradiol, EstradiolGel
from .estradiol_valerate import EstradiolValerate
from .estradiol_cypionate import EstradiolCypionate
from .testosterone import Testosterone
from .testosterone_cypionate import TestosteroneCypionate
from .metylphenidate import Methylphenidate
from .lisdex import Lisdexamphetamine, Dexamphetamine
from .cyproterone_acetate import CyproteroneAcetate
from typing import Optional


def drug_db(drug_string: str) -> Optional[type]:
  if drug_string.lower() in ["estradiol", "e2"]:
    return Estradiol
  if drug_string.lower() in ["estradiol gel", "estrogel", "gynokadin"]:
    return EstradiolGel
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
  if drug_string.lower() in ["cpa", "cypro", 'cyproterone', 'cyproterone acetate']:
    return CyproteroneAcetate
  if drug_string.lower() in ["t", "testo", "testosterone"]:
    return Testosterone
  if drug_string.lower() in ["tcyp", "testosterone cypionate"]:
    return TestosteroneCypionate
