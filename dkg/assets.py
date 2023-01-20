from dkg.module import Module


class ContentAsset:
    @classmethod
    def create(cls):
        return cls()


class Assets(Module):
    ContentAsset: ContentAsset
