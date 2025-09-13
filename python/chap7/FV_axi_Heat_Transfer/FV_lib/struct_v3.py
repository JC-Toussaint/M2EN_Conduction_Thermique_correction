import re

class Struct:
    def __init__(self, *args, recursive=False, validate_names=False, **kwargs):
        self._reserved = set(dir(self))
        self._validate_names = validate_names

        # Initialisation avec dictionnaires positionnels
        for arg in args:
            if not isinstance(arg, dict):
                raise TypeError(f"Argument positionnel invalide : {arg} (type {type(arg)})")
            self._set_attrs(arg, recursive)

        # Initialisation avec kwargs
        self._set_attrs(kwargs, recursive)

    def _is_valid_name(self, key):
        return re.fullmatch(r'[a-zA-Z_]\w*', key) is not None

    def _set_attrs(self, d, recursive):
        for key, value in d.items():
            if self._validate_names and not self._is_valid_name(key):
                raise ValueError(f"Nom d'attribut invalide : '{key}'")
            if key in self._reserved:
                raise AttributeError(f"Le nom '{key}' est réservé et ne peut pas être utilisé comme attribut.")
            if recursive and isinstance(value, dict):
                setattr(self, key, Struct(value, recursive=True, validate_names=self._validate_names))
            else:
                setattr(self, key, value)

    def update(self, *args, recursive=False, **kwargs):
        for arg in args:
            if not isinstance(arg, dict):
                raise TypeError(f"Argument positionnel invalide : {arg} (type {type(arg)})")
            self._set_attrs(arg, recursive)
        self._set_attrs(kwargs, recursive)
        return self

    def to_dict(self):
        result = {}
        for key, value in vars(self).items():
            if isinstance(value, Struct):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

    def keys(self):
        return vars(self).keys()

    def values(self):
        return vars(self).values()

    def items(self):
        return vars(self).items()

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __delitem__(self, key):
        delattr(self, key)

    def __contains__(self, key):
        return hasattr(self, key)

    def __len__(self):
        return len(vars(self))

    def __iter__(self):
        return iter(vars(self))

    def __repr__(self):
        attributes = vars(self)
        repr_str = ', '.join(f"{key}={value!r}" for key, value in attributes.items())
        return f"{self.__class__.__name__}({repr_str})"

    def __dir__(self):
        return list(self.__dict__.keys()) + list(super().__dir__())


if __name__ == "__main__":
    print("=== Exemple simple ===")
    s = Struct(x=1, y=2)
    print(s)             # Struct(x=1, y=2)
    print(s['x'])        # 1
    s['z'] = 3
    print('z' in s)      # True
    print(s.z)
    print(len(s))

    print("\n=== Suppression et mise à jour ===")
    del s['y']
    print(s)             # Struct(x=1, z=3)
    s.update({'a': 10}, b=20)
    print(list(s.keys()))  # ['x', 'z', 'a', 'b']

    print("\n=== Struct imbriqué ===")
    nested = Struct(user={'name': 'Alice', 'age': 30}, recursive=True)
    print(nested)
    print(nested.user.name)

    print("\n=== Conversion dict ===")
    print(nested.to_dict())  # {'user': {'name': 'Alice', 'age': 30}}

    print("\n=== Noms invalides (validation activée) ===")
    try:
        Struct({'1invalid': 42}, validate_names=True)
    except ValueError as e:
        print("Erreur attendue :", e)
