import elastica as ea


class Simulator(
    ea.BaseSystemCollection,
    ea.Constraints,
    ea.Forcing,
    ea.Damping,
    ea.CallBacks,
    ea.Contact,
):
    pass
