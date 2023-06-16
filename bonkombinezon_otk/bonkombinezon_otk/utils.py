class CustomStr:
    def __str__(self):
        if hasattr(self, 'title'):
            return self.title
        elif hasattr(self, 'name'):
            return self.name
        else:
            return self


def safe_get(Model, **kwargs):
    try:
        return Model.objects.get(**kwargs)
    except Model.MultipleObjectsReturned:
        return Model.objects.filter(**kwargs).last()
    except Model.DoesNotExist:
        return None