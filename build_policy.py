from build_policies import default


class BuildPolicy:
    def __init__(self, policy=default):
        self.policy = policy

    async def update(self):
        # for small changes.. though... not sure how useful this will be...
        pass

    async def set_new(self):
        # probably what we would use the most.
        pass
