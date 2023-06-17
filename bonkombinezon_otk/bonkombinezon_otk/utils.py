class CustomStr:
    def __str__(self):
        if hasattr(self, 'title'):
            return self.title
        elif hasattr(self, 'name'):
            return self.name
        elif hasattr(self, 'employee') and hasattr(self, 'product'):
            return f'{self.employee} {self.product}'
        else:
            return self.id


def safe_get(Model, **kwargs):
    try:
        return Model.objects.get(**kwargs)
    except Model.MultipleObjectsReturned:
        return Model.objects.filter(**kwargs).last()
    except Model.DoesNotExist:
        return None