import dns.resolver
from fastapi import FastAPI
import logging
import re
from starlette.responses import FileResponse

logger = logging.getLogger('LocToMap')

app = FastAPI()
COORD_PATTERN = r"(\d+) (\d+) (\d+\.\d+) ([NS]) (\d+) (\d+) (\d+\.\d+) ([EW])"

def dms_to_decimal(degrees: int, minutes: int, seconds: float) -> float:
    return degrees + minutes / 60 + seconds / 3600

@app.get("/")
async def read_index():
    return FileResponse('map.html')

@app.get("/api/{domain}")
async def get_loc_record(domain: str) -> dict:
    try:
        response = dns.resolver.query(domain, "LOC")
        loc_data = {}
        for record in response:
            full_record = str(record)
            logger.info("Got LOC record %s %s", domain, full_record)
            match = re.search(COORD_PATTERN, full_record)
            if match:
                latitude_degrees = int(match.group(1))
                latitude_minutes = int(match.group(2))
                latitude_seconds = float(match.group(3))
                hemisphere_north_south = match.group(4)
                longitude_degrees = int(match.group(5))
                longitude_minutes = int(match.group(6))
                longitude_seconds = float(match.group(7))
                hemisphere_east_west = match.group(8)

                latitude = dms_to_decimal(latitude_degrees, latitude_minutes, latitude_seconds)
                if hemisphere_north_south == 'S':
                    latitude *= -1

                longitude = dms_to_decimal(longitude_degrees, longitude_minutes, longitude_seconds)
                if hemisphere_east_west == 'W':
                    longitude *= -1

                loc_data["latitude"] = str(latitude)
                loc_data["longitude"] = str(longitude)
                loc_data['full'] = full_record
        return loc_data
    except Exception as e:
        return {"error": str(e)}

logging.basicConfig(level=logging.INFO)
