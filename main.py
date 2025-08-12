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

def get_loc_record(domain: str) -> dict | None:
    # Might raise NoAnswer or NXDOMAIN
    response = dns.resolver.resolve(domain, "LOC")

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

            return dict(
                domain=domain,
                latitude=str(latitude),
                longitude=str(longitude),
                full=full_record,
            )

@app.get("/api/{domain}")
async def get_loc(domain: str) -> dict:
    tried = set()

    # Get LOC record for that domain
    try:
        tried.add(domain)
        logger.info("Trying %r", domain)
        return get_loc_record(domain)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        pass

    # Resolve to IP addresses
    for addr_type in ("A", "AAAA"):
        try:
            response = dns.resolver.resolve(domain, addr_type)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
        else:
            for record in response:
                logger.info("Trying IP %s", record.address)
                try:
                    # Resolve IPv4 back to name
                    name = str(dns.resolver.resolve(dns.reversename.from_address(record.address), "PTR")[0].target)

                    logger.info("Got domain %r from IP", name)
                    if name not in tried:
                        # Get LOC record for that name
                        tried.add(name)
                        return get_loc_record(name)
                except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                    pass

    return {"error": "No LOC record found"}

logging.basicConfig(level=logging.INFO)
