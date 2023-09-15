from libraries.bptf import *
import json


test = GetListings("Rotation Sensation",6)

paintListingsbuy = ListingFilter(test["buy"]).OnlyPaints().Finish()
print(paintListingsbuy)