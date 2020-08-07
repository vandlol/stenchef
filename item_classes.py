from mongo_thingy import connect, Thingy
connect("mongodb://localhost/lego")


class Containers(Thingy):
    pass


class Templates(Thingy):
    pass


class Categories(Thingy):
    pass


class Codes(Thingy):
    pass


class Colors(Thingy):
    pass


class Itemtypes(Thingy):
    pass


class Catalog(Thingy):
    pass


class Itemidentifier(Thingy):
    pass
