from flask import current_app
import googlemaps
from sqlalchemy import Column, Integer, ForeignKey, func, select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2 import Geometry
from godisbilen.app import db
from godisbilen.region import Region

class Location(db.Model):
    """
    A class used to represent a Location

    Attributes
    ----------
    id : int
        The unique id of the location
    coord : Geometry
        The locations coordinates
    region_id: int
        The id of the region where the location is in
    region: Region
        The region where the location is in
    orders: list<Order>
        A list of orders that has been placed on the location
    lat: float
        The latitude of the location
    lng: float
        The longitude of the location
    count_orders: int
        How many orders thas has been placed on the location
    formatted_address: str
        A formatted address of the location
    street_name: str
        The name of the street
    street_number: str
        The streetnumber
    postal_town: str
        The postal town
    
    Methods
    -------
    time_between(destination: Location)
        Returns the time to the specified location. (Driving time)
    """

    __tablename__ = "location"
    id = Column(Integer, primary_key=True)
    coord = Column(Geometry("POINT"))
    region_id = Column(Integer, ForeignKey("region.id"))
    region = relationship("Region", back_populates="locations")
    orders = relationship("Order", back_populates="location")

    def __init__(self, lat, lng, *args, **kwargs):
        self.coord = "POINT({} {})".format(lng, lat)
        self.region = Region.query.filter_by(active=True).filter(Region.bounds.ST_Intersects(self.coord)).first()
        super().__init__(*args, **kwargs)

    @hybrid_property
    def lat(self):
        """Get latitude of the location

        Returns:
            float : The latitude
        """
        return db.session.scalar(self.coord.ST_Y())
    
    @lat.expression
    def lat(cls):
        return cls.coord.ST_Y()

    @hybrid_property
    def lng(self):
        """Get longitude of the location

        Returns:
            float : The longitude
        """
        return db.session.scalar(self.coord.ST_X())
    
    @lng.expression
    def lng(cls):
        return cls.coord.ST_X()
    
    @hybrid_property
    def count_orders(self):
        """Get count of orders on the location

        Returns:
            int : The order count
        """
        return len(self.orders)
    
    @count_orders.expression
    def count_orders(cls):
        from godisbilen.order import Order
        return select([func.count(Order.id)]).where(Order.location_id == cls.id).label("count_orders")

    @property
    def formatted_address(self):
        """Get a formatted address of the location

        Returns:
            str : The formatted address
        """
        gmaps = googlemaps.Client(key=current_app.config["GOOGLE_MAPS_API_KEY"])
        data = gmaps.reverse_geocode((self.lat, self.lng))[0]
        try:
            return data["formatted_address"]
        except:
            return None

    @property
    def street_name(self):
        """Get the streetname of the location

        Returns:
            str : The streetname
        """
        gmaps = googlemaps.Client(key=current_app.config["GOOGLE_MAPS_API_KEY"])
        data = gmaps.reverse_geocode((self.lat, self.lng))[0]
        for x in data["address_components"]:
            if("route" in x["types"]):
                return x["long_name"]
        return None
    
    @property
    def street_number(self):
        """Get the streetnumber of the location

        Returns:
            str : The streetnumber
        """
        gmaps = googlemaps.Client(key=current_app.config["GOOGLE_MAPS_API_KEY"])
        data = gmaps.reverse_geocode((self.lat, self.lng))[0]
        for x in data["address_components"]:
            if("street_number" in x["types"]):
                return x["long_name"]
        return None
    
    @property
    def postal_town(self):
        """Get the postal_town of the location

        Returns:
            str : The postal_town
        """
        gmaps = googlemaps.Client(key=current_app.config["GOOGLE_MAPS_API_KEY"])
        data = gmaps.reverse_geocode((self.lat, self.lng))[0]
        for x in data["address_components"]:
            if("postal_town" in x["types"]):
                return x["long_name"]
        return None

    def time_between(self, destination):
        """Get the time between the location and another one

        Returns:
            int : The time between in seconds
        """
        gmaps = googlemaps.Client(key=current_app.config["GOOGLE_MAPS_API_KEY"])
        if(isinstance(destination, list)):
            data = gmaps.distance_matrix((self.lat, self.lng), (destination[0], destination[1]), mode="driving")
        else:
            data = gmaps.distance_matrix((self.lat, self.lng), (destination.lat, destination.lng), mode="driving")
        if(data["status"] == "OK"):
            return data["rows"][0]["elements"][0]["duration"]["value"]
        return 600

    def __repr__(self):
        return self.formatted_address