"""Munich Train System - MVG"""
DOMAIN = "mvg"
ATTRIBUTION = "Data provided by mvg api"

CONF_NEXT_DEPARTURE = "nextdeparture"
CONF_STATION = "station"
CONF_DESTINATIONS = "destinations"
CONF_LINES = "lines"
CONF_PRODUCTS = "products"
CONF_TIMEOFFSET = "timeoffset"
CONF_NUMBER = "number"
CONF_PRODUCTS = {
    "U-Bahn" : "Untergrundbahn", 
    "Tram" : "Straßenbahn", 
    "Bus": "Busverkehr", 
    "ExpressBus" : "Express Bus", 
    "S-Bahn" : "Stadtbahn", 
    "Nachteule" : "Bus Nachtlinie",
}
ATTR_DATA = "data"
