from typing import List, Union


class Line(object):
    def __init__(
        self,
        category: str,
        service_name: str = None,
        base_url: str = None,
        profile_url: str = None,
    ):
        self.category = category

        self.service_name = service_name
        self.base_url = base_url
        self.profile_url = profile_url

    def profile_link(self, name):
        return self.profile_url + str(name)

    def category_multiple(self):
        return self.category + "s"

    def make_line(self):
        raise NotImplementedError


def block(items: List[Line]):
    return f"__{items[0].category_multiple()}__\n" + "\n".join(
        [item.make_line() for item in items]
    )


def content(items: List[Union[Line, List[Line]]], user=None):
    res = ""

    for item in items:
        if hasattr(item, "make_block"):
            res += item.make_block()
        else:
            res += block(item)

        res += "\n\n"

    target = items[0]

    if isinstance(target, list):
        target = target[0]

    res += f"({target.service_name})[{target.profile_link(user)}]"

    return res
