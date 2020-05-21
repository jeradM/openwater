from .endpoints import init_endpoints


async def setup_plugin(oi):
    init_endpoints(oi)
