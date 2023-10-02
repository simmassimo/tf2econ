from libraries.bptf import *
from libraries import scraptf


ses = InitializeSession()
ses = LinkBackpackTF(ses)
ses = FindOpportunities(ses)