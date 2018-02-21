from random import choices, randrange


def get_random_items(model):
    items = model.objects.all()
    return choices(items, k=randrange(len(items)))
